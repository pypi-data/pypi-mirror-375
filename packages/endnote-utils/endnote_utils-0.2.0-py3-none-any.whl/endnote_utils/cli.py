from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from .core import (
    DEFAULT_FIELDNAMES,
    export_files_with_report,  # generic writer: csv/json/xlsx
)

SUPPORTED_FORMATS = ("csv", "json", "xlsx")
EXT_TO_FORMAT = {".csv": "csv", ".json": "json", ".xlsx": "xlsx"}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Export EndNote XML (file or folder) to CSV/JSON/XLSX with a TXT report."
    )

    # Input source (mutually exclusive)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--xml", help="Path to a single EndNote XML file.")
    g.add_argument("--folder", help="Path to a folder containing *.xml files.")

    # Output selection (CSV legacy flag + new generic flags)
    p.add_argument(
        "--csv",
        required=False,
        help="(Legacy) Output CSV path. Prefer --out for csv/json/xlsx.",
    )
    p.add_argument(
        "--out",
        required=False,
        help="Generic output path; format inferred from file extension if --format not provided. "
             "Supported extensions: .csv, .json, .xlsx",
    )
    p.add_argument(
        "--format",
        choices=SUPPORTED_FORMATS,
        help="Output format. If omitted, inferred from --out extension or --csv.",
    )

    # Report controls
    p.add_argument("--report", required=False, help="Path to TXT report (default: <output>_report.txt).")
    p.add_argument(
        "--no-report",
        action="store_true",
        help="Disable writing the TXT report (by default, a report is always generated).",
    )

    # CSV-specific formatting options (ignored for JSON/XLSX except delimiter/quoting/header)
    p.add_argument("--delimiter", default=",", help="CSV delimiter (default: ',').")
    p.add_argument(
        "--quoting",
        default="minimal",
        choices=["minimal", "all", "nonnumeric", "none"],
        help="CSV quoting mode (default: minimal).",
    )
    p.add_argument("--no-header", action="store_true", help="Do not write CSV header row.")
    p.add_argument("--encoding", default="utf-8", help="Output text encoding (default: utf-8).")

    # Filters / limits
    p.add_argument("--ref-type", default=None, help="Filter by ref_type name.")
    p.add_argument("--year", default=None, help="Filter by year.")
    p.add_argument("--max-records", type=int, default=None, help="Max records per file (testing).")
    
    # Deduplication & Stats
    p.add_argument("--dedupe", choices=["none", "doi", "title-year"], default="none",
                help="Deduplicate records by key. Default: none.")
    p.add_argument("--dedupe-keep", choices=["first", "last"], default="first",
                help="When duplicates found, keep the first or last occurrence. Default: first.")
    p.add_argument("--stats", action="store_true",
                help="Compute summary stats and include them in the TXT report.")
    p.add_argument("--stats-json",
                help="Optional JSON file path to write detailed stats (when --stats is used).")
    p.add_argument("--top-authors", type=int, default=10,
                help="How many top authors to list in the report/stats JSON. Default: 10.")

    # Verbosity
    p.add_argument("--verbose", action="store_true", help="Verbose logging.")

    return p


def _resolve_inputs(args: argparse.Namespace) -> List[Path]:
    if args.xml:
        xml_path = Path(args.xml)
        if not xml_path.is_file():
            raise FileNotFoundError(xml_path)
        return [xml_path]

    folder = Path(args.folder)
    if not folder.is_dir():
        raise FileNotFoundError(folder)
    inputs = sorted(p for p in folder.glob("*.xml") if p.is_file())
    if not inputs:
        raise FileNotFoundError(f"No *.xml files found in folder: {folder}")
    return inputs


def _resolve_output_and_format(args: argparse.Namespace) -> tuple[Path, str, Optional[Path]]:
    """
    Decide final out_path, out_format, and report_path using:
      - Prefer --out/--format if provided
      - Fallback to --csv (legacy) which implies CSV
      - If --no-report, return report_path=None
    """
    target_path: Optional[Path] = None
    out_format: Optional[str] = None

    if args.out:
        target_path = Path(args.out)
        out_format = args.format
        if not out_format:
            # infer from extension
            out_format = EXT_TO_FORMAT.get(target_path.suffix.lower())
            if not out_format:
                raise SystemExit(
                    "Cannot infer output format from extension. "
                    "Use --format {csv,json,xlsx} or set a supported extension."
                )
    elif args.csv:
        target_path = Path(args.csv)
        out_format = args.format or "csv"
        if out_format != "csv":
            # user asked for non-csv but used --csv path
            raise SystemExit("When using --csv, --format must be 'csv'. Use --out for json/xlsx.")
    else:
        raise SystemExit("You must provide either --out (preferred) or --csv (legacy).")

    # Report path defaults next to chosen output file (unless disabled)
    if args.no_report:
        report_path: Optional[Path] = None
    else:
        report_path = Path(args.report) if args.report else target_path.with_name(target_path.stem + "_report.txt")

    return target_path, out_format, report_path


def main() -> None:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )

    try:
        inputs = _resolve_inputs(args)
        out_path, out_format, report_path = _resolve_output_and_format(args)

        total, final_out, final_report = export_files_with_report(
            inputs=inputs,
            out_path=out_path,
            out_format=out_format,
            fieldnames=DEFAULT_FIELDNAMES,
            delimiter=args.delimiter,
            quoting=args.quoting,
            include_header=not args.no_header,
            encoding=args.encoding,
            ref_type=args.ref_type,
            year=args.year,
            max_records_per_file=args.max_records,
            dedupe=args.dedupe,
            dedupe_keep=args.dedupe_keep,
            stats=args.stats,
            stats_json=Path(args.stats_json) if args.stats_json else None,
            top_authors=args.top_authors,
            report_path=report_path,  # may be None → core should skip writing report
        )

        logging.info("Exported %d record(s) → %s", total, final_out)
        if report_path is None:
            logging.info("Report disabled by --no-report.")
        else:
            logging.info("Report → %s", final_report)

    except FileNotFoundError as e:
        logging.error("File/folder not found: %s", e)
        sys.exit(1)
    except Exception as e:
        logging.error("Unexpected error: %s", e)
        sys.exit(2)
