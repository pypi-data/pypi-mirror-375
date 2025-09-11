
import sys, runpy
from typing import List

# Map friendly command names to module paths inside this package
COMMANDS = {
    "cruise": "cruise_toolkit.cruise",
    "barcode-split": "cruise_toolkit.barcode_split",
    "adjust-bc-umi": "cruise_toolkit.adjust_bc_umi",
    "cbumi-counter": "cruise_toolkit.cbumi_counter",
    "cr-ur-align": "cruise_toolkit.cr_ur_align",
    "add-cb-ub": "cruise_toolkit.add_cb_ub",
}

def _forward_to_module(module_name: str, argv: List[str]) -> int:
    # Emulate "python -m module" with provided argv
    old_argv = sys.argv[:]
    try:
        sys.argv = [module_name] + argv
        runpy.run_module(module_name, run_name="__main__")
        return 0
    finally:
        sys.argv = old_argv

def cruise(): return sys.exit(_forward_to_module(COMMANDS["cruise"], sys.argv[1:]))
def barcode_split(): return sys.exit(_forward_to_module(COMMANDS["barcode-split"], sys.argv[1:]))
def adjust_bc_umi(): return sys.exit(_forward_to_module(COMMANDS["adjust-bc-umi"], sys.argv[1:]))
def cbumi_counter(): return sys.exit(_forward_to_module(COMMANDS["cbumi-counter"], sys.argv[1:]))
def cr_ur_align(): return sys.exit(_forward_to_module(COMMANDS["cr-ur-align"], sys.argv[1:]))
def add_cb_ub(): return sys.exit(_forward_to_module(COMMANDS["add-cb-ub"], sys.argv[1:]))
