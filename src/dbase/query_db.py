import pdb

import json
import os

def list_referring_providers_from_template(patients_data, template_structure, target_fields):
    # Ensure target_fields is a list of stripped strings
    target_fields = [field.strip() for field in target_fields]

    # Step 1: Find which section(s) contain any of the target fields
    target_sections = [
        section for section, fields in template_structure.items()
        if any(f.strip() in target_fields for f in fields)
    ]

    providers = []

    # Step 2: Search through all patients and check the fields directly
    for patient in patients_data:
        if 'mapped_data' in patient:  # Ensure 'mapped_data' exists in patient
            mapped_data = patient['mapped_data']
            patient_id = patient.get("patient_id")
            processed_fields = set()  # Track processed target fields for this patient

            for section in target_sections:
                if section in mapped_data:  # Check if section exists in 'mapped_data'
                    section_data = mapped_data[section]
                    for field in template_structure[section]:
                        stripped_field = field.strip()

                        # Only process if the field is in target_fields and hasn't been processed for this patient
                        if stripped_field in target_fields and stripped_field not in processed_fields:
                            if stripped_field in section_data:
                                provider = section_data.get(stripped_field)
                                if provider:
                                    providers.append((patient_id, provider.strip()))
                                    processed_fields.add(stripped_field)  # Mark this field as processed

    return providers

# For quick standalone testing
if __name__ == '__main__':
    with open('./output/all_patients_mapped.json') as f:
        patients_data = json.load(f)

    with open('../mapping/field_to_section_map.json') as f:
        template_structure = json.load(f)
    
    # ------------------------------------------------------------
    # Use this to extract data for research purposes
    # ------------------------------------------------------------
    target_fields = ["Newborn Difficulties Hydrocephalus"]
    providers = list_referring_providers_from_template(patients_data, template_structure, target_fields)

    print("Requested Data:")
    for p in providers:
        print("-", p)
