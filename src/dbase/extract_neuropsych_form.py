# ------------------------------------------
# This is a support / utility function file.
# Ideally we'd structure this to be a larger module for use across multiple projects
# ------------------------------------------
from pdfrw import PdfReader
import pdb

def extract_pdf_form_data(pdf_path):
    # Read the PDF file
    pdf = PdfReader(pdf_path)

    # Initialize a dictionary to store form field names and their values
    form_data = {}

    # Loop through each page to extract the form fields
    for page in pdf.pages:
        annotations = page['/Annots']
        if annotations:
            for annotation in annotations:
                field = annotation.get('/T')
                value = annotation.get('/V')
                if field and value:
                    form_data[field[1:-1]] = value[1:-1]  # Remove leading/trailing brackets

    return form_data
    
import json

# Load mapping from the JSON file
def load_field_to_section_map(path='field_to_section_map.json'):
    with open(path, 'r') as file:
        return json.load(file)

# Invert the mapping to map field names back to section
def invert_mapping(section_map):
    return {
        field: section
        for section, fields in section_map.items()
        for field in fields
    }

# Extract a specific section from filled_values
def extract_specific_section(filled_values, target_section, section_map):    
    return {
        key: filled_values[key]
        for key in section_map.get(target_section, [])
        if key in filled_values
    }

# Extract all relevant sections
def extract_sections(filled_values, target_sections, section_map):
    extracted = {}
    for section in target_sections:
        extracted[section] = extract_specific_section(filled_values, section, section_map)
    return extracted