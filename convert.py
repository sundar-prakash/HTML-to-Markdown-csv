import csv
import io
from markdownify import markdownify as md
import os


def count_csv_rows(file_path, encoding='windows-1252'):
    """
    Count rows by splitting on CRLF at the raw byte level, then removing only
    the trailing empty line (EOF). This preserves intentional empty/blank rows
    and is not fooled by bare \r inside unquoted field content.
    """
    if not os.path.exists(file_path):
        return 0, "File not found"
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        lines = content.split(b'\r\n')
        if lines and lines[-1] == b'':
            lines = lines[:-1]  # strip trailing EOF empty line only
        return len(lines), "OK"
    except Exception as e:
        return 0, f"Error: {e}"


def fix_mojibake(text, passes=2):
    """
    Fix double-encoded (mojibake) text where UTF-8 bytes were misread as cp1252.
    e.g. 'Ã¢â‚¬Ëœ' -> '\u2018' (left single quote), 'Ã‚Â°' -> '°'
    Applies up to `passes` rounds since some text is double-mangled.
    Clean ASCII text passes through unchanged.
    """
    for _ in range(passes):
        try:
            fixed = text.encode('cp1252').decode('utf-8')
            if fixed == text:
                break  # no change, already clean
            text = fixed
        except (UnicodeEncodeError, UnicodeDecodeError):
            break  # can't fix further, return what we have
    return text


def convert_html_csv_to_md(input_file, output_file, column_names):
    """
    Reads a CSV, converts specified columns' HTML to Markdown, fixes encoding
    mojibake, and writes a new CSV. Preserves ALL rows including blank rows.

    Args:
        input_file:   Path to input CSV (Windows-1252 encoded)
        output_file:  Path to output CSV (UTF-8)
        column_names: List of column names to convert (e.g. ['Description', 'short_description'])
    """
    if isinstance(column_names, str):
        column_names = [column_names]  # allow passing a single string too

    input_rows, input_status = count_csv_rows(input_file, encoding='windows-1252')
    print(f"📊 INPUT CSV ('{input_file}') - Rows: {input_rows} (Status: {input_status})")
    print(f"🎯 Target columns: {column_names}")

    try:
        with open(input_file, 'rb') as f:
            raw_content = f.read()

        lines = raw_content.split(b'\r\n')
        if lines and lines[-1] == b'':
            lines = lines[:-1]  # remove trailing EOF newline only

        out_lines = []
        col_indices = {}  # {column_name: index}

        for i, line_bytes in enumerate(lines):
            # Preserve empty rows exactly as-is
            if line_bytes == b'':
                out_lines.append(b'')
                continue

            line_str = line_bytes.decode('windows-1252')

            # Parse this single line as a CSV row
            row = next(csv.reader(io.StringIO(line_str)))

            if i == 0:
                # Header row — find all target column indices
                for col in column_names:
                    if col not in row:
                        print(f"⚠️  Warning: Column '{col}' not found in CSV. Available: {row}")
                    else:
                        col_indices[col] = row.index(col)
                out_lines.append(line_bytes)  # write header unchanged
                continue

            if not col_indices:
                print("Error: None of the target columns were found. Aborting.")
                return

            # Process each target column
            for col, idx in col_indices.items():
                if idx < len(row):
                    html_content = row[idx]
                    if html_content.strip():
                        # Step 1: Fix mojibake encoding corruption
                        html_content = fix_mojibake(html_content)
                        # Step 2: Convert HTML -> Markdown
                        converted = md(html_content, heading_style="ATX").strip()
                        # Step 3: Normalize line endings (bare \r corrupts CSV rows)
                        converted = converted.replace('\r\n', '\n').replace('\r', '\n')
                        row[idx] = converted

            # Re-encode the row as a fully-quoted CSV line in UTF-8
            buf = io.StringIO()
            writer = csv.writer(buf, quoting=csv.QUOTE_ALL)
            writer.writerow(row)
            encoded_line = buf.getvalue().rstrip('\r\n').encode('utf-8')
            out_lines.append(encoded_line)

        # Write output with CRLF line endings (standard for CSV)
        with open(output_file, 'wb') as f:
            f.write(b'\r\n'.join(out_lines) + b'\r\n')

        output_rows, output_status = count_csv_rows(output_file, encoding='utf-8')
        print(f"✅ CONVERSION COMPLETE!")
        print(f"📊 OUTPUT CSV ('{output_file}') - Rows: {output_rows} (Status: {output_status})")

        match_status = '✅ PERFECT' if input_rows == output_rows else '❌ MISMATCH!'
        print(f"🔍 ROW MATCH: {match_status}")
        print(f"   Input: {input_rows} rows | Output: {output_rows} rows")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"An error occurred: {e}")


# --- Configuration ---
INPUT_CSV = '/mnt/user-data/uploads/prod_desc.csv'
OUTPUT_CSV = '/mnt/user-data/outputs/products_markdown.csv'

# ✅ List all HTML columns you want converted — handles one or many
TARGET_COLUMNS = ['Description']  # e.g. ['Description', 'short_description', 'long_description']

if __name__ == "__main__":
    os.makedirs('/mnt/user-data/outputs', exist_ok=True)
    convert_html_csv_to_md(INPUT_CSV, OUTPUT_CSV, TARGET_COLUMNS)
