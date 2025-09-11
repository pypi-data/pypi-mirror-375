#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os, sys, subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Union

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg: str, level: str = "INFO", end: str = "\n") -> None:
    sys.stderr.write(f"[{_now()}] {level}: {msg}{end}")
    sys.stderr.flush()

def log_run(cmd: List[str]) -> None:
    log("RUN: " + " ".join(map(str, cmd)))

def ensure_dir(*paths: Union[str, Path]) -> None:
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)

def run_cmd(cmd: List[str], log_file: Optional[Path] = None, check: bool = True) -> int:
    """Stream stdout to console and optional log file, fail fast on nonzero exit."""
    log_run(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    with proc.stdout as pipe, (open(log_file, "a") if log_file else open(os.devnull, "w")) as lf:
        for line in pipe:
            sys.stderr.write(line)
            if log_file:
                lf.write(line)
    code = proc.wait()
    if check and code != 0:
        raise SystemExit(f"[ERR] Command failed (exit {code}): {' '.join(cmd)}")
    return code

def run_cmd_capture(cmd: List[str]) -> str:
    """Return stdout text (for small outputs)."""
    log_run(cmd)
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if res.returncode != 0:
        sys.stderr.write(res.stdout or "")
        raise SystemExit(f"[ERR] Command failed (exit {res.returncode}): {' '.join(cmd)}")
    return res.stdout

def run_cmd_to_file(cmd: List[str], outfile: Path) -> None:
    """Write stdout to file (truncate)."""
    log_run(cmd + [">", str(outfile)])
    with open(outfile, "w") as fh:
        res = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, text=True)
    if res.returncode != 0:
        raise SystemExit(f"[ERR] Command failed (exit {res.returncode}): {' '.join(cmd)}")
