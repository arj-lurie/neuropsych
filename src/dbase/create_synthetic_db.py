import os
import json
import random
import re
import pandas as pd
from collections import defaultdict
import pdb

# === SETTINGS ===
TOTAL_PATIENTS = 100
OUTPUT_DIR = "../../data/np_hx/synthetic_patients"
EXCEL_CONFIG = "../../data/np_hx/synthetic_patients/requirements/synthetic_data_config.xlsx"

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

        # Parse count
        if count == "" or pd.isna(count):
            count = 0
        elif isinstance(count, (int, float)):
            count = int(count)
        else:
            count = str(count).strip()

        field = value if value else variable
        flat_config.append([field, count])

    return deduplicate_config(flat_config)

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

def apply_config_with_exclusivity(config_data, mutually_exclusive_groups):
    field_to_group = {}
    for group in mutually_exclusive_groups:
        for field in group:
            field_to_group[field] = tuple(group)

    for field, count in config_data:
        if isinstance(count, str) and re.match(r"\d+\s*-\s*\d+", count):
            low, high = map(int, re.findall(r"\d+", count))
            for patient in patients:
                patient[field] = str(random.randint(low, high))

        elif isinstance(count, int):
            if count == 0:
                continue
            indexes = get_random_indexes(count)
            group = field_to_group.get(field)

            for i in indexes:
                if group:
                    if any(patients[i].get(f) is True for f in group):
                        continue  # skip if any other in group already set
                patients[i][field] = True

# === SAVE JSON FILES ===
def save_patient_jsons(patients, base_dir=OUTPUT_DIR):
    os.makedirs(base_dir, exist_ok=True)
    for i, patient in enumerate(patients, start=1):
        folder = os.path.join(base_dir, f"P{i}")
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "form.json"), "w") as f:
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

    print("\n✔️ Done verifying.\n")

# def validate_missing_from_groups(patients, mutually_exclusive_groups):
#     print("\n🔍 Checking for patients with missing values from exclusive groups...\n")
#     for i, patient in enumerate(patients, start=1):
#         for group in mutually_exclusive_groups:
#             group_str = ', '.join(group)
#             pdb.set_trace()
#             if not any(patient.get(f) is True for f in group):
#                 print(f"⚠️ Patient P{i} missing assignment for group: {group_str}")

# === RUN EVERYTHING ===
config_data = load_and_prepare_config(EXCEL_CONFIG)
apply_config_with_exclusivity(config_data, MUTUALLY_EXCLUSIVE_GROUPS)
save_patient_jsons(patients)
verify_synthetic_data(config_data, MUTUALLY_EXCLUSIVE_GROUPS)
# validate_missing_from_groups(patients, MUTUALLY_EXCLUSIVE_GROUPS)