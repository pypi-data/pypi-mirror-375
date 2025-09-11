#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""
add_cb_ub.py

Read input FASTQ whose headers contain CR:Z:... and UR:Z:... (A/C/G/T/N),
use an adjust mapping (query_combined=CR+UR -> ref_combined=CB+UMI),
and emit a filtered FASTQ whose header keeps original content but
appends tags joined by '|||' at the end:

    ...|||CB:Z:<cb>|||UB:Z:<ub>[|||DB:Z:<db>|||NB:Z:<sample>_<db>]

Rules for DB/NB:
- DB is looked up from --validcell (a two-column file: CB<TAB>DB) using mapped CB.
- NB is written only if both --validcell and --samplename are provided: NB = <sample>_<DB>.
- If --validcell is missing → DO NOT write DB/NB (even if --samplename is given).

Notes
- Only the connector for appended tags is '|||'.
- Existing CB/UB/DB/NB (joined by spaces or '|||') are removed first to avoid duplicates.
- Reads without CR/UR or without a mapping entry are dropped.
"""

import argparse
import sys
import gzip
import re
from pathlib import Path
from typing import Dict, Optional
from common_utils import log, ensure_dir

# --- regex patterns ---
CR_RE = re.compile(r"CR:Z:([ACGTN]+)")
UR_RE = re.compile(r"UR:Z:([ACGTN]+)")
# remove existing tags (space or '|||' joined)
TAG_CLEAN_RE = re.compile(r'(?:\s+|\|\|\|)+(?:CB|UB|DB|NB):Z:[A-Za-z0-9_]+')

def parse_args():
    p = argparse.ArgumentParser(description="Attach CB/UB/DB/NB tags to FASTQ using adjust mapping.")
    p.add_argument("--fastq", required=True, help="Input FASTQ (.fq/.fastq[.gz]) with CR/UR tags in header.")
    p.add_argument("--out", required=True, help="Output FASTQ (.fq/.fastq[.gz]).")
    p.add_argument("--map-tsv", required=True, help="adjust.tsv produced by adjust_bc_umi.py (CR+UR -> CB+UB)")
    p.add_argument("--validcell", default=None,
                   help="Optional two-column file: CB<TAB>DB. If provided, keep reads with CB in file and write DB; "
                        "with --samplename also write NB=<sample>_<DB>.")
    p.add_argument("--workers", type=int, default=1, help="Reserved; current impl is single-threaded.")
    p.add_argument("--cb-len", type=int, default=None, help="Optional: expected CB length (for validation only).")
    p.add_argument("--umi-len", type=int, default=None, help="Optional: expected UMI length (for validation only).")
    p.add_argument("--reads-per-block", type=int, default=1_000_000, help="Streaming block size.")
    p.add_argument("--log-interval", type=int, default=500_000, help="Print progress every N reads.")
    p.add_argument("--samplename", default=None,
                   help="Optional sample label. With --validcell, NB= <samplename>_<DB>.")
    return p.parse_args()

def open_maybe_gz(path: Path, mode: str):
    if str(path).endswith(".gz"):
        return gzip.open(path, mode + "t", encoding="utf-8", newline="")
    return open(path, mode, encoding="utf-8", newline="")

def load_map_tsv(path: Path) -> Dict[str, str]:
    """Load CR+UR -> CB+UB mapping from TSV."""
    mp: Dict[str, str] = {}
    with open(path, "r") as fh:
        for ln in fh:
            if not ln.strip():
                continue
            parts = ln.rstrip("\n").split("\t")
            if len(parts) < 2:
                continue
            q = parts[0]; r = parts[1]
            mp[q] = r
    return mp

def load_valid_map(path: Optional[Path]) -> Optional[Dict[str, str]]:
    """
    Load CB->DB mapping from a two-column file (CB<TAB>DB).
    Lines with fewer than 2 columns are skipped.
    """
    if not path:
        return None
    m: Dict[str, str] = {}
    with open(path, "r") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            cols = ln.split()
            if len(cols) < 2:
                continue
            cb, db = cols[0].upper(), cols[1]
            m[cb] = db
    return m

def extract_cr_ur(header: str):
    m1 = CR_RE.search(header)
    m2 = UR_RE.search(header)
    if not (m1 and m2):
        return None
    return m1.group(1), m2.group(1)

def inject_tags(header: str, cb: str, ub: str,
                db: Optional[str], nb: Optional[str]) -> str:
    """
    Minimal-change header edit:
      1) Keep original header content;
      2) Remove any existing CB/UB/DB/NB (space or '|||' joined);
      3) Append '|||CB:Z:<cb>|||UB:Z:<ub>[|||DB:Z:<db>][|||NB:Z:<nb>]'.
    """
    h = header.rstrip("\r\n")
    h = TAG_CLEAN_RE.sub("", h).rstrip()  # remove existing tags
    parts = [f"CB:Z:{cb}", f"UB:Z:{ub}"]
    if db is not None:
        parts.append(f"DB:Z:{db}")
    if nb is not None:
        parts.append(f"NB:Z:{nb}")
    return h + "|||" + "|||".join(parts) + "\n"

def main():
    a = parse_args()
    in_fq  = Path(a.fastq)
    out_fq = Path(a.out)
    map_tsv = Path(a.map_tsv)
    valid_path = Path(a.validcell) if a.validcell else None

    ensure_dir(out_fq.parent)
    mp = load_map_tsv(map_tsv)                # CR+UR -> CB+UB
    cb2db = load_valid_map(valid_path)        # CB -> DB (two columns) or None

    # DB/NB emission rule
    write_db = cb2db is not None
    write_nb = write_db and (a.samplename not in (None, ""))

    print("=== Parameters ===")
    print(f"Input FASTQ         : {in_fq}")
    print(f"Output FASTQ        : {out_fq}")
    print(f"Mapping TSV         : {map_tsv}  (entries: {len(mp):,})")
    print(f"Validcell (CB->DB)  : {valid_path or '(none)'}")
    print(f"Write DB            : {'YES' if write_db else 'NO'}")
    print(f"Write NB            : {'YES' if write_nb else 'NO'}")
    print(f"CB/UMI length hint  : {a.cb_len or '-'} / {a.umi_len or '-'}")
    print(f"Sample name         : {a.samplename or '(none)'}")
    print("==================\n")

    total=0; kept=0; skipped_nomap=0; skipped_invalid=0; len_mismatch=0

    with open_maybe_gz(in_fq, "r") as r, open_maybe_gz(out_fq, "w") as w:
        while True:
            h = r.readline()
            if not h:
                break
            s = r.readline(); p = r.readline(); q = r.readline()
            if not q:
                break

            total += 1
            if (total % a.log_interval) == 0:
                log(f"progress reads={total:,}, kept={kept:,}, no_map={skipped_nomap:,}, invalid={skipped_invalid:,}")

            cr_ur = extract_cr_ur(h)
            if not cr_ur:
                skipped_nomap += 1
                continue
            cr, ur = cr_ur
            key_q = cr + ur
            if key_q not in mp:
                skipped_nomap += 1
                continue

            key_r = mp[key_q]
            # split mapped combined using current record's CR/UR lengths
            cb = key_r[:len(cr)]
            ub = key_r[len(cr):]

            # optional length validation (record only)
            if a.cb_len and len(cb) != a.cb_len:
                len_mismatch += 1
            if a.umi_len and len(ub) != a.umi_len:
                len_mismatch += 1

            db = None
            nb = None
            if write_db:
                # lookup DB by CB in validcell map; filter out if not present
                db = cb2db.get(cb.upper()) if cb2db else None
                if db is None:
                    skipped_invalid += 1
                    continue
                if write_nb:
                    nb = f"{a.samplename}_{db}"

            # append tags using '|||'
            h2 = inject_tags(h, cb, ub, db, nb)
            w.write(h2); w.write(s); w.write(p); w.write(q)
            kept += 1

    log(f"Finished: total={total:,}, kept={kept:,}, no_map={skipped_nomap:,}, invalid={skipped_invalid:,}, len_mismatch={len_mismatch:,}")
    print("\n✅ DONE. Output:")
    print(f"  - {out_fq}")

if __name__ == "__main__":
    main()
