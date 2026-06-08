"""Command line interface."""

from __future__ import annotations

import argparse
import importlib.util

from tlmpy._version import __version__


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="tlmpy")
    parser.add_argument("--version", action="store_true", help="print version and exit")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("info")
    args = parser.parse_args(argv)
    if args.version:
        print(__version__)
        return 0
    if args.command == "info":
        cupy = importlib.util.find_spec("cupy") is not None
        backends = ["numpy"] + (["cupy"] if cupy else [])
        print(f"TLMpy version: {__version__}")
        print(f"Available backends: {', '.join(backends)}")
        print(f"CuPy importable: {cupy}")
        return 0
    parser.print_help()
    return 0

