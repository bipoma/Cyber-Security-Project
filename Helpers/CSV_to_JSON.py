#import necessary libraries
import csv
import json
from pathlib import Path

#Data loading
CSV_FILE = "Phishing_validation_emails.csv"
JSON_FILE = "ZendoEmails.json"

# Helper functions for ID generation and tag mapping
def make_id(n: int) -> str:
    # zendo00, zendo01, ..., zendo10, ...
    return f"zendo{n:02d}"

# Map raw email type to standardized tag
def map_tag(raw: str) -> str:
    raw = (raw or "").strip().lower()
    if raw == "safe email":
        return "SAFE"
    if raw == "phishing email":
        return "PHISHING"
    return raw.upper() or "UNKNOWN"

# Main function to read CSV, transform data, and write JSON
def main():
    json_path = Path(JSON_FILE)
    if not json_path.exists():
        print(f"No file found: {JSON_FILE}. Nothing written.")
        return
# Read CSV and transform to list of dicts for JSON output
    rows_out = []
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            rows_out.append({
                "id": make_id(i),
                "subject": "",
                "body": row.get("Email Text", "") or "",
                "tag": map_tag(row.get("Email Type", "")),
            })
# Write transformed data to JSON file
    with open(JSON_FILE, "w", encoding="utf-8") as out:
        json.dump(rows_out, out, indent=2, ensure_ascii=False)

# Execute main function
if __name__ == "__main__":
    main()
