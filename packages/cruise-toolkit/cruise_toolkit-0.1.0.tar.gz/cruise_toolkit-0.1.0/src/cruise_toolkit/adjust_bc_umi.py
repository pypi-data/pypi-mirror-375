#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""
adjust_bc_umi.py  (edlib version)

Aggregate CR+UR -> CB+UMI mappings from multiple alignment summaries (aln_CR_UR.txt),
select the best mapping per query by support count and edit distance thresholds,
and write a consolidated mapping table.

Mapping TSV format (from cr_ur_align.py -> aln_CR_UR.txt):
  query_combined \t ref_combined \t support \t ed

Selection per query:
  - require support >= --umi_support_min
  - require ed <= --ed_max   (edlib global alignment)
  - break ties by: support desc, ed asc, ref lex asc
"""

import argparse, sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Tuple, List, Iterable, Optional

from common_utils import log, log_run, ensure_dir

# --- edlib (C-accelerated) ---
try:
    import edlib  # pip install edlib
except ImportError:
    log("Missing dependency 'edlib'. Please install: pip install edlib", level="ERROR")
    raise

# ---------------------------- CLI ---------------------------- #

def parse_args():
    p = argparse.ArgumentParser(description="Consolidate CR/UR->CB/UMI mapping with edlib distance.")
    p.add_argument("--files", required=True,
                   help="Comma-separated aln_CR_UR.txt files (from cr_ur_align.py).")
    p.add_argument("--ed_max", type=int, default=4, help="Max edit distance to accept (combined).")
    p.add_argument("--umi_support_min", type=int, default=5, help="Min support to accept.")
    p.add_argument("--workers", type=int, default=1,
                   help="Parallel workers across queries (use >1 for speed).")
    p.add_argument("--map_tsv", required=True, help="Output mapping TSV.")
    p.add_argument("--debug_tsv", default=None, help="Optional: write all candidates TSV.")
    p.add_argument("--tmpdir", default="tmp", help="(Reserved) temporary dir.")
    return p.parse_args()

# ----------------------- Edit distance ----------------------- #

def ed_distance(a: str, b: str) -> int:
    """Global edit distance by edlib (Needleman–Wunsch, task='distance')."""
    # edlib default mode is global (NW); task='distance' returns only distance
    return edlib.align(a, b, task="distance")["editDistance"]

# -------------------------- IO ------------------------------ #

def read_pairs(files: List[Path]) -> Dict[str, Counter]:
    """
    Read mapping pairs from multiple aln_CR_UR.txt files.
    Return dict: query -> Counter({ref: support_count})
    """
    agg: Dict[str, Counter] = defaultdict(Counter)
    for fp in files:
        log_run(["read", str(fp)])
        with open(fp, "r") as fh:
            for ln in fh:
                if not ln.strip():
                    continue
                # expected columns: qname, rname, cigar, seq, tag14, tag15, tag16
                parts = ln.rstrip("\n").split("\t")
                if len(parts) < 2:
                    continue
                q = parts[0]
                r = parts[1]
                agg[q][r] += 1
    return agg

# --------------------- Candidate ranking --------------------- #

def _best_for_query(
    payload: Tuple[str, Dict[str, int], int, int, bool]
) -> Tuple[Optional[Tuple[str, str, int, int]], Optional[List[Tuple[str, str, int, int]]]]:
    """
    Worker-safe function to compute best mapping for a single query.

    Args payload:
      q: query string
      cand_map: dict ref -> support
      ed_max: int
      support_min: int
      want_debug: bool

    Returns:
      (best or None, all_rows or None)
      where best = (q, ref, support, ed)
            all_rows = [(q, ref, support, ed), ...]  (only if want_debug)
    """
    q, cand_map, ed_max, support_min, want_debug = payload
    qlen = len(q)

    best: Optional[Tuple[str, str, int, int]] = None
    all_rows: Optional[List[Tuple[str, str, int, int]]] = [] if want_debug else None

    # If not collecting debug, only evaluate refs that meet support_min
    items = cand_map.items() if want_debug else ((r, c) for r, c in cand_map.items() if c >= support_min)

    for r, c in items:
        # Quick length-pruning lower bound: Levenshtein >= |len(a)-len(b)|
        if abs(qlen - len(r)) > ed_max:
            if want_debug:
                # still record as an inf-distance-like large value? We can write ed as ed_max+1 to denote skip
                all_rows.append((q, r, c, ed_max + 1))
            continue

        ed = ed_distance(q, r)

        if want_debug:
            all_rows.append((q, r, c, ed))

        if c < support_min or ed > ed_max:
            continue

        if best is None:
            best = (q, r, c, ed)
        else:
            # choose by support desc, ed asc, ref lex asc
            _, r0, c0, ed0 = best[0], best[1], best[2], best[3]
            if (c > c0) or (c == c0 and (ed < ed0 or (ed == ed0 and r < r0))):
                best = (q, r, c, ed)

    return best, all_rows

def select_best_parallel(
    agg: Dict[str, Counter], ed_max: int, support_min: int, workers: int, want_debug: bool
) -> Tuple[List[Tuple[str,str,int,int]], List[Tuple[str,str,int,int]]]:
    """
    Parallel (or single-thread) selection across queries.
    Returns:
      accepted list and (optional) all_rows (empty if not requested).
    """
    tasks: List[Tuple[str, Dict[str, int], int, int, bool]] = [
        (q, dict(ctr), ed_max, support_min, want_debug) for q, ctr in agg.items()
    ]

    accepted: List[Tuple[str,str,int,int]] = []
    all_rows: List[Tuple[str,str,int,int]] = []

    if workers <= 1:
        for t in tasks:
            best, rows = _best_for_query(t)
            if best is not None:
                accepted.append(best)
            if rows:
                all_rows.extend(rows)
        return accepted, all_rows

    # Multiprocessing (process pool)
    from concurrent.futures import ProcessPoolExecutor, as_completed
    # On some platforms edlib may be faster with fewer workers; let user decide
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_best_for_query, t) for t in tasks]
        for fut in as_completed(futs):
            best, rows = fut.result()
            if best is not None:
                accepted.append(best)
            if rows:
                all_rows.extend(rows)

    return accepted, all_rows

# --------------------------- Main ---------------------------- #

def main():
    a = parse_args()
    files = [Path(x) for x in a.files.split(",") if x.strip()]
    if not files:
        log("No input files.", level="ERROR"); sys.exit(1)
    for f in files:
        if not f.exists():
            log(f"Missing file: {f}", level="ERROR"); sys.exit(2)

    ensure_dir(Path(a.map_tsv).parent)
    if a.debug_tsv:
        ensure_dir(Path(a.debug_tsv).parent)
    ensure_dir(a.tmpdir)

    print("=== Parameters ===")
    print(f"Files               : {len(files)}")
    print(f"ed_max              : {a.ed_max}")
    print(f"umi_support_min     : {a.umi_support_min}")
    print(f"Workers             : {a.workers}")
    print(f"map_tsv             : {a.map_tsv}")
    print(f"debug_tsv           : {a.debug_tsv or '(none)'}")
    print("==================\n")

    agg = read_pairs(files)

    kept, all_rows = select_best_parallel(
        agg, a.ed_max, a.umi_support_min, max(1, a.workers), bool(a.debug_tsv)
    )

    # write outputs
    with open(a.map_tsv, "w") as out:
        for q, r, c, ed in kept:
            out.write(f"{q}\t{r}\t{c}\t{ed}\n")

    if a.debug_tsv:
        with open(a.debug_tsv, "w") as dbg:
            for q, r, c, ed in all_rows:
                dbg.write(f"{q}\t{r}\t{c}\t{ed}\n")

    log(f"Accepted mappings: {len(kept):,} / queries: {len(agg):,}")
    print("\n✅ DONE. Outputs:")
    print(f"  - {a.map_tsv}")
    if a.debug_tsv:
        print(f"  - {a.debug_tsv}")

if __name__ == "__main__":
    main()
