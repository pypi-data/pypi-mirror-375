#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRUISE / 码舟 — cruise.py
(resume-enabled + sample-level parallel + optional cleanup + full QC aggregation)

流程（与原版一致）：
  0) cbumi_counter.py -> 00.ref/short.fasta
  1) [并行 每样本] barcode_split.py -> tmp_<SID>/01.barcode/model.retain.mask.drc.merge.fq
                     cr_ur_align.py   -> tmp_<SID>/02.align_cb/aln_CR_UR.txt
  2) adjust_bc_umi.py (跨样本)        -> 01.adjust/adjust.tsv
  3) [并行 每样本] add_cb_ub.py       -> tmp_<SID>/03.filterBam/mask.adjust.valid.fq
  4) 合并 -> 01.adjust/merge.mask.adjust.valid.fq
  5) QC 汇总（每样本）：raw / ≥min_len / q10 / model / adjust
  6) 可选清理：--no-keep-sample-tmp 删除所有 tmp_*，仅保留 00.ref 与 01.adjust
"""

from __future__ import annotations
import argparse, glob, os, sys, shutil, gzip
from pathlib import Path
from typing import List, Iterable, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from common_utils import log, log_run, ensure_dir, run_cmd, run_cmd_capture

HERE   = Path(__file__).resolve().parent
CBUMI  = HERE / "cbumi_counter.py"
SPLIT  = HERE / "barcode_split.py"
ALIGN  = HERE / "cr_ur_align.py"
ADJUST = HERE / "adjust_bc_umi.py"
ADDCB  = HERE / "add_cb_ub.py"

# --------------------- CLI ---------------------
def parse_args():
    p = argparse.ArgumentParser(description="CRUISE / Batch FASTQ pipeline orchestrator (resume-enabled).")
    # Inputs & discovery
    p.add_argument("--bam", required=True, help="Coordinate-sorted BAM (indexed).")
    p.add_argument("--fastqs", nargs="*", default=None,
                   help="Explicit FASTQ list. Space-separated; items may contain commas（内部会拆分为单文件样本）.")
    p.add_argument("--outdir", default=".", help="Project root.")
    p.add_argument("--valid-cell", default=None, help="Valid CB whitelist (one per line).")
    # Core model
    p.add_argument("--adapt", required=True, help="Adapter sequence (A/C/G/T).")
    p.add_argument("--model", required=True, help="Model sequence (A/C/G/T/B/U; B=CR, U=UR).")
    # Global compute
    p.add_argument("--threads", type=int, default=16, help="General threads (传给子工具).")
    p.add_argument("--force", action="store_true", help="Force rerun all steps (ignore resume).")
    p.add_argument("--skip-qc", action="store_true", help="Skip final QC table.")
    # cbumi_counter params
    p.add_argument("--cb-tags", default="CC,CB")
    p.add_argument("--umi-tag", default="UB")
    p.add_argument("--cbumi-min-mapq", type=int, default=20)
    p.add_argument("--bam-threads", type=int, default=2)
    p.add_argument("--cbumi-chunk-size", type=int, default=20_000_000)
    p.add_argument("--cbumi-max-chunks", type=int, default=200_000)
    p.add_argument("--cbumi-cb-whitelist", default=None)
    p.add_argument("--cbumi-min-count", type=int, default=1)
    p.add_argument("--cbumi-no-fasta", action="store_true")
    # barcode_split params
    p.add_argument("--split-min-len", type=int, default=200)
    p.add_argument("--split-q", type=int, default=10)
    p.add_argument("--split-u", type=int, default=40)
    p.add_argument("--split-revcomp", dest="split_revcomp", action="store_true", default=True)
    p.add_argument("--split-no-revcomp", dest="split_revcomp", action="store_false")
    p.add_argument("--split-keep-temp", action="store_false", default=False)
    # cr_ur_align params
    p.add_argument("--align-bwa-args", default="-k13 -W5 -r8 -A1 -B1 -O1 -E1 -L0 -T24")
    p.add_argument("--align-force", action="store_true")
    # adjust_bc_umi params
    p.add_argument("--adjust-ed-max", type=int, default=4)
    p.add_argument("--adjust-umi-support-min", type=int, default=1)
    p.add_argument("--adjust-workers", type=int, default=64)
    p.add_argument("--adjust-tmpdir", default="tmp")
    p.add_argument("--adjust-debug-tsv", default=None)
    # add_cb_ub params
    p.add_argument("--add-workers", type=int, default=1)
    p.add_argument("--add-cb-len", type=int, default=20)
    p.add_argument("--add-umi-len", type=int, default=10)
    p.add_argument("--add-reads-per-block", type=int, default=1_500_000)
    p.add_argument("--add-log-interval", type=int, default=500_000)
    p.add_argument("--samplename", default=None, help="Optional sample label; passed to add_cb_ub.")
    # NEW: cleanup switch
    p.add_argument("--keep-sample-tmp", dest="keep_sample_tmp", action="store_true", default=True,
                   help="Keep per-sample tmp_<SID> directories (default: True).")
    p.add_argument("--no-keep-sample-tmp", dest="keep_sample_tmp", action="store_false",
                   help="Delete all tmp_* at the end; keep only 00.ref and 01.adjust.")
    return p.parse_args()

# --------------------- Helpers ---------------------
def _expand_fastqs(tokens: Iterable[str]) -> List[str]:
    out=[]
    for t in tokens:
        out.extend([x.strip() for x in str(t).split(",") if x.strip()])
    return out


def discover_fastqs(fq_dir: str) -> List[str]:
    files=[]
    for pat in ["*.fq", "*.fastq", "*.fq.gz", "*.fastq.gz"]:
        files += glob.glob(str(Path(fq_dir)/pat))
    return sorted(files)


def sid_from_path(p: str) -> str:
    b=Path(p).name
    for suf in (".gz",".fastq",".fq"):
        if b.endswith(suf): b=b[:-len(suf)]
    return b

def mtime(path: Path) -> float:
    try: return path.stat().st_mtime
    except FileNotFoundError: return 0.0

def exists_nonempty(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0

def need_rebuild(output: Path, inputs: Iterable[Path], force: bool=False) -> bool:
    if force or (not exists_nonempty(output)): return True
    out_m = mtime(output)
    return any(mtime(ip) > out_m for ip in inputs)

def seqkit_available() -> bool:
    return shutil.which("seqkit") is not None

def seqkit_stat_text(path: Path) -> str:
    if not seqkit_available(): return ""
    return run_cmd_capture(["seqkit", "stat", str(path), "--all"])

# ---------- Counting utilities ----------
def _seqkit_count_reads(path: Path) -> Optional[int]:
    if not seqkit_available(): return None
    try:
        txt = run_cmd_capture(["seqkit", "stats", "-T", str(path)])
        lines = [ln for ln in txt.splitlines() if ln.strip()]
        if len(lines) < 2: return None
        header = lines[0].split("\t")
        row    = lines[-1].split("\t")
        idx = header.index("num_seqs")
        return int(row[idx].replace(",", ""))
    except Exception:
        return None

def _count_fastq_lines(path: Path) -> int:
    n = 0
    if str(path).endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8", errors="ignore") as f:
            for _ in f: n += 1
    else:
        with open(path, "rt", encoding="utf-8", errors="ignore") as f:
            for _ in f: n += 1
    return n // 4

def count_reads(path: Optional[Path]) -> int:
    if not path or not path.exists(): return 0
    v = _seqkit_count_reads(path)
    return v if v is not None else _count_fastq_lines(path)

def find_first_existing(base: Path, names: List[str]) -> Optional[Path]:
    for nm in names:
        p = base / nm
        if p.exists() and p.stat().st_size > 0:
            return p
    return None

# ---------- Parse barcode_split QC (tail lines) ----------
def parse_barcode_qc(qc_path: Path, input_fq: Path) -> Dict[str, int]:
    """
    解析 tmp_<SID>/01.barcode/qc.standard.reads.txt（每行为 seqkit stat 的 tail 行）.
    返回：
      {'raw': x, 'len_ge': y, 'q10': z, 'model': m, 'model_retain': r?}
    未出现的键返回 0；后续会以文件读取作为补充。
    """
    keys = {"raw":0, "len_ge":0, "q10":0, "model":0, "model_retain":0}
    if not qc_path.exists():
        return keys

    in_name = input_fq.name
    try:
        with open(qc_path, "r") as f:
            for ln in f:
                ln = ln.strip()
                if not ln: continue
                cols = ln.split()
                if len(cols) < 4: continue
                fcol = cols[0]
                try:
                    nseq = int(cols[3].replace(",", ""))
                except Exception:
                    continue
                # 匹配规则（尽量稳健）
                if "model.retain.mask.drc.merge.fq" in fcol:
                    keys["model"] = nseq
                elif "model.retain.drc.fq" in fcol:
                    keys["model_retain"] = nseq
                elif ("q10" in fcol) and (".fq" in fcol or ".fastq" in fcol):
                    keys["q10"] = nseq
                elif (("200" in fcol) and (".fq" in fcol or ".fastq" in fcol)
                      and ("q10" not in fcol)):
                    keys["len_ge"] = nseq
                elif fcol.endswith(in_name) or (in_name in fcol):
                    keys["raw"] = nseq
                else:
                    # 若第一行即 raw（容错）：当 raw 仍未赋值，且当前为第一条，兜底为 raw
                    if keys["raw"] == 0 and keys["len_ge"] == 0 and keys["q10"] == 0 and keys["model"] == 0:
                        keys["raw"] = nseq
    except Exception:
        return keys
    return keys

# --------------------- Per-sample workers ---------------------
def run_split_align_for_sample(args_pack) -> Tuple[str, str]:
    """返回 (sid, aln_txt_path)；异常抛出以便主线程停止。"""
    a, fq, sid, ref_fa, root = args_pack
    w_tmp = root/f"tmp_{sid}"
    w_bar = w_tmp/"01.barcode"
    w_aln = w_tmp/"02.align_cb"
    ensure_dir(w_bar, w_aln)

    merged_fq = w_bar/"model.retain.mask.drc.merge.fq"

    # barcode_split.py
    if need_rebuild(merged_fq, [Path(fq)], a.force):
        log(f"[{sid}] RUN: barcode_split.py")
        split_cmd = [
            sys.executable, str(SPLIT),
            "-i", fq,
            "--adapt", a.adapt,
            "--model", a.model,
            "--workdir", str(w_bar),
            "-j", str(a.threads),
            "--min_len", str(a.split_min_len),
            "--q", str(a.split_q),
            "--u", str(a.split_u)
        ]
        split_cmd += ["--revcomp"] if a.split_revcomp else ["--no-revcomp"]
        split_cmd += ["--keep-temp"] if a.split_keep_temp else []
        run_cmd(split_cmd)
    else:
        log(f"[{sid}] SKIP (resume): barcode_split output is up-to-date")

    if not merged_fq.exists():
        raise RuntimeError(f"Missing {merged_fq}")

    # cr_ur_align.py
    aln_txt = w_aln/"aln_CR_UR.txt"
    if need_rebuild(aln_txt, [merged_fq, ref_fa], (a.align_force or a.force)):
        log(f"[{sid}] RUN: cr_ur_align.py")
        align_cmd = [
            sys.executable, str(ALIGN),
            "-i", str(merged_fq),
            "-r", str(ref_fa),
            "-o", str(w_aln),
            "-t", str(a.threads),
            "--bwa-args", a.align_bwa_args
        ]
        if a.align_force or a.force:
            align_cmd += ["--force"]
        run_cmd(align_cmd)
    else:
        log(f"[{sid}] SKIP (resume): align output is up-to-date")

    if not aln_txt.exists():
        raise RuntimeError(f"Missing {aln_txt}")
    return sid, str(aln_txt)

def run_add_for_sample(args_pack) -> Tuple[str, str]:
    """返回 (sid, out_fq_path)；异常抛出以便主线程停止。"""
    a, fq, sid, map_tsv, root = args_pack
    w_tmp = root/f"tmp_{sid}"
    w_bar = w_tmp/"01.barcode"
    w_fil = w_tmp/"03.filterBam"
    ensure_dir(w_fil)

    merged_fq = w_bar/"model.retain.mask.drc.merge.fq"
    out_fq = w_fil/"mask.adjust.valid.fq"

    deps = [merged_fq, map_tsv]
    if a.valid_cell is not None:
        deps.append(Path(a.valid_cell))

    if need_rebuild(out_fq, deps, a.force):
        log(f"[{sid}] RUN: add_cb_ub.py")
        add_cmd = [
            sys.executable, str(ADDCB),
            "--fastq", str(merged_fq),
            "--out",   str(out_fq),
            "--map-tsv", str(map_tsv),
            "--workers", str(a.add_workers),
            "--reads-per-block", str(a.add_reads_per_block),
            "--log-interval", str(a.add_log_interval)
        ]
        if a.add_cb_len is not None:  add_cmd += ["--cb-len",  str(a.add_cb_len)]
        if a.add_umi_len is not None: add_cmd += ["--umi-len", str(a.add_umi_len)]
        if a.samplename is not None:  add_cmd += ["--samplename", str(a.samplename)]
        if a.valid_cell is not None:  add_cmd += ["--validcell", str(a.valid_cell)]
        run_cmd(add_cmd)
    else:
        log(f"[{sid}] SKIP (resume): add_cb_ub output is up-to-date")

    if not out_fq.exists():
        raise RuntimeError(f"Missing {out_fq}")
    return sid, str(out_fq)

# --------------------- Main pipeline ---------------------
def main():
    a = parse_args()
    root = Path(a.outdir); ensure_dir(root)
    ref_dir    = root / "00.ref"
    adjust_dir = root / "01.adjust"
    ensure_dir(ref_dir, adjust_dir)

    # Collect FASTQs
    if a.fastqs:
        fastqs = _expand_fastqs(a.fastqs)
    else:
        log("Provide --fastqs or --fastq-dir", level="ERROR"); sys.exit(1)
    if not fastqs:
        log("No FASTQ found.", level="ERROR"); sys.exit(1)

    sample_names = [sid_from_path(p) for p in fastqs]

    # 0) Build reference once
    ref_fa = ref_dir / "short.fasta"
    alt_fa = ref_dir / "short.fa"
    ref_inputs = [Path(a.bam)] + ([Path(a.cbumi_cb_whitelist)] if a.cbumi_cb_whitelist else [])
    if need_rebuild(ref_fa if ref_fa.exists() else alt_fa, ref_inputs, a.force):
        log("RUN: cbumi_counter.py")
        cmd = [
            sys.executable, str(CBUMI),
            "-i", a.bam, "-o", str(ref_dir),
            "--min-mapq", str(a.cbumi_min_mapq),
            "--threads",   str(a.threads),
            "--bam-threads", str(a.bam_threads),
            "--cb-tags", a.cb_tags,
            "--umi-tag", a.umi_tag,
            "--chunk-size", str(a.cbumi_chunk_size),
            "--max-chunks", str(a.cbumi_max_chunks),
            "--min-count", str(a.cbumi_min_count),
        ]
        if a.cbumi_cb_whitelist: cmd += ["--cb-whitelist", a.cbumi_cb_whitelist]
        if a.cbumi_no_fasta:     cmd += ["--no-fasta"]
        if a.force:              cmd += ["--force"]
        run_cmd(cmd)
    else:
        log("SKIP (resume): reference up-to-date")

    ref_fa = ref_dir/"short.fasta" if (ref_dir/"short.fasta").exists() else alt_fa
    if not ref_fa.exists():
        log(f"Reference FASTA not found in {ref_dir}", level="ERROR"); sys.exit(2)

    # 1) split + align (parallel)
    MAX_WORKERS = min(len(fastqs), max(1, (os.cpu_count() or 2)//2))
    log(f"Sample-parallel (step1): workers={MAX_WORKERS} (n={len(fastqs)})")

    aln_txts_map: Dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        fut_map = {
            ex.submit(run_split_align_for_sample, (a, fq, sid, ref_fa, Path(a.outdir))): sid
            for fq, sid in zip(fastqs, sample_names)
        }
        for fut in as_completed(fut_map):
            sid = fut_map[fut]
            try:
                sid2, aln_txt_path = fut.result()
                aln_txts_map[sid2] = aln_txt_path
            except Exception as e:
                log(f"[{sid}] ERROR in split+align: {e}", level="ERROR")
                for f2 in fut_map:
                    f2.cancel()
                sys.exit(3)
    aln_txts = [aln_txts_map[sid] for sid in sample_names]

    # 2) adjust across samples
    files_csv = ",".join(aln_txts)
    map_tsv = adjust_dir/"adjust.tsv"
    ensure_dir(adjust_dir, a.adjust_tmpdir)
    if need_rebuild(map_tsv, [Path(p) for p in aln_txts], a.force):
        log(f"RUN: adjust_bc_umi.py across {len(aln_txts)} files")
        adjust_cmd = [
            sys.executable, str(ADJUST),
            "--files", files_csv,
            "--ed_max", str(a.adjust_ed_max),
            "--umi_support_min", str(a.adjust_umi_support_min),
            "--workers", str(a.adjust_workers),
            "--map_tsv", str(map_tsv),
            "--tmpdir", a.adjust_tmpdir
        ]
        if a.adjust_debug_tsv:
            adjust_cmd += ["--debug_tsv", str(adjust_dir/"adjust.debug.tsv")]
        run_cmd(adjust_cmd)
    else:
        log("SKIP (resume): adjust map up-to-date")

    # 3) add_cb_ub (parallel)
    log(f"Sample-parallel (step3): workers={MAX_WORKERS}")
    sample_outfq_map: Dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        fut_map = {
            ex.submit(run_add_for_sample, (a, fq, sid, map_tsv, Path(a.outdir))): sid
            for fq, sid in zip(fastqs, sample_names)
        }
        for fut in as_completed(fut_map):
            sid = fut_map[fut]
            try:
                sid2, out_fq_path = fut.result()
                sample_outfq_map[sid2] = out_fq_path
            except Exception as e:
                log(f"[{sid}] ERROR in add_cb_ub: {e}", level="ERROR")
                for f2 in fut_map:
                    f2.cancel()
                sys.exit(4)
    sample_outfq = [sample_outfq_map[sid] for sid in sample_names]

    # 4) merge final
    merge_fq = adjust_dir/"merge.mask.adjust.valid.fq"
    if need_rebuild(merge_fq, [Path(p) for p in sample_outfq], a.force):
        log("RUN: merge final FASTQs")
        with open(merge_fq,"w") as out:
            for f in sample_outfq:
                with open(f) as fh:
                    for ln in fh:
                        out.write(ln)
    else:
        log("SKIP (resume): merged FASTQ up-to-date")

    # 5) build QC table (full aggregation)
    if not a.skip_qc:
        qc_rows: List[Tuple[str,int,int,int,int,int]] = []
        for fq, sid in zip(fastqs, sample_names):
            w_tmp = root/f"tmp_{sid}"
            w_bar = w_tmp/"01.barcode"
            w_fil = w_tmp/"03.filterBam"

            # 先尝试从 01.barcode/qc.standard.reads.txt 解析
            qc_bar = w_bar/"qc.standard.reads.txt"
            qc_map = parse_barcode_qc(qc_bar, Path(fq))

            # 若缺口，按文件计数兜底
            if qc_map["raw"] == 0:
                qc_map["raw"] = count_reads(Path(fq))
            if qc_map["len_ge"] == 0:
                f_len = find_first_existing(w_bar, ["tmp.200.fq", "filter.200bp.fq"])
                qc_map["len_ge"] = count_reads(f_len) if f_len else 0
            if qc_map["q10"] == 0:
                f_q10 = find_first_existing(w_bar, ["tmp.q10.fq", "filter.200bp.q10.fq"])
                qc_map["q10"] = count_reads(f_q10) if f_q10 else 0
            if qc_map["model"] == 0:
                f_model = w_bar/"model.retain.mask.drc.merge.fq"
                qc_map["model"] = count_reads(f_model) if f_model.exists() else 0

            # adjust（valid）
            f_adj = w_fil/"mask.adjust.valid.fq"
            adj_cnt = count_reads(f_adj) if f_adj.exists() else 0

            qc_rows.append((sid, qc_map["raw"], qc_map["len_ge"], qc_map["q10"], qc_map["model"], adj_cnt))

        qc_path = adjust_dir/"qc.merged.tsv"
        log("WRITE: per-step QC -> " + str(qc_path))
        with open(qc_path, "w") as out:
            out.write(f"Sample\traw\tlen>={a.split_min_len}\tq10\tmodel\tadjust\n")
            for sid, r0, r1, r2, r3, r4 in qc_rows:
                out.write(f"{sid}\t{r0}\t{r1}\t{r2}\t{r3}\t{r4}\n")
            if len(qc_rows) > 1:
                tot = lambda i: sum(row[i] for row in qc_rows)
                out.write("TOTAL\t{}\t{}\t{}\t{}\t{}\n".format(
                    tot(1), tot(2), tot(3), tot(4), tot(5)
                ))

    # 6) optional cleanup
    if not a.keep_sample_tmp:
        removed = 0
        for p in root.glob("tmp_*"):
            if p.is_dir():
                try:
                    shutil.rmtree(p)
                    removed += 1
                except Exception as e:
                    log(f"WARNING: failed to remove {p}: {e}", level="WARN")
        log(f"Cleanup: removed {removed} tmp_* directories. Kept 00.ref and 01.adjust.")

    print("\n✅ ALL DONE")
    print(f"  - Reference FASTA : {ref_fa}")
    print(f"  - Adjust map      : {map_tsv}")
    print(f"  - Merged FASTQ    : {merge_fq}")
    if not a.skip_qc:
        print(f"  - QC merged table : {adjust_dir/'qc.merged.tsv'}")
    if not a.keep_sample_tmp:
        print("  - Cleaned sample tmp_* directories")

if __name__ == "__main__":
    main()
