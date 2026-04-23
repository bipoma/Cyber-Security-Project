#import necessary libraries
import csv
import json

#Data loading
INPUT_CSV = "Datasets\Emails\email list.csv"
OUTPUT_JSON = "Datasets\Emails\SPAMorNOT.json"
GEN_JSON = "Datasets\Emails\GenEmails.json"
ZENDO_JSON = "Datasets\Emails\zendoEmails.json"

# Helper function to load JSON data into a dictionary keyed by lowercase ID
def load_id_data_map(filename):
    """
    Load JSON file containing a list of objects and return:
    {
        id_lower: {
            "tag": str,
            "subject": str,
            "body": str
        }
    }
    """
    # If file doesn't exist, return empty dict
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Validate that data is a list of dicts
    if not isinstance(data, list):
        raise ValueError(f"{filename} must contain a list of objects")

    id_map = {}
    # Process each entry, ensuring it has an 'id' field and is a dict
    for entry in data:
        if not isinstance(entry, dict):
            continue

        entry_id = entry.get("id")
        if not entry_id:
            continue

        id_map[entry_id.strip().lower()] = {
            "tag": str(entry.get("tag", "")).strip(),
            "subject": str(entry.get("subject", "")).strip(),
            "body": str(entry.get("body", "")).strip(),
        }

    return id_map

# Main function to read CSV, merge with JSON data, and write output JSON
def main():
    # Load reference data
    gen_map = load_id_data_map(GEN_JSON)
    zendo_map = load_id_data_map(ZENDO_JSON)

    # Merge (zendo overrides gen)
    combined_map = {**gen_map, **zendo_map}

    output = []
    # Read CSV and create output entries, using combined_map for tag/subject/body
    with open(INPUT_CSV, "r", encoding="utf-8", newline="") as infile:
        reader = csv.reader(infile)
        for row in reader:
            if not row:
                continue

            email_id = row[0].strip()
            if not email_id:
                continue

            data = combined_map.get(email_id.lower())

            if data:
                entry = {
                    "id": email_id,
                    "tag": data["tag"] if data["tag"] else "UNKNOWN",
                    "subject": data["subject"],
                    "body": data["body"],
                }
            else:
                entry = {
                    "id": email_id,
                    "tag": "UNKNOWN",
                    "subject": "",
                    "body": "",
                }

            output.append(entry)
    # Write output to JSON file
    with open(OUTPUT_JSON, "w", encoding="utf-8") as outfile:
        json.dump(output, outfile, indent=2, ensure_ascii=False)

    print(f"Processed {len(output)} entries")
    print(f"Output written to {OUTPUT_JSON}")

# Execute main function
if __name__ == "__main__":
    main()
