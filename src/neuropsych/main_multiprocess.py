# Use this file for multiporcessing of several filesimport os
import multiprocessing
from pathlib import Path
from extract_neuropsych_form import extract_pdf_form_data, extract_sections, load_field_to_section_map
from ai_configuration_local import get_local_response
from ai_configuration_remote import get_remote_response
from ai_instructions import get_ai_instruction
from report_renderer import render_summary_html
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import time

# Root folder to search for PDFs
ROOT_DIR = Path('../../data/np_hx/patients')
TARGET_SECTIONS = ['Background Information', 'Birth and Developmental History']

# -----------------------------------------------------------------------
# Parallelize each section of the report. Since this function involves making a remote API call, which is likely I/O-bound 
# (and potentially slow due to network latency), parallelizing this function using threading would work well to speed things up.
# -----------------------------------------------------------------------
def process_pdf(fpath):
    start_time = time.time()
    try:
        filled_values = extract_pdf_form_data(fpath)
        field_section_map = load_field_to_section_map()
        extracted_data = extract_sections(filled_values, TARGET_SECTIONS, field_section_map)

        section_data = {}

        # Create a ThreadPoolExecutor for concurrent calls to get_remote_response
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_section = {
                executor.submit(get_remote_response, get_ai_instruction(data)): section
                for section, data in extracted_data.items()
            }

            # Process the results in the order of the original sections
            for section in extracted_data:
                future = future_to_section.popitem()[0]  # Pop the future for each section in order
                try:
                    result = future.result()
                    section_data[section] = result
                except Exception as e:
                    section_data[section] = f"Error: {e}"

        # Render the summary after processing all sections
        render_summary_html(section_data, fpath)
        elapsed = time.time() - start_time
        print(f"✅ Processed: {fpath} in {elapsed:.2f} seconds")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Failed to process {fpath} after {elapsed:.2f} seconds: {e}")


def find_all_pdfs(root_dir):
    return [file for file in root_dir.rglob('*.pdf')]

def main():
    total_start = time.time()
    pdf_files = find_all_pdfs(ROOT_DIR)

    print(f"Found {len(pdf_files)} PDFs. Processing...")

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.map(process_pdf, pdf_files)

    total_elapsed = time.time() - total_start
    print(f"\n🏁 All PDFs processed in {total_elapsed:.2f} seconds.")

if __name__ == '__main__':
    main()

# -----------------------------------------------------------------------
# This is the standard call to generate each section of the report sequentially
# -----------------------------------------------------------------------
# def process_pdf(fpath):
#     start_time = time.time()
#     try:
#         filled_values = extract_pdf_form_data(fpath)
#         field_section_map = load_field_to_section_map()
#         extracted_data = extract_sections(filled_values, TARGET_SECTIONS, field_section_map)

#         section_data = {}
#         for section in extracted_data:
#             # result = get_local_response(get_ai_instruction(extracted_data[section]))
#             result = get_remote_response(get_ai_instruction(extracted_data[section]))
#             section_data[section] = result

#         render_summary_html(section_data, fpath)
#         elapsed = time.time() - start_time
#         print(f"✅ Processed: {fpath} in {elapsed:.2f} seconds")
#     except Exception as e:
#         elapsed = time.time() - start_time
#         print(f"❌ Failed to process {fpath} after {elapsed:.2f} seconds: {e}")