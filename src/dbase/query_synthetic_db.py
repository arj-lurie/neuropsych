import json
import pandas as pd
import os
import pdb


# Step 1: Load all possible keys from the JSON file
def load_available_keys(json_file):
    with open(json_file, 'r') as f:
        available_keys = json.load(f)
    
    # Flatten the available keys dictionary to get only the field names (values of the dictionary)
    flat_keys = []
    for category, fields in available_keys.items():
        flat_keys.extend(fields)
    
    return flat_keys

# Step 2: Load synthetic patient data from JSON files in a directory
def load_patient_data(data_dir):
    patients = []
    
    # Loop through the folders and load the patient data from form.json files
    for folder in os.listdir(data_dir):
        form_path = os.path.join(data_dir, folder, "form.json")
        if not os.path.isfile(form_path):
            continue
        
        with open(form_path, "r") as f:
            data = json.load(f)
        
        data['patient_id'] = folder
        patients.append(data)
    
    df = pd.DataFrame(patients)  # Convert the list of patient data to a DataFrame
    return df

# Step 3: Query the data based on exact matches of user query
def query_data(query, df, available_keys):
    # Split the query into individual field names (if comma-separated)
    query_fields = [field.strip() for field in query.split(',')]
    
    # For each query field, check if it exists in the available keys and if it exists in the DataFrame
    for query_field in query_fields:
        if query_field in available_keys:
            if query_field in df.columns:
                query_result = df[df[query_field] == True]
                print(f"Number of patients with '{query_field}' = {len(query_result)}")
            else:
                print(f"Key '{query_field}' does not exist in the data.")
        else:
            print(f"Key '{query_field}' is not available in the list of fields.")

def query_data_intersection(query, df, available_keys):
    # Split and clean up the query fields
    query_fields = [field.strip() for field in query.split(',')]

    # Check each field
    missing_keys = [field for field in query_fields if field not in available_keys]
    for field in missing_keys:
        print(f"⚠️ Key '{field}' is not available in the list of fields.")

    # Proceed only with valid keys
    valid_fields = [field for field in query_fields if field in available_keys and field in df.columns]

    if not valid_fields:
        print("❌ No valid fields found in query.")
        return

    # Filter the DataFrame where all valid fields are True
    filtered_df = df.copy()
    for field in valid_fields:
        filtered_df = filtered_df[filtered_df[field] == True]

    print(f"✅ Number of patients matching **all** of these fields: {len(filtered_df)}")

def query_data_advanced(query, df, available_keys, return_ids=False):
    import re

    query = query.strip()
    clauses = []
    # pdb.set_trace()
    # OR logic in parentheses
    or_blocks = re.findall(r'\((.*?)\)', query)
    for block in or_blocks:
        or_fields = [field.strip() for field in block.split('OR')]
        clauses.append({'type': 'OR', 'fields': or_fields})
        query = query.replace(f"({block})", "")

    # Remaining fields are ANDs
    and_fields = [field.strip() for field in query.split(',') if field.strip()]
    for field in and_fields:
        clauses.append({'type': 'AND', 'fields': [field]})

    filtered_df = df.copy()

    for clause in clauses:
        valid_fields = [f for f in clause['fields'] if f in available_keys and f in df.columns]

        if not valid_fields:
            print(f"⚠️ No valid fields in clause: {clause['fields']}")
            return

        if clause['type'] == 'AND':
            for field in valid_fields:
                filtered_df = filtered_df[filtered_df[field] == True]
        elif clause['type'] == 'OR':
            condition = filtered_df[valid_fields].any(axis=1)
            filtered_df = filtered_df[condition]

    if 'patient_id' in filtered_df.columns:
        patient_ids = filtered_df['patient_id'].tolist()
    else:
        print("⚠️ 'patient_id' column not found. Cannot infer patient IDs.")
        patient_ids = filtered_df.index.tolist()

    print(f"✅ {len(filtered_df)} patient(s) match the query.")
    if return_ids:
        print("🆔 Matching patient IDs:", patient_ids)

    return patient_ids if return_ids else None

# Load your available keys (from JSON)
json_file = '../mapping/field_to_section_map.json'  # Replace with the path to your JSON
available_keys = load_available_keys(json_file)

# Load your synthetic data
data_dir = '../../data/np_hx/synthetic_patients'  # Replace with the path to your data folder
df = load_patient_data(data_dir)

# -------------------------------------------------
# Query Logic Rules:
# -------------------------------------------------
# "A, B, C" → A AND B AND C
# "A, (B OR C), D" → A AND (B OR C) AND D
# "A, (B OR C OR D)" → A AND (any of B, C, or D)
# ** Use comma for AND, parentheses with OR is for (any of)

# # Example of how to query the data
# query_1 = "Pt Ethnicity Hispanic Yes, Med Hx Brain Tumor or Cancer, Imm Fam Cancer"  # All three conditions
# query_2 = "(Imm Fam Cancer OR Ext Fam Cancer)"

# # Returns each of the conditions individually - simple querrying where you want each condition separately
# query_data(query_1, df, available_keys)
# print ('*******************************************')
# # Example of how to query the data with advanced logic:
# query_data_advanced(query_1, df, available_keys, return_ids=True)
# print ('*******************************************')
# query_data_advanced(query_2, df, available_keys, return_ids=True)
# print ('*******************************************')

# List of queries to run
queries = [
    ("Med Hx Brain Tumor or Cancer, Imm Fam Cancer", "query_1"),
    ("Med Hx Sickle Cell Disease, Med Hx Stroke or CVA, Academic Services IEP", "query_2"),
    ("Med Hx Epilepsy or Seizure DO, Related School Services OT", "query_3"),
    ("Med Hx Epilepsy or Seizure DO, Related School Services PT", "query_4")
]

# Loop through each query
for query, query_name in queries:
    print(f"Running {query_name}...")
    patient_ids = query_data_advanced(query, df, available_keys, return_ids=True)
    
    # Print the results
    # print(f"Results for {query_name}:")
    # print(patient_ids)
    print('*******************************************')