# ------------------------------------------------------------
# Use this file for single file debugging and creating all functionality
# When completed and found satisfactory, switch to multiprocessing for batch processing
# ------------------------------------------------------------
import os
from extract_neuropsych_form import extract_pdf_form_data, extract_sections, load_field_to_section_map
from ai_configuration_local import get_local_response
from ai_configuration_remote import get_remote_response
from ai_instructions import get_ai_instruction
import webbrowser
import os
from report_renderer import render_summary_html
from patient_details import get_patient_info

import pdb

# Read the source PDF file
fpath = '../../data/np_hx/patients/P1/Sample NP Hx Form - Reno.pdf'
filled_values = extract_pdf_form_data(fpath)
# pdb.set_trace()
patient_info = get_patient_info(filled_values)

# print(filled_values)
field_section_map = load_field_to_section_map()
# target_sections = ['Reason for Referral', 
#                    'Background Info Header', 
#                    'Concerns Prompting This Evaluation', 
#                    'Medical History', 
#                    'Birth & Development History',
#                    'School History',
#                    'Family History']

target_sections = ['Background Info Header', 
                   'Concerns Prompting This Evaluation', 
                   'Medical History', 
                   'Birth & Development History',
                   'School History',
                   'Family History']

extracted_data = extract_sections(filled_values, target_sections, field_section_map)

section_data = {}
for section in extracted_data:
    # result = get_local_response(get_ai_instruction(extracted_data[section]))
    result = get_remote_response(get_ai_instruction(extracted_data[section], section))
    section_data[section] = result

# Render the HTML page
render_summary_html(section_data, fpath, patient_info)