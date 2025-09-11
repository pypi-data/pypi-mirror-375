#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
barcode_split.py

Single-FASTQ pipeline driven by ADAPT + MODEL:
- MODEL contains A/C/G/T fixed, B=CR, U=UR
- cutadapt#1: pattern1 = ADAPT + MODEL_N (B/U->N); err=0.2; min_overlap1=floor(0.9 * len(pattern1)); -m=min_overlap1
- split at (len(MODEL)+10): R1=1..split_len, R2=split_len..end
- cutadapt#2: pattern2 = MODEL_N; err=0.2; min_overlap2=len(MODEL); -m=min_overlap2
- PISA parse2: rule built only from MODEL (R1 counted from MODEL start; 1-based)
Keeps only:
  - workdir/model.retain.mask.drc.merge.fq
  - workdir/qc.standard.reads.txt
"""

import argparse, math, re
from pathlib import Path
from typing import List, Tuple, Optional
from common_utils import log, log_run, ensure_dir, run_cmd, run_cmd_capture, run_cmd_to_file

def parse_args():
    p = argparse.ArgumentParser(description="Split FASTQ by ADAPT/MODEL; emit merged fq + QC.")
    p.add_argument("-i","--fastq", required=True, help="Input FASTQ (.fq/.fastq/.gz)")
    p.add_argument("--adapt", required=True, help="Adapter (A/C/G/T only)")
    p.add_argument("--model", required=True, help="Model (A/C/G/T/B/U; B=CR, U=UR)")
    p.add_argument("-j","--threads", type=int, default=8, help="Threads for cutadapt/fastp")
    p.add_argument("--workdir", default="01.barcode", help="Working directory")
    p.add_argument("--min_len", type=int, default=200, help="Initial length filter threshold")
    p.add_argument("--q", type=int, default=10, help="fastp Q threshold")
    p.add_argument("--u", type=int, default=40, help="fastp allowed low-quality percentage")
    p.add_argument("--revcomp", dest="revcomp", action="store_true", default=True, help="cutadapt --revcomp")
    p.add_argument("--no-revcomp", dest="revcomp", action="store_false", help="Disable --revcomp")
    p.add_argument("--keep-temp", action="store_true", help="Keep intermediates for debugging")
    return p.parse_args()

def validate(adapt: str, model: str):
    if not re.fullmatch(r"[ACGT]+", adapt): raise SystemExit("[ERR] --adapt must be A/C/G/T only")
    if not re.fullmatch(r"[ACGTBU]+", model): raise SystemExit("[ERR] --model must be A/C/G/T/B/U")

def model_to_N(model: str) -> str:
    return ''.join('N' if c in ('B','U') else c for c in model)

def find_runs(s: str, ch: str):
    runs=[]; i=0
    while i<len(s):
        if s[i]==ch:
            j=i
            while j+1<len(s) and s[j+1]==ch: j+=1
            runs.append((i,j)); i=j+1
        else: i+=1
    return runs

def pisa_rule_from_model(model: str) -> str:
    entries=[]
    for s,e in find_runs(model,'B'): entries.append(f"CR,R1:{s+1}-{e+1}")
    for s,e in find_runs(model,'U'): entries.append(f"UR,R1:{s+1}-{e+1}")
    entries.append("R1,R2")
    return ";".join(entries)

def append_seqkit_stat_line(fastq: Path, qc: Path):
    qc.parent.mkdir(parents=True, exist_ok=True); qc.touch(exist_ok=True)
    out = run_cmd_capture(["seqkit","stat",str(fastq),"--all"])
    lines=[ln for ln in out.splitlines() if ln.strip()]
    if lines:
        with open(qc,"a") as f: f.write(lines[-1]+"\n")

def main():
    a = parse_args()
    validate(a.adapt, a.model)
    wd = Path(a.workdir); ensure_dir(wd)
    qc = wd/"qc.standard.reads.txt"; qc.touch(exist_ok=True)

    modelN = model_to_N(a.model)
    pattern1 = a.adapt + modelN
    min1 = math.floor(len(pattern1)*0.9)
    pattern2 = modelN
    min2 = len(a.model)
    split_len = len(a.model + a.adapt) + 5
    rule = pisa_rule_from_model(a.model)

    print("=== Parameters ===")
    print(f"Input FASTQ         : {a.fastq}")
    print(f"ADAPT               : {a.adapt}")
    print(f"MODEL               : {a.model}")
    print(f"MODEL (B/U->N)      : {modelN}")
    print(f"Pattern #1          : {pattern1}")
    print(f"min_overlap #1 / -m : {min1}")
    print(f"Pattern #2          : {pattern2}")
    print(f"min_overlap #2 / -m : {min2}")
    print(f"R1 split range      : 1:{split_len}")
    print(f"PISA -rule          : {rule}")
    print("==================\n")

    temps = []
    try:
        # 0) QC on raw
        append_seqkit_stat_line(Path(a.fastq), qc)

        # 1) length filter
        f200 = wd/"tmp.200.fq"; temps.append(f200)
        run_cmd_to_file(["seqkit","seq","-m",str(a.min_len),a.fastq], f200)
        append_seqkit_stat_line(f200, qc)

        # 2) fastp
        fqQ = wd/"tmp.q10.fq"; temps.append(fqQ)
        run_cmd([
            "fastp","-i",str(f200),"-A","-q",str(a.q),"-u",str(a.u),
            "-o",str(fqQ),"-w",str(a.threads),
            "-j",str(wd/"fastp.json"),"-h",str(wd/"fastp.html")
        ], log_file=wd/"log.fastp.txt")
        append_seqkit_stat_line(fqQ, qc)

        # 3) cutadapt #1
        retain = wd/"tmp.retain.fq"; temps.append(retain)
        untrim = wd/"tmp.untrim.fq"; temps.append(untrim)
        cmd1 = ["cutadapt","-j",str(a.threads),"-g",f"{pattern1};max_error_rate=0.2;min_overlap={min1}"]
        if a.revcomp: cmd1.append("--revcomp")
        cmd1 += ["-o",str(retain),str(fqQ),"--action=retain","--rename","{header}","-m",str(min1+100),"--untrimmed-output",str(untrim)]
        run_cmd(cmd1, log_file=wd/"cut1.out")
        append_seqkit_stat_line(retain, qc)

        # 4) split
        r1 = wd/"tmp.r1.fq"; r2 = wd/"tmp.r2.fq"; temps += [r1,r2]
        run_cmd_to_file(["seqkit","subseq","-r",f"1:{split_len}",str(retain)], r1)
        run_cmd_to_file(["seqkit","subseq","-r",f"{split_len}:-1",str(retain)], r2)

        # 5) cutadapt #2
        r1f = wd/"tmp.r1f.fq"; r1u = wd/"tmp.r1u.fq"; temps += [r1f,r1u]
        cmd2 = ["cutadapt","-j",str(a.threads),"-g",f"{pattern2};max_error_rate=0.2;min_overlap={min2}"]
        if a.revcomp: cmd2.append("--revcomp")
        cmd2 += ["-o",str(r1f),str(r1),"--action=retain","-m",str(min2),"--untrimmed-output",str(r1u)]
        run_cmd(cmd2, log_file=wd/"cut2.out")

        # 6) pair IDs to filter r2
        ids = wd/"tmp.ids"; temps.append(ids)
        r2f = wd/"tmp.r2f.fq"; temps.append(r2f)
        run_cmd_to_file(["seqkit","seq",str(r1f),"-n","-i"], ids)
        run_cmd(["seqkit","grep","-n","-f",str(ids),str(r2),"-o",str(r2f)], log_file=wd/"log.seqkit_grep.txt")

        # 7) PISA parse2 → final
        final_merge = wd/"model.retain.mask.drc.merge.fq"
        run_cmd(["PISA","parse2","-rule",rule,"-1",str(final_merge),str(r1f),str(r2f)], log_file=wd/"log.pisa.txt")

        # 8) final QC
        append_seqkit_stat_line(final_merge, qc)

        # cleanup
        if not a.keep_temp:
            for p in temps:
                try: p.unlink()
                except: pass

        print("\n✅ DONE. Kept only:")
        print(f"  - {final_merge}")
        print(f"  - {qc}")

    except SystemExit:
        log("Pipeline failed. Temps kept for debugging.", level="ERROR")
        raise

if __name__ == "__main__":
    main()
