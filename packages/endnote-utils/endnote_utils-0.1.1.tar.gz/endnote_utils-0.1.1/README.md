# EndNote Utils

Convert **EndNote XML files** into clean CSVs with automatic TXT reports.  
Supports both **Python API** and **command-line interface (CLI)**.

---

## Features

- ✅ Parse one XML file (`--xml`) or an entire folder of `*.xml` (`--folder`)
- ✅ Streams `<record>` elements using `iterparse` (low memory usage)
- ✅ Extracts fields:  
  `database, ref_type, title, journal, authors, year, volume, number, abstract, doi, urls, extracted_date`
- ✅ Adds a `database` column from the XML filename stem (`IEEE.xml → IEEE`)
- ✅ Normalizes DOI (`10.xxxx` → `https://doi.org/...`)
- ✅ Always generates a **TXT report** (default: `<csv>_report.txt`) with:
  - per-file counts (exported/skipped records)  
  - totals, files processed  
  - run timestamp & duration
- ✅ Auto-creates output folders if missing
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
endnote-utils --xml data/IEEE.xml --csv output/ieee.csv
```

#### Folder with multiple files

```bash
endnote-utils --folder data/xmls --csv output/all_records.csv
```

#### Custom report path

```bash
endnote-utils \
  --xml data/Scopus.xml \
  --csv output/scopus.csv \
  --report reports/scopus_run.txt
```

If `--report` is not provided, it defaults to `<csv>_report.txt`.

---

### CLI Options

| Option          | Description                                         | Default            |
| --------------- | --------------------------------------------------- | ------------------ |
| `--xml`         | Path to a single EndNote XML file                   | –                  |
| `--folder`      | Path to a folder containing multiple `*.xml` files  | –                  |
| `--csv`         | Output CSV path                                     | –                  |
| `--report`      | Output TXT report path                              | `<csv>_report.txt` |
| `--delimiter`   | CSV delimiter                                       | `,`                |
| `--quoting`     | CSV quoting: `minimal`, `all`, `nonnumeric`, `none` | `minimal`          |
| `--no-header`   | Suppress CSV header row                             | –                  |
| `--encoding`    | Output CSV encoding                                 | `utf-8`            |
| `--ref-type`    | Only include records with this `ref_type` name      | –                  |
| `--year`        | Only include records with this year                 | –                  |
| `--max-records` | Stop after N records per file (useful for testing)  | –                  |
| `--verbose`     | Verbose logging with debug details                  | –                  |

---

### Example Report

```
Run started: 2025-09-11 14:30:22
IEEE.xml: 120 exported, 0 skipped
Scopus.xml: 95 exported, 2 skipped
TOTAL exported: 215
Files processed: 2
Duration: 3.14 seconds
```

---

## Python API

You can also use it directly in Python scripts:

```python
from pathlib import Path
from endnote_utils import export, export_folder

# Single file
total, csv_out, report_out = export(
    Path("data/IEEE.xml"), Path("output/ieee.csv")
)

# Folder
total, csv_out, report_out = export_folder(
    Path("data/xmls"), Path("output/all.csv"),
    ref_type="Conference Proceedings", year="2024"
)
```

---

## Development Notes

* Pure Python, uses only standard library (`argparse`, `csv`, `xml.etree.ElementTree`, `logging`, `pathlib`).
* Streaming XML parsing avoids high memory usage.
* Robust error handling: skips malformed records but logs them in verbose mode.
* Follows [PEP 621](https://peps.python.org/pep-0621/) packaging (`pyproject.toml`).

---

## License

MIT License © 2025 Minh Quach