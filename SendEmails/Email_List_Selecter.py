"""
Build "Datasets\Emails\email list.csv" with randomized IDs
- Picks 100 generated IDs from GenEmails.json by id family Chat/Gemini/Grok/Sonar (01..25).
- Samples 100 PHISHING + 100 SAFE from zendoEmails.json by 'tag'.
- Combines and shuffles to 300 IDs.
- Overwrites "Datasets\Emails\email list.csv" each run.
"""
#import necessary libraries
import json
import re
import csv
import os
import time
import argparse
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Define file paths relative to this script's location
HERE = Path(__file__).resolve().parent
GEN_JSON = HERE / "Datasets\Emails\GenEmails.json"
ZENDO_JSON = HERE / "Datasets\Emails\zendoEmails.json"
OUT_CSV = HERE / "Datasets\Emails\email list.csv"

# Function to load JSON data, ensuring it's a list of dicts
def load_json_array(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list):
                return v
    raise ValueError(f"{path} is not a JSON list or a dict containing a list")

# Function to extract family and index from ID, e.g. "Chat01" -> ("chat", 1)
def family_index_from_id(raw_id: str) -> Tuple[str, int]:
    m = re.fullmatch(r"(Chat|Gemini|Grok|Sonar)0*(\d{1,3})", str(raw_id))
    if not m:
        return None, None
    return m.group(1).lower(), int(m.group(2))

# Select 100 generated IDs, prioritizing lower indices within each family
def select_generated_ids(gen_items: List[Dict[str, Any]]) -> List[str]:
    buckets = {"chat": [], "gemini": [], "grok": [], "sonar": []}
    # Group IDs by family and index
    for item in gen_items:
        rid = item.get("id") or item.get("ID") or item.get("Id")
        if not rid:
            continue
        fam, idx = family_index_from_id(rid)
        if fam and 1 <= idx <= 25:
            buckets[fam].append((idx, str(rid)))
    final_ids = []
    # For each family, sort by index and take the first 25
    for fam in ("sonar", "gemini", "grok", "chat"):
        picked = sorted(buckets[fam], key=lambda x: x[0])[:25]
        final_ids.extend([rid for _, rid in picked])
    if len(final_ids) != 100:
        print("Warning: expected 100 generated emails, found",
              len(final_ids), "; family candidates:",
              {k: len(v) for k, v in buckets.items()})
    return final_ids

# Select n IDs from zendo_items with a specific tag (PHISHING or SAFE)
def select_zendo_ids(zendo_items: List[Dict[str, Any]], tag_value: str, n: int, rng: random.Random) -> List[str]:
    # Filter items by tag (case-insensitive)
    pool = [x for x in zendo_items if str(x.get("tag", "")).upper() == tag_value.upper()]
    if len(pool) < n:
        raise ValueError(f"Requested {n} with tag {tag_value}, but only {len(pool)} available")
    chosen = rng.sample(pool, n)
    out = []
    # Extract IDs from chosen items
    for it in chosen:
        rid = it.get("id") or it.get("ID") or it.get("Id")
        if rid is not None:
            out.append(str(rid))
    return out

# Derive a seed for randomization, using user input or OS entropy + time
def derive_seed(user_seed: int | None) -> int:
    if user_seed is not None:
        return int(user_seed)
    # Mix OS entropy and time for variability across runs
    entropy = int.from_bytes(os.urandom(8), "big")
    return entropy ^ time.time_ns()

# Main function to orchestrate the selection and writing of email IDs
def main():
    # Set up argument parser for optional seed
    parser = argparse.ArgumentParser(description="Build randomized 'email list.csv'")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed for reproducible runs")
    args = parser.parse_args()

    master_seed = derive_seed(args.seed)
    rng = random.Random(master_seed)

    gen_items = load_json_array(GEN_JSON)
    zendo_items = load_json_array(ZENDO_JSON)

    ids_gen = select_generated_ids(gen_items)
    ids_phish = select_zendo_ids(zendo_items, "PHISHING", n=100, rng=rng)
    ids_safe = select_zendo_ids(zendo_items, "SAFE", n=100, rng=rng)

    all_ids = ids_gen + ids_phish + ids_safe
    rng.shuffle(all_ids)
    # Write the shuffled IDs to the output CSV file
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for eid in all_ids:
            w.writerow([eid])
    # Print summary of the operation
    print(f"Wrote {len(all_ids)} IDs to {OUT_CSV}")
    if args.seed is None:
        print(f"(Run was non-deterministic; master seed was {master_seed})")
    else:
        print(f"(Run was reproducible; master seed = {master_seed})")
# Execute main function
if __name__ == "__main__":
    main()

