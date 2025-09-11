# EndNote Utils

Convert **EndNote XML files** into clean CSV/JSON/XLSX with automatic TXT reports.  
Supports both **Python API** and **command-line interface (CLI)**.

---

## Features

- ✅ Parse one XML file (`--xml`) or an entire folder of `*.xml` (`--folder`)
- ✅ Streams `<record>` elements using `iterparse` (low memory usage)
- ✅ Extracts fields:  
  `database, ref_type, title, journal, authors, year, volume, number, abstract, doi, urls, keywords, publisher, isbn, language, extracted_date`
- ✅ Adds a `database` column from the XML filename stem (`IEEE.xml → IEEE`)
- ✅ Normalizes DOI (`10.xxxx` → `https://doi.org/...`)
- ✅ Supports **multiple output formats**: CSV, JSON, XLSX
- ✅ Always generates a **TXT report** (default: `<out>_report.txt`) with:
  - per-file counts (exported/skipped)
  - totals, files processed
  - run timestamp & duration
  - **duplicate table** per database (Origin / Retractions / Duplicates / Remaining)
  - optional duplicate key list (top-N)
  - optional summary stats (year, ref_type, journal, top authors)
- ✅ Auto-creates output folders if missing
- ✅ Deduplication:
  - `--dedupe doi` (unique by DOI)
  - `--dedupe title-year` (unique by normalized title + year)
  - `--dedupe-keep first|last` (keep first or last occurrence within each file)
- ✅ Summary stats (`--stats`) with optional JSON export (`--stats-json`)
- ✅ CLI options for CSV formatting, filters, verbosity
- ✅ Importable Python API for scripting & integration

---

## Installation

### From PyPI

```bash
pip install endnote-utils
```

Requires **Python 3.8+**.

---

## Usage

### Command Line

#### Single file

```bash
endnote-utils --xml data/IEEE.xml --out output/ieee.csv
```

#### Folder with multiple files

```bash
endnote-utils --folder data/xmls --out output/all_records.csv
```

#### Custom report path

```bash
endnote-utils \
  --xml data/Scopus.xml \
  --out output/scopus.csv \
  --report reports/scopus_run.txt \
  --stats \
  --verbose
```

If `--report` is not provided, it defaults to `<out>_report.txt`.
Use `--no-report` to disable report generation.

---

### CLI Options

| Option          | Description                                         | Default            |
| --------------- | --------------------------------------------------- | ------------------ |
| `--xml`         | Path to a single EndNote XML file                   | –                  |
| `--folder`      | Path to a folder containing multiple `*.xml` files  | –                  |
| `--csv`         | (Legacy) Output CSV path                            | –                  |
| `--out`         | Generic output path (`.csv`, `.json`, `.xlsx`)      | –                  |
| `--format`      | Explicit format (`csv`, `json`, `xlsx`)             | inferred           |
| `--report`      | Output TXT report path                              | `<out>_report.txt` |
| `--no-report`   | Disable TXT report completely                       | –                  |
| `--delimiter`   | CSV delimiter                                       | `,`                |
| `--quoting`     | CSV quoting: `minimal`, `all`, `nonnumeric`, `none` | `minimal`          |
| `--no-header`   | Suppress CSV header row                             | –                  |
| `--encoding`    | Output text encoding                                | `utf-8`            |
| `--ref-type`    | Only include records with this `ref_type` name      | –                  |
| `--year`        | Only include records with this year                 | –                  |
| `--max-records` | Stop after N records per file (for testing)         | –                  |
| `--dedupe`      | Deduplicate mode: `none`, `doi`, `title-year`       | `none`             |
| `--dedupe-keep` | Deduplication strategy: `first`, `last`             | `first`            |
| `--stats`       | Include summary stats in TXT report                 | –                  |
| `--stats-json`  | Path to JSON file to save stats & duplicate info    | –                  |
| `--verbose`     | Verbose logging with debug details                  | –                  |

---

### Example Report (snippet)

```
========================================
EndNote Export Report
========================================
Run started : 2025-09-11 14:30:22
Files       : 4
Duration    : 0.47 seconds

Per-file results
----------------------------------------
GGScholar.xml    : 13 exported, 0 skipped
IEEE.xml         : 2147 exported, 0 skipped
PubMed.xml       : 504 exported, 0 skipped
Scopus.xml       : 847 exported, 0 skipped
TOTAL exported: 3511

Duplicates table (by database)
----------------------------------------
Database        Origin   Retractions  Duplicates  Remaining
------------------------------------------------------------
GGScholar           179            0         27        152
IEEE               1900            0        589       1311
PubMed              320            0        225         95
Scopus             1999            1        511       1489
TOTAL              4410            1       1352       3047

Duplicate keys (top)
----------------------------------------
Mode   : doi
Keep   : first
Removed: 1352
Details (top):
  10.1109/SPMB55497.2022.10014965 : 3 duplicate(s)
  10.1109/TSSA63730.2024.10864368 : 2 duplicate(s)

Summary stats
----------------------------------------
By year:
   2022 : 569
   2023 : 684
   2024 : 1148
   2025 : 1108

By ref_type (top):
  Journal Article: 2037
  Conference Proceedings: 1470
  Book Section: 4

By journal (top 20):
  IEEE Access: 175
  IEEE Journal of Biomedical and Health Informatics: 67
  ...

Top authors (top 10):
  Y. Wang: 50
  X. Wang: 35
  ...
```

---

## Python API

```python
from pathlib import Path
from endnote_utils import export, export_folder

# Single file
total, out_file, report_file = export(
    Path("data/IEEE.xml"),
    Path("output/ieee.csv"),
    dedupe="doi", stats=True
)

# Folder
total, out_file, report_file = export_folder(
    Path("data/xmls"),
    Path("output/all.csv"),
    ref_type="Conference Proceedings",
    year="2024",
    dedupe="title-year",
    dedupe_keep="last",
    stats=True,
    stats_json=Path("output/stats.json"),
)
```

---

## Development Notes

* Pure Python, uses only standard library (`argparse`, `csv`, `xml.etree.ElementTree`, `logging`, `pathlib`, `json`).
* Optional dependency: `openpyxl` (for Excel `.xlsx` export).
* Streaming XML parsing avoids high memory usage.
* Deduplication strategies configurable (`doi` / `title-year`).
* Report includes per-database table and optional JSON snapshot.
* Follows [PEP 621](https://peps.python.org/pep-0621/) packaging (`pyproject.toml`).

---

## License

MIT License © 2025 Minh Quach