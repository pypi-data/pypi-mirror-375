#!/usr/bin/env python3
"""
parsedat_bedrock.__main__

CLI entry point for ParseDAT Bedrock.
"""

import argparse
import json
from parsedat_bedrock.parser import parse_bedrock_leveldat


def main() -> None:
    """
    CLI entry point. Converts level.dat to JSON.

    Arguments
    ---------
    input_path : Path to level.dat
    --out, -o  : Output JSON file. If omitted and --stdout not set, defaults to input_path with .json.
    --stdout   : Write JSON to stdout instead of a file.
    --pretty   : Pretty-print JSON with indentation.
    --preserve-types : Emit typed JSON objects as {"type": "...","value": ...}.
    --ensure-ascii   : Escape non-ASCII in JSON output.
    --debug     : Include internal parse info (_debug) to help diagnose weird files.
    """
    ap = argparse.ArgumentParser(description="Convert Minecraft Bedrock level.dat (NBTLE) to JSON.")
    ap.add_argument("input_path", help="Path to level.dat")
    ap.add_argument("--out", "-o", dest="out_path", help="Output JSON path")
    ap.add_argument("--stdout", action="store_true", help="Write JSON to stdout")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    ap.add_argument("--preserve-types", action="store_true", help="Preserve NBT types in JSON output")
    ap.add_argument("--ensure-ascii", action="store_true", help="Escape non-ASCII chars in JSON")
    ap.add_argument("--debug", action="store_true", help="Include parse debug info (_debug) in JSON output")
    args = ap.parse_args()

    with open(args.input_path, "rb") as f:
        raw = f.read()

    root_obj = parse_bedrock_leveldat(raw, preserve_types=args.preserve_types, debug=args.debug)

    indent = 2 if args.pretty else None
    json_text = json.dumps(root_obj, indent=indent, ensure_ascii=args.ensure_ascii)

    if args.stdout:
        print(json_text)
        return

    out_path = args.out_path
    if not out_path:
        if args.input_path.lower().endswith(".dat"):
            out_path = args.input_path[:-4] + ".json"
        else:
            out_path = args.input_path + ".json"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(json_text)


if __name__ == "__main__":
    main()
