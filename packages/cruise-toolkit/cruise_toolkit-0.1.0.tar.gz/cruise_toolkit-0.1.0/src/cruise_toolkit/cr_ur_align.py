#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cr_ur_align.py

1) Count (CR,UR) from FASTQ headers → long.tsv  (cols: CR, UR, '', COUNT)
2) Build long.fasta (one entry per CR+UR)
3) Stream `bwa mem`:
   - write full SAM to aln_CR_UR.sam
   - in the same pass, filter FLAG==0 rows and emit fields $1,$3,$6,$10,$14,$15,$16 → aln_CR_UR.txt
"""

import argparse, gzip, io, re, shutil, subprocess, sys
from pathlib import Path
from collections import Counter
from typing import Optional
from common_utils import log, log_run, ensure_dir

CR_RE = re.compile(r"CR:Z:([ACGTN]+)")
UR_RE = re.compile(r"UR:Z:([ACGTN]+)")

def parse_args():
    p = argparse.ArgumentParser(description="CR/UR → TSV/FASTA; BWA-MEM alignment to reference.")
    p.add_argument("-i","--fq", required=True, help="Input FASTQ(.gz) with CR/UR in headers")
    p.add_argument("-r","--ref", default="01.barcode/short.fa", help="Reference FASTA for BWA")
    p.add_argument("-o","--outdir", default="01.barcode", help="Output directory")
    p.add_argument("-t","--threads", type=int, default=32, help="Threads for BWA-MEM")
    p.add_argument("--bwa-args", default="-k13 -W5 -r8 -A1 -B1 -O1 -E1 -L0 -T24", help="Extra args for bwa mem")
    p.add_argument("--force", action="store_true", help="Overwrite outputs if exist")
    return p.parse_args()

def ensure_bwa():
    if shutil.which("bwa") is None:
        log("'bwa' not found in PATH.", level="ERROR"); sys.exit(2)

def need_bwa_index(ref: Path) -> bool:
    return any(not (ref.with_suffix(ref.suffix+ext)).exists() for ext in (".amb",".ann",".bwt",".pac",".sa"))

def open_maybe_gz(path: Path):
    return gzip.open(path,"rt") if str(path).endswith(".gz") else open(path,"r")

def count_cr_ur(fq: Path) -> Counter:
    cnt = Counter(); nrec=0
    with open_maybe_gz(fq) as f:
        while True:
            h=f.readline()
            if not h: break
            _=f.readline(); _=f.readline(); q=f.readline()
            if not q: break
            nrec+=1
            m1=CR_RE.search(h); m2=UR_RE.search(h)
            if m1 and m2: cnt[(m1.group(1), m2.group(1))]+=1
    log(f"Parsed FASTQ headers: {nrec:,} records, pairs found: {sum(cnt.values()):,}")
    return cnt

def write_long_tsv(cnt: Counter, out_tsv: Path):
    with open(out_tsv,"w") as out:
        for (cr,ur),c in cnt.items(): out.write(f"{cr}\t{ur}\t\t{c}\n")

def write_long_fasta(cnt: Counter, out_fa: Path):
    with open(out_fa,"w") as out:
        for (cr,ur) in cnt.keys():
            combo=f"{cr}{ur}"; out.write(f">{combo}\n{combo}\n")

def bwa_index_if_needed(ref: Path):
    if need_bwa_index(ref):
        log(f"BWA index not found for {ref}. Building...")
        subprocess.check_call(["bwa","index",str(ref)])
    else:
        log("BWA index present.")

def run_bwa_stream(ref: Path, query_fa: Path, out_sam: Path, out_txt: Path, threads: int, extra: str):
    cmd = ["bwa","mem"] + extra.split() + ["-t",str(threads),str(ref),str(query_fa)]
    log_run(cmd + ["| stream ->", str(out_sam),"&",str(out_txt)])
    kept=0
    with open(out_sam,"w") as sam, open(out_txt,"w") as txt:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1<<20)
        assert p.stdout is not None
        for ln in p.stdout:
            sam.write(ln)
            if ln.startswith("@"): continue
            cols = ln.rstrip("\n").split("\t")
            try: flag=int(cols[1])
            except: continue
            if flag!=0: continue
            idx=(0,2,5,9,13,14,15)
            vals=[cols[i] if i<len(cols) else "" for i in idx]
            txt.write("\t".join(vals)+"\n"); kept+=1
        err = p.stderr.read() if p.stderr else ""
        rc = p.wait()
        if err: log(err.rstrip(), level="BWA")
        if rc!=0: log(f"bwa mem exited {rc}", level="ERROR"); sys.exit(4)
    log(f"SAM rows (FLAG==0) → {kept:,}")

def main():
    a = parse_args(); ensure_bwa()
    outdir=Path(a.outdir); ensure_dir(outdir)
    fq=Path(a.fq); ref=Path(a.ref)
    if not ref.exists():
        alt=outdir/"short.fasta"
        if a.ref.endswith("short.fa") and alt.exists():
            log(f"Ref {ref} missing, fallback {alt}"); ref=alt

    long_tsv=outdir/"long.tsv"; long_fa=outdir/"long.fasta"
    sam=outdir/"aln_CR_UR.sam"; txt=outdir/"aln_CR_UR.txt"
    if not a.force:
        for p in (long_tsv,long_fa,sam,txt):
            if p.exists(): log(f"Output exists: {p}. Use --force.", level="ERROR"); sys.exit(1)

    print("=== Parameters ===")
    print(f"Input FASTQ         : {fq}")
    print(f"Reference FASTA     : {ref}")
    print(f"Output dir          : {outdir}")
    print(f"BWA threads         : {a.threads}")
    print(f"BWA extra args      : {a.bwa_args}")
    print("==================\n")

    cnt = count_cr_ur(fq)
    if not cnt: log("No (CR,UR) found.", level="ERROR"); sys.exit(5)
    write_long_tsv(cnt,long_tsv); write_long_fasta(cnt,long_fa)
    bwa_index_if_needed(ref)
    run_bwa_stream(ref,long_fa,sam,txt,a.threads,a.bwa_args)

    print("\n✅ DONE. Outputs:")
    print(f"  - {long_tsv}")
    print(f"  - {long_fa}")
    print(f"  - {sam}")
    print(f"  - {txt}")

if __name__=="__main__":
    main()
