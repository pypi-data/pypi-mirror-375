#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cbumi_counter.py

Parallel (CB, UMI) counter to produce:
  - short.tsv (CB,UMI, ,count)
  - short.fasta (one entry per CB+UMI)
"""

import argparse, os, sys, time
from collections import defaultdict
from multiprocessing import Pool, cpu_count, Process, Manager, get_context
from typing import Dict, Tuple, List, Optional, Iterable
from pathlib import Path
from datetime import datetime
from common_utils import log, log_run, ensure_dir

try:
    import pysam
except ImportError:
    log("pysam is required: pip install pysam", level="ERROR"); raise

try:
    from sys import intern  # type: ignore
except Exception:
    def intern(s: str) -> str: return s

LOG_Q=None  # worker queue

def parse_args():
    p = argparse.ArgumentParser(description="(CB,UMI) counter with chunked parallelism & live logging.")
    p.add_argument("-i","--in-bam", required=True, help="Input BAM (coordinate-sorted + indexed)")
    p.add_argument("-o","--outdir", required=True, help="Output directory")
    p.add_argument("--min-mapq", type=int, default=20)
    p.add_argument("--threads", type=int, default=max(1,cpu_count()))
    p.add_argument("--bam-threads", type=int, default=2, help="htslib threads per worker")
    p.add_argument("--cb-tags", default="CC,CB")
    p.add_argument("--umi-tag", default="UB")
    p.add_argument("--chunk-size", type=int, default=20_000_000)
    p.add_argument("--max-chunks", type=int, default=200000)
    p.add_argument("--cb-whitelist", default=None)
    p.add_argument("--min-count", type=int, default=1)
    p.add_argument("--no-fasta", action="store_true")
    p.add_argument("--force", action="store_true")
    return p.parse_args()

def has_index(bam: str) -> bool:
    try:
        b=pysam.AlignmentFile(bam,"rb")
        try:
            if hasattr(b,"has_index") and b.has_index(): return True
        finally:
            b.close()
    except: pass
    return os.path.exists(bam+".bai") or os.path.exists(bam+".csi")

def load_whitelist(path: Optional[str]) -> Optional[set]:
    if not path: return None
    s=set()
    with open(path) as fh:
        for ln in fh:
            w=ln.strip(); 
            if w: s.add(intern(w))
    return s

def build_chunks(bam: str, chunk: int, cap: int) -> List[Tuple[str,int,int]]:
    b=pysam.AlignmentFile(bam,"rb"); res=[]
    try:
        for r,n in zip(b.header.references, b.header.lengths):
            if n<=0: continue
            start=0
            while start<n:
                end=min(start+chunk, n); res.append((r,start,end)); start=end
                if len(res)>cap: raise RuntimeError(f"Too many chunks ({len(res)}); increase --chunk-size")
    finally:
        b.close()
    return res

def _should_keep(aln, q: int)->bool:
    return not (aln.is_unmapped or aln.is_secondary or aln.is_supplementary) and aln.mapping_quality>=q

def _first_tag(aln, tags: List[str]) -> Optional[str]:
    for t in tags:
        if aln.has_tag(t): return aln.get_tag(t)
    return None

def logger_process(q, interval: float):
    start=time.time(); last=start; reads=0; keys=0; shards=0
    try:
        while True:
            try: kind,val=q.get(timeout=interval)
            except Exception:
                now=time.time()
                if now-last>=interval:
                    el=max(1e-6, now-start)
                    rps=reads/el; kps=keys/el
                    log(f"progress reads={reads:,} ({rps:,.0f}/s) keys={keys:,} ({kps:,.0f}/s) shards_done={shards}")
                    last=now
                continue
            if kind=="__DONE__": break
            if kind=="reads": reads+=val
            elif kind=="pairs": keys+=val
            elif kind=="shard_done": shards+=1
    finally:
        el=max(1e-6,time.time()-start)
        log(f"FINAL reads={reads:,} ({reads/el:,.0f}/s), keys={keys:,} ({keys/el:,.0f}/s), shards_done={shards}")

def _init_worker(q): 
    global LOG_Q; LOG_Q=q

def _push(msg): 
    if LOG_Q is not None:
        try: LOG_Q.put(msg, block=False)
        except: pass

def worker(args)->str:
    (bam_path,rname,beg,end,min_mapq,cb_tags,umi_tag,bam_threads,outdir,tmp_prefix,wl)=args
    cbumi=defaultdict(int); reads=0
    bam=pysam.AlignmentFile(bam_path,"rb")
    try:
        try: bam.set_threads(bam_threads)  # type: ignore[attr-defined]
        except: pass
        for aln in bam.fetch(rname,beg,end):
            reads+=1
            if (reads & 0xFFFFF)==0: _push(("reads",0x100000)); _push(("pairs",0))
            if not _should_keep(aln,min_mapq): continue
            cb=_first_tag(aln,cb_tags)
            if cb is None: continue
            if wl is not None and cb not in wl: continue
            if not aln.has_tag(umi_tag): continue
            umi=aln.get_tag(umi_tag)
            cbumi[(intern(cb),intern(umi))]+=1
    finally:
        bam.close()
    residual=reads & 0xFFFFF
    if residual: _push(("reads",residual))
    shard=str(Path(outdir)/f"cbumi_{rname}_{beg}_{end}.tsv")
    if cbumi:
        with open(shard,"w") as fh:
            for (cb,umi),c in cbumi.items(): fh.write(f"{cb}\t{umi}\t\t{c}\n")
        _push(("pairs",len(cbumi)))
    else:
        open(shard,"w").close()
    _push(("shard_done",1))
    return shard

def merge_shards(paths: Iterable[str], out_tsv: str, min_count: int)->int:
    tot=defaultdict(int)
    for sp in paths:
        with open(sp) as fh:
            for ln in fh:
                ps=ln.rstrip("\n").split("\t")
                if len(ps)<4: continue
                try: cnt=int(ps[3])
                except: continue
                if cnt<min_count: continue
                tot[(ps[0],ps[1])]+=cnt
    with open(out_tsv,"w") as out:
        for (cb,umi),c in tot.items():
            if c>=min_count: out.write(f"{cb}\t{umi}\t\t{c}\n")
    return len(tot)

def write_fasta(tsv: str, fa: str):
    seen=set()
    with open(tsv) as fh, open(fa,"w") as out:
        for ln in fh:
            ps=ln.rstrip("\n").split("\t")
            if len(ps)<2: continue
            key=ps[0]+ps[1]
            if key in seen: continue
            seen.add(key); out.write(f">{key}\n{key}\n")

def main():
    a=parse_args(); ensure_dir(a.outdir)
    out_tsv=str(Path(a.outdir)/"short.tsv")
    out_fa=str(Path(a.outdir)/"short.fasta")
    if not a.force and (Path(out_tsv).exists() or (Path(out_fa).exists() and not a.no_fasta)):
        log("Outputs exist. Use --force.", level="ERROR"); sys.exit(1)
    if not has_index(a.in_bam):
        log("BAM index missing (.bai/.csi). Run: samtools index <bam>", level="ERROR"); sys.exit(2)

    wl=load_whitelist(a.cb_whitelist)
    cb_tags=[t.strip() for t in a.cb_tags.split(",") if t.strip()]
    chunks=build_chunks(a.in_bam,a.chunk_size,a.max_chunks)
    if not chunks: log("No chunks from BAM header.", level="ERROR"); sys.exit(3)

    print("=== Parameters ===")
    print(f"Input BAM           : {a.in_bam}")
    print(f"Output dir          : {a.outdir}")
    print(f"Min MAPQ            : {a.min_mapq}")
    print(f"Workers             : {min(a.threads, len(chunks))}")
    print(f"htslib threads/worker: {a.bam_threads}")
    print(f"CB tags             : {','.join(cb_tags)}")
    print(f"UMI tag             : {a.umi_tag}")
    print(f"Chunk size          : {a.chunk_size:,}")
    print(f"Whitelist           : {a.cb_whitelist or '(none)'}")
    print(f"Min count (merge)   : {a.min_count}")
    print(f"FASTA output        : {'OFF' if a.no_fasta else 'ON'}")
    print("==================\n")

    mgr=Manager(); q=mgr.Queue(maxsize=10000)
    logp=Process(target=logger_process, args=(q, 2.0), daemon=True); logp.start()

    work=[(a.in_bam,r,s,e,a.min_mapq,cb_tags,a.umi_tag,a.bam_threads,a.outdir,"cbumi_",wl) for (r,s,e) in chunks]
    nproc=max(1,min(a.threads,len(work)))
    try:
        try: ctx=get_context("fork")
        except ValueError: ctx=get_context()
        shard_paths=[]
        log_run([f"start workers nproc={nproc}", f"shards={len(work):,}"])
        with ctx.Pool(processes=nproc, initializer=_init_worker, initargs=(q,)) as pool:
            for sp in pool.imap_unordered(worker, work, chunksize=4):
                shard_paths.append(sp)
    finally:
        try: q.put(("__DONE__",None))
        except: pass
        logp.join(timeout=5)

    nkeys=merge_shards(shard_paths, out_tsv, a.min_count)
    if not a.no_fasta: write_fasta(out_tsv,out_fa)
    for sp in shard_paths:
        try: os.remove(sp)
        except: pass

    print("\n✅ DONE. Kept outputs:")
    print(f"  - TSV  : {out_tsv}")
    if not a.no_fasta:
        print(f"  - FASTA: {out_fa}")
    log(f"Unique (CB,UMI) pairs: {nkeys:,}")

if __name__=="__main__":
    main()
