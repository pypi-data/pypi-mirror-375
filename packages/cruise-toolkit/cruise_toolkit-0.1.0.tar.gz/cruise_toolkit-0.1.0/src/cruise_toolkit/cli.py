
import argparse
import logging
import sys
import runpy

def main():
    parser = argparse.ArgumentParser(
        prog="cruise-toolkit",
        description="Run cruise main workflow with unified logging."
    )
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"],
                        help="Global log level (default: INFO)")
    parser.add_argument("--log-file", default=None, help="Optional path to a log file")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    args, passthrough = parser.parse_known_args()

    if args.version:
        try:
            from importlib.metadata import version
            print(f"cruise-toolkit {version('cruise-toolkit')}")
        except Exception:
            print("cruise-toolkit (version unknown)")
        sys.exit(0)

    # Configure logging
    log_handlers = [logging.StreamHandler(sys.stderr)]
    if args.log_file:
        log_handlers.append(logging.FileHandler(args.log_file, mode="a", encoding="utf-8"))
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=log_handlers,
        force=True,
    )

    # Forward all remaining args to cruise_toolkit.cruise
    try:
        old_argv = sys.argv[:]
        sys.argv = ["cruise_toolkit.cruise"] + passthrough
        runpy.run_module("cruise_toolkit.cruise", run_name="__main__")
    finally:
        sys.argv = old_argv

if __name__ == "__main__":
    main()
