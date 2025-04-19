# This file is used to process the spreadsheet that maps the neuropsych hx form variables to report sections
# Only run when that form is needed to be updated - otherwise, the JSON file is used directly
# ------------------------------------------------------------
import pandas as pd
import json
import re

def clean_value(val):
    if pd.isna(val):
        return None
    # Strip whitespace, quotes, and trailing commas
    val = str(val).strip()
    val = re.sub(r'^[\'"]+', '', val)  # leading quotes
    val = re.sub(r'[\'",\s]+$', '', val)  # trailing quotes, commas, spaces
    return val

def process_spreadsheet_to_json(file_path):
    df = pd.read_excel(file_path)

    df.columns = [col.strip() if isinstance(col, str) else "" for col in df.columns]
    expected_cols = ["Page/Section", "Variable", "Sub Variable", "Report Section", "Importance"]
    df = df.reindex(columns=expected_cols)

    result = {}
    current_report_section = None

    for _, row in df.iterrows():
        variable = clean_value(row["Variable"])
        sub_variable = clean_value(row["Sub Variable"])
        report_section = clean_value(row["Report Section"])

        if not variable and not sub_variable and not report_section:
            continue

        # Combine variable and sub_variable
        item = sub_variable or variable
        if not item:
            continue

        # Handle report sections (possibly multiple)
        if report_section:
            sections = [sec.strip() for sec in report_section.split(",")]
            current_report_section = sections
        elif current_report_section:
            sections = current_report_section
        else:
            sections = ["unclassified"]

        # Add to result
        for section in sections:
            if section not in result:
                result[section] = []
            if item not in result[section]:
                result[section].append(item)

    return result

# Example usage
if __name__ == "__main__":
    input_file = "../../data/np_hx/np_hx_forms/NP_Hx_FormField_ReportSection.xlsx"  # Replace with your actual file
    output_file = "field_to_section_map.json"

    data = process_spreadsheet_to_json(input_file)
    
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"JSON saved to {output_file}")
