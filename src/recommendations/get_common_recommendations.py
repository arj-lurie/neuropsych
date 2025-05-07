import os
import json
import re
from typing import List, Dict
import pdb

def read_file_with_fallback_encoding(file_path: str) -> str:
    """Try reading a file using UTF-8 and fallback to Windows-1252 if it fails."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="windows-1252") as f:
            return f.read()

def extract_json_from_file(file_path: str) -> dict:
    """Extract the JSON block without '$defs' from a markdown-style file with encoding fallback."""
    content = read_file_with_fallback_encoding(file_path)

    # Find all JSON blocks in triple-backtick format
    matches = re.findall(r"```json\s*({.*?})\s*```", content, re.DOTALL)

    if not matches:
        raise ValueError(f"No JSON blocks found in {file_path}")

    for json_str in matches:
        try:
            parsed = json.loads(json_str)
            if "$defs" not in parsed:
                return parsed
        except json.JSONDecodeError:
            continue

    raise ValueError(f"No valid JSON block without '$defs' found in {file_path}")

def extract_all_recommendations(folder_path: str) -> List[Dict[str, str]]:
    """Parse all files and collect all 'all_recommendations' with file info."""
    all_recs = []

    for filename in os.listdir(folder_path):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(folder_path, filename)        
        try:
            data = extract_json_from_file(path)
            print(path)
            themes = data.get("themes")
            if not isinstance(themes, list):
                print(f"No valid 'themes' in {filename}")
                continue

            for theme in themes:
                for rec in theme.get("all_recommendations", []):
                    all_recs.append({
                        "file": filename,
                        "recommendation": rec.strip()
                    })
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            raise

    return all_recs

folder_path = "./results"  # your folder path here
recommendation_data = extract_all_recommendations(folder_path)

# Optional: check how many and what kinds
print(f"Loaded {len(recommendation_data)} total recommendations from {len(set(r['file'] for r in recommendation_data))} files")
pdb.set_trace()

with open('recommendations.json', 'w', encoding='utf-8') as f:
    json.dump(recommendation_data, f, ensure_ascii=False, indent=2)
