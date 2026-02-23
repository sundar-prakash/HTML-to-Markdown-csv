# html-to-markdown-csv

> Convert HTML product descriptions in CSV files to clean Markdown — with mojibake encoding repair, multi-column support, and guaranteed row preservation.

---

## ✨ Features

- 🔄 **HTML → Markdown** conversion via [`markdownify`](https://github.com/matthewwithanm/python-markdownify)
- 🛠️ **Mojibake repair** — automatically fixes double-encoded text (`Ã‚Â°` → `°`, `Ã¢â‚¬Ëœ` → `'`) caused by UTF-8 bytes misread as cp1252
- 📋 **Multi-column support** — convert one or many HTML columns in a single pass
- 🔢 **Exact row preservation** — blank/empty rows are kept exactly as-is (no silent skipping)
- 📦 **Input:** Windows-1252 encoded CSV → **Output:** UTF-8 CSV with CRLF line endings

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install markdownify
```

### 2. Configure the script

Edit the bottom of `convert.py`:

```python
INPUT_CSV    = 'prod_desc.csv'           # your input file
OUTPUT_CSV   = 'products_markdown.csv'   # where to write output
TARGET_COLUMNS = ['Description']         # one or more HTML column names
```

For **multiple columns**:

```python
TARGET_COLUMNS = ['short_description', 'long_description', 'Description']
```

### 3. Run

```bash
python convert.py
```

**Example output:**

```
📊 INPUT CSV ('prod_desc.csv') - Rows: 460 (Status: OK)
🎯 Target columns: ['Description', 'short_description']
✅ CONVERSION COMPLETE!
📊 OUTPUT CSV ('products_markdown.csv') - Rows: 460 (Status: OK)
🔍 ROW MATCH: ✅ PERFECT
   Input: 460 rows | Output: 460 rows
```

---

## 🧠 How It Works

### The Encoding Problem

Product CSVs exported from platforms like Shopify, WooCommerce, or custom ERPs often contain **mojibake** — garbled text created when UTF-8 encoded content is saved or read using the wrong encoding (cp1252/Windows-1252).

| Garbled | Fixed |
|--------|-------|
| `Ã‚Â°` | `°` |
| `Ã¢â‚¬ËœVibe with vybn!Ã¢â‚¬â„¢` | `'Vibe with vybn!'` |
| `Ã¢â‚¬â€™` | `'` |

The `fix_mojibake()` function applies up to **2 passes** of `encode('cp1252').decode('utf-8')` to unwind the double-encoding. Clean ASCII text is never modified.

### The Row Count Problem

Standard `csv.reader` with `newline=''` **overcounts rows** when unquoted fields contain bare `\r` characters (common in HTML content) — treating each `\r` as a row terminator. `csv.DictReader` silently **skips blank rows**. This script solves both by:

1. Splitting the raw file on `\r\n` at the **byte level** to get true logical lines
2. Processing each line individually through `csv.reader`
3. Writing empty lines back unchanged

This guarantees **input row count == output row count**, always.

---

## 📁 Project Structure

```
html-to-markdown-csv/
├── convert.py       # main script
└── README.md
```

---

## ⚙️ Requirements

- Python 3.7+
- [`markdownify`](https://pypi.org/project/markdownify/)

```bash
pip install markdownify
```

---

## 📝 License

MIT
