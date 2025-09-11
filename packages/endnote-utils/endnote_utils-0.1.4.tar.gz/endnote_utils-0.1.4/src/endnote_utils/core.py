# src/endnote_exporter/core.py
from __future__ import annotations

import csv
import logging
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

DEFAULT_FIELDNAMES: List[str] = [
    "database", "ref_type", "title", "journal", "authors", "year",
    "volume", "number", "abstract", "doi", "urls", "extracted_date",
]

CSV_QUOTING_MAP = {
    "minimal": csv.QUOTE_MINIMAL,
    "all": csv.QUOTE_ALL,
    "nonnumeric": csv.QUOTE_NONNUMERIC,
    "none": csv.QUOTE_NONE,
}

def ensure_parent_dir(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)

# ----------------------------
# Utilities
# ----------------------------

def clean_text(text: Optional[str]) -> str:
    """
    Trim, collapse internal whitespace, remove stray CRs, keep punctuation intact.
    Safer for CSV fields than aggressive normalization.
    """
    if not text:
        return ""
    text = text.replace("\r", " ")
    return " ".join(text.split()).strip()


def safe_find_text(node: ET.Element, path: str) -> str:
    """Find text with XPath and return cleaned string."""
    elem = node.find(path)
    return clean_text(elem.text) if elem is not None and elem.text is not None else ""


def join_nonempty(items: Iterable[str], sep: str) -> str:
    return sep.join(x for x in (i.strip() for i in items) if x)

def ensure_parent_dir(p: Path) -> None:
    """Create parent directory if it doesn't exist."""
    if not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)


# ----------------------------
# Record processing
# ----------------------------

def process_doi(record: ET.Element) -> str:
    """Extract and format DOI information to a canonical URL if possible."""
    doi_raw = safe_find_text(record, ".//electronic-resource-num/style")
    if not doi_raw:
        return ""
    if doi_raw.startswith("10."):
        return f"https://doi.org/{doi_raw}"
    if doi_raw.startswith(("http://", "https://")):
        return doi_raw
    return ""


def extract_authors(record: ET.Element) -> str:
    """Collect authors from //author/style, joined by '; '."""
    authors: List[str] = []
    for author in record.findall(".//author"):
        style = author.find("style")
        if style is not None and style.text:
            authors.append(clean_text(style.text))
    return join_nonempty(authors, "; ")


def extract_urls(record: ET.Element) -> str:
    """Collect related URLs from //urls/related-urls/url/style, joined by ' | '."""
    urls: List[str] = []
    for url in record.findall(".//urls/related-urls/url"):
        style = url.find("style")
        if style is not None and style.text:
            urls.append(clean_text(style.text))
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            deduped.append(u)
    return join_nonempty(deduped, " | ")


def process_record(record: ET.Element, database: str) -> Dict[str, str]:
    """Transform a <record> element into a dictionary for CSV."""
    ref_type_name = ""
    ref_type = record.find("ref-type")
    if ref_type is not None:
        ref_type_name = ref_type.get("name") or ""

    return {
        "database": database,
        "ref_type": clean_text(ref_type_name),
        "title": safe_find_text(record, ".//title/style"),
        "journal": safe_find_text(record, ".//secondary-title/style"),
        "authors": extract_authors(record),
        "year": safe_find_text(record, ".//year/style"),
        "volume": safe_find_text(record, ".//volume/style"),
        "number": safe_find_text(record, ".//number/style"),
        "abstract": safe_find_text(record, ".//abstract/style"),
        "doi": process_doi(record),
        "urls": extract_urls(record),
        "extracted_date": datetime.now().strftime("%Y-%m-%d"),
    }

def iter_records(xml_path: Path) -> Iterable[ET.Element]:
    context = ET.iterparse(str(xml_path), events=("start", "end"))
    _, root = next(context)
    for event, elem in context:
        if event == "end" and elem.tag == "record":
            yield elem
            elem.clear()
            root.clear()

def record_matches_filters(row: Dict[str, str], ref_type: Optional[str], year: Optional[str]) -> bool:
    if ref_type and row.get("ref_type") != ref_type: return False
    if year and row.get("year") != str(year): return False
    return True

def export_files_to_csv_with_report(
    inputs: List[Path],
    csv_path: Path,
    report_path: Optional[Path] = None,
    *,
    fieldnames: List[str] = None,
    delimiter: str = ",",
    quoting: str = "minimal",
    include_header: bool = True,
    encoding: str = "utf-8",
    ref_type: Optional[str] = None,
    year: Optional[str] = None,
    max_records_per_file: Optional[int] = None,
) -> Tuple[int, Path, Path]:
    """Primary library API: export one or many XML files to a single CSV + TXT report."""
    fieldnames = fieldnames or DEFAULT_FIELDNAMES
    qmode = CSV_QUOTING_MAP[quoting]
    report_path = report_path or csv_path.with_name(csv_path.stem + "_report.txt")

    ensure_parent_dir(csv_path)
    ensure_parent_dir(report_path)

    total_written, report_lines = 0, []
    start_ts = time.time()
    run_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(csv_path, "w", newline="", encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter, quoting=qmode)
        if include_header:
            writer.writeheader()

        for xml_path in inputs:
            database = xml_path.stem
            logging.info("Processing %s (database=%s)", xml_path.name, database)
            file_written = file_skipped = 0

            for rec in iter_records(xml_path):
                try:
                    row = process_record(rec, database=database)  # your existing function
                    if record_matches_filters(row, ref_type, year):
                        writer.writerow({k: row.get(k, "") for k in fieldnames})
                        file_written += 1
                        total_written += 1
                        if max_records_per_file and file_written >= max_records_per_file:
                            break
                except Exception:
                    file_skipped += 1
                    logging.debug("Record error in %s", xml_path, exc_info=True)

            report_lines.append(f"{xml_path.name}: {file_written} exported, {file_skipped} skipped")

    dur = time.time() - start_ts
    report_lines = [
        f"Run started: {run_start}",
        *report_lines,
        f"TOTAL exported: {total_written}",
        f"Files processed: {len(inputs)}",
        f"Duration: {dur:.2f} seconds",
    ]
    with open(report_path, "w", encoding="utf-8") as rf:
        rf.write("\n".join(report_lines))

    return total_written, csv_path, report_path

def export(xml_file: Path, csv_path: Path, **kwargs):
    """Convenience: single XML file to CSV (+report)."""
    return export_files_to_csv_with_report([xml_file], csv_path, **kwargs)

def export_folder(folder: Path, csv_path: Path, **kwargs):
    """Convenience: all *.xml in folder to CSV (+report)."""
    inputs = sorted(p for p in Path(folder).glob("*.xml") if p.is_file())
    if not inputs:
        raise FileNotFoundError(f"No *.xml found in {folder}")
    return export_files_to_csv_with_report(inputs, csv_path, **kwargs)
