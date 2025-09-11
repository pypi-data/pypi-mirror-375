from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .core import DEFAULT_FIELDNAMES, export, export_folder


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Export EndNote XML (file or folder) to CSV + TXT report.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--xml", help="Path to a single EndNote XML file.")
    g.add_argument("--folder", help="Path to a folder containing *.xml files.")
    p.add_argument("--csv", required=True, help="Path to CSV output file.")
    p.add_argument("--report", required=False, help="Path to TXT report (default: <csv>_report.txt).")
    p.add_argument("--delimiter", default=",")
    p.add_argument("--quoting", default="minimal", choices=["minimal","all","nonnumeric","none"])
    p.add_argument("--no-header", action="store_true")
    p.add_argument("--encoding", default="utf-8")
    p.add_argument("--ref-type", default=None)
    p.add_argument("--year", default=None)
    p.add_argument("--max-records", type=int, default=None)
    p.add_argument("--verbose", action="store_true")
    return p

def main() -> None:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s", stream=sys.stderr
    )
    csv_path = Path(args.csv)
    report_path = Path(args.report) if args.report else csv_path.with_name(csv_path.stem + "_report.txt")
    kwargs = dict(
        report_path=report_path,
        fieldnames=DEFAULT_FIELDNAMES,
        delimiter=args.delimiter,
        quoting=args.quoting,
        include_header=not args.no_header,
        encoding=args.encoding,
        ref_type=args.ref_type,
        year=args.year,
        max_records_per_file=args.max_records,
    )

    if args.xml:
        total, csv_out, rep_out = export(Path(args.xml), csv_path, **kwargs)
    else:
        total, csv_out, rep_out = export_folder(Path(args.folder), csv_path, **kwargs)

    logging.info("Exported %d record(s) → %s", total, csv_out)
    logging.info("Report → %s", rep_out)
