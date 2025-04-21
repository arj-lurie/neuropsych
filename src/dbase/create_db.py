import json
from structure_patient_info import read_master_template, map_patient_data_to_template
from extract_neuropsych_form import extract_pdf_form_data
import os

# Path to your patient folders
PATIENTS_DIR = '../../data/np_hx/patients'
TEMPLATE_PATH = '../mapping/field_to_section_map.json'

# Read the template once
template_structure = read_master_template(TEMPLATE_PATH)

# Collect all mapped patient data
all_patients_data = []

# Loop through patient subdirectories
for patient_folder in sorted(os.listdir(PATIENTS_DIR)):
    folder_path = os.path.join(PATIENTS_DIR, patient_folder)

    if os.path.isdir(folder_path):
        # Assume a single PDF per folder
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        if not pdf_files:
            print(f"No PDF found in {folder_path}")
            continue

        pdf_path = os.path.join(folder_path, pdf_files[0])
        print(f"Processing {pdf_path}...")

        try:
            # Extract, map and store the data
            patient_data = extract_pdf_form_data(pdf_path)
            mapped_data = map_patient_data_to_template(patient_data, template_structure)
            all_patients_data.append({
                'patient_id': patient_folder,
                'mapped_data': mapped_data
            })
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")

# Optionally: Save to a file
output_dir = './output'
os.makedirs(output_dir, exist_ok=True)
with open('./output/all_patients_mapped.json', 'w') as f:
    json.dump(all_patients_data, f, indent=4)

print(f"\n✅ Processed {len(all_patients_data)} patients.")