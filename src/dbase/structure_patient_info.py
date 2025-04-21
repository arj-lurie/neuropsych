import json

# Function to read the master template from a JSON file
def read_master_template(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Function to map patient data to template
def map_patient_data_to_template(patient_data, template):
    mapped_data = {}

    for section, fields in template.items():
        mapped_section = {}
        
        for field in fields:
            # If the field exists in the patient_data dictionary, map it
            if field in patient_data:
                mapped_section[field] = patient_data[field]
            else:
                mapped_section[field] = None  # Assign None or an empty string if no data exists

        mapped_data[section] = mapped_section
    
    return mapped_data