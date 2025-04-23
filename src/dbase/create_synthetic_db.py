import os
import json
import random
import re
import pandas as pd
from collections import defaultdict
import pdb

# --------------------------------------------------
# === SETTINGS ===
OUTPUT_DIR = "../../data/np_hx/synthetic_patients"
EXCEL_CONFIG = "../../data/np_hx/synthetic_patients/requirements/synthetic_data_config.xlsx"
TOTAL_PATIENTS = 100  # Note: rounded integers are used when scaling, so you might occasionally get slight mismatch totals. 
# --------------------------------------------------
# === DEFINE MUTUALLY EXCLUSIVE GROUPS ===
MUTUALLY_EXCLUSIVE_GROUPS = [
    # Sex
    ["Pt Sex Male", "Pt Sex Female", "Pt Sex Unknown", "Pt Sex Other"],

    # Ethnicity
    ["Pt Ethnicity Hispanic Yes", "Pt Ethnicity Hispanic No", "Pt Ethnicity Hispanic Unknown"],

    # Newborn Difficulties
    ["Newborn Difficulties Yes", "Newborn Difficulties No"],

    # Pregnancy Concerns
    ["Pregnancy Concerns Yes", "Pregnancy Concerns No"],

    # School Type
    ["School Type Public", "School Type Parochial", "School Type Private", "School Type Homeschool"],

    # Race
    [
        "Pt Race White",
        "Pt Race Middle Eastern",
        "Pt Race Not Listed",
        "Pt Race Black",
        "Pt Race Pacific Islander",
        "Pt Race Indigenous",
        "Pt Race Asian",
        "Pt Race Indigenous Nation Text",
        "Pt Race Not Listed Text"
    ]
]
# --------------------------------------------------
def percentify_config(flat_config, total_from_config):
    percent_config = []
    for field, count in flat_config:
        if isinstance(count, int):
            percent = count / total_from_config
            percent_config.append((field, percent))
        else:
            # For ranges or other string-based values
            percent_config.append((field, count))
    return percent_config

def scale_config(percent_config, total_patients):
    scaled = []
    for field, pct in percent_config:
        if isinstance(pct, float):
            scaled_count = int(round(pct * total_patients))
            scaled.append((field, scaled_count))
        else:
            scaled.append((field, pct))  # e.g., for "10-20" type fields
    return scaled

# === LOAD AND CLEAN CONFIG ===
def load_and_prepare_config(path, skiprows=2):
    df = pd.read_excel(path, skiprows=skiprows)
    df.fillna("", inplace=True)

    flat_config = []

    for _, row in df.iterrows():
        variable = str(row["Variable"]).strip().strip('"')
        value = str(row["n"]).strip().strip('"')
        count = row["count"]

        if not variable and not value:
            continue

        # Handle missing or invalid count
        if count == "" or pd.isna(count):
            count = 0
        elif isinstance(count, (int, float)):
            count = int(count)
        else:
            count = str(count).strip()

        field = value if value else variable
        flat_config.append([field, count])

    # Now return the raw flat_config which is already proportional to 100 patients
    deduped_config = deduplicate_config(flat_config)
    return deduped_config

def deduplicate_config(flat_config):
    from collections import defaultdict
    aggregated = defaultdict(int)
    range_fields = {}

    for field, count in flat_config:
        if isinstance(count, int):
            aggregated[field] += count
        elif isinstance(count, str) and re.match(r"\d+\s*-\s*\d+", count):
            range_fields[field] = count
        else:
            aggregated[field] += 1

    final = [[field, count] for field, count in aggregated.items()]
    final += [[field, rng] for field, rng in range_fields.items()]
    return final

# === GENERATION ===
patients = [defaultdict(lambda: None) for _ in range(TOTAL_PATIENTS)]

def get_random_indexes(count):
    return random.sample(range(TOTAL_PATIENTS), int(count))

def apply_config_with_full_coverage(config_data, mutually_exclusive_groups):
    config_map = dict(config_data)

    # Prepare reverse lookup from field to group
    field_to_group = {}
    for group in mutually_exclusive_groups:
        for field in group:
            field_to_group[field] = group

    # Initialize a list to track unassigned patient indexes per group
    available_patients = set(range(TOTAL_PATIENTS))

    # Apply mutually exclusive fields group by group
    for group in mutually_exclusive_groups:
        group_counts = {field: config_map.get(field, 0) for field in group}
        total_in_group = sum(int(count) for count in group_counts.values())

        # Auto-adjust if underassigned (optional)
        if total_in_group < TOTAL_PATIENTS:
            fallback = next((f for f in group if "Unknown" in f), group[-1])
            group_counts[fallback] += (TOTAL_PATIENTS - total_in_group)

        # Shuffle to randomize assignment
        patient_indexes = list(available_patients)
        random.shuffle(patient_indexes)
        idx = 0

        for field, count in group_counts.items():
            for _ in range(int(count)):
                if idx >= len(patient_indexes):
                    break
                i = patient_indexes[idx]
                patients[i][field] = True
                idx += 1

def apply_remaining_config(config_data, mutually_exclusive_groups):
    exclusive_fields = set(f for group in mutually_exclusive_groups for f in group)

    for field, count in config_data:
        if field in exclusive_fields:
            continue  # already handled by full coverage

        if isinstance(count, str) and re.match(r"\d+\s*-\s*\d+", count):
            low, high = map(int, re.findall(r"\d+", count))
            for patient in patients:
                patient[field] = str(random.randint(low, high))

        elif isinstance(count, int) and count > 0:
            for i in get_random_indexes(count):
                patients[i][field] = True

# === SAVE JSON FILES ===
def save_patient_jsons(patients, base_dir=OUTPUT_DIR):
    os.makedirs(base_dir, exist_ok=True)
    for i, patient in enumerate(patients, start=1):
        folder = os.path.join(base_dir, f"P{i}")
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "form.json"), "w") as f:
            # pdb.set_trace()
            json.dump(patient, f, indent=2)
    print(f"✅ Done! Created {len(patients)} patient folders in '{base_dir}'")

# === VALIDATION ===
def verify_synthetic_data(config_data, mutually_exclusive_groups, data_dir=OUTPUT_DIR):
    actual_counts = defaultdict(int)
    total_patients = 0
    exclusivity_violations = []

    for folder in os.listdir(data_dir):
        form_path = os.path.join(data_dir, folder, "form.json")
        if not os.path.isfile(form_path):
            continue
        total_patients += 1

        with open(form_path, "r") as f:
            data = json.load(f)

        # Count actuals
        for field, expected in config_data:
            value = data.get(field)
            if isinstance(expected, int):
                if value is True:
                    actual_counts[field] += 1
            elif isinstance(expected, str) and re.match(r"\d+\s*-\s*\d+", expected):
                try:
                    val = int(value)
                    low, high = map(int, re.findall(r"\d+", expected))
                    if low <= val <= high:
                        actual_counts[field] += 1
                except Exception:
                    pass

        # Check exclusivity violations
        for group in mutually_exclusive_groups:
            set_fields = [f for f in group if data.get(f) is True]
            if len(set_fields) > 1:
                exclusivity_violations.append((folder, set_fields))

    # Print validation report
    print(f"\n✅ Validation Report for {total_patients} patient files:\n")
    for field, expected in config_data:
        actual = actual_counts.get(field, 0)
        if isinstance(expected, int):
            print(f"🧪 {field}: expected {expected}, actual {actual} → {'✅' if actual == expected else '❌'}")
        elif isinstance(expected, str) and re.match(r"\d+\s*-\s*\d+", expected):
            print(f"🧪 {field} (range {expected}): valid values in {actual}/{total_patients} forms")

    if exclusivity_violations:
        print(f"\n❌ Found {len(exclusivity_violations)} mutual exclusivity violations:")
        for folder, fields in exclusivity_violations[:5]:  # limit preview
            print(f" - {folder}: {fields}")
    else:
        print("\n✅ No exclusivity violations found.")

    print("\n✔️  Done verifying.\n")

def validate_missing_from_groups(patients, mutually_exclusive_groups):
    print("\n🔍 Checking for patients with missing values from exclusive groups...\n")
    for i, patient in enumerate(patients, start=1):
        for group in mutually_exclusive_groups:
            group_str = ', '.join(group)
            # pdb.set_trace()
            if not any(patient.get(f) is True for f in group):
                print(f"⚠️ Patient P{i} missing assignment for group: {group_str}")

    print("\n✔️  Validity check complete.\n")


# --------------------------------------------------
# === CREATE SYNTHETIC DATA ===
# --------------------------------------------------
raw_config = load_and_prepare_config(EXCEL_CONFIG)
# pdb.set_trace()
percent_config = percentify_config(raw_config, 100)
config_data = scale_config(percent_config, TOTAL_PATIENTS)

patients = [defaultdict(lambda: None) for _ in range(TOTAL_PATIENTS)]
apply_config_with_full_coverage(config_data, MUTUALLY_EXCLUSIVE_GROUPS)
apply_remaining_config(config_data, MUTUALLY_EXCLUSIVE_GROUPS)
save_patient_jsons(patients)
verify_synthetic_data(config_data, MUTUALLY_EXCLUSIVE_GROUPS)
validate_missing_from_groups(patients, MUTUALLY_EXCLUSIVE_GROUPS)