import time
import multiprocessing
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from extract_neuropsych_form import extract_pdf_form_data, extract_sections, load_field_to_section_map
from ai_configuration_remote import get_remote_response
from ai_instructions import get_ai_instruction
from report_renderer import render_summary_html
from patient_details import get_patient_info
from extract_epic_data import extract_text_from_pdf, parse_epic_sections
import pdb

# --------------------------------------------------
# Config
# --------------------------------------------------
ROOT_DIR = Path('../../data/np_hx/patients')
TARGET_SECTIONS = [    
    'Background Info Header',
    'Concerns Prompting This Evaluation',
    'Medical History',
    'Birth & Development History',
    'School History',
    'Family History'
]

# --------------------------------------------------
# PDF-Type Routing
# --------------------------------------------------
PDF_TYPE_HANDLERS = {
    "np_hx_form": lambda path: extract_sections(
        extract_pdf_form_data(path),
        TARGET_SECTIONS,
        load_field_to_section_map()
    ),
    "epic_report": lambda path: {
        "Reason for Referral": {
            "text": extract_text_from_pdf(path)
        }
    },   
    # Add more PDF types here
}

def identify_pdf_type(filename):
    for tag in PDF_TYPE_HANDLERS:
        if tag in filename.lower():
            return tag
    return None  # Unknown or unsupported file

# --------------------------------------------------
# Core Processing Function
# --------------------------------------------------
def process_patient_folder(folder_path):
    start_time = time.time()
    try:
        section_data_raw = defaultdict(dict)

        for pdf_path in folder_path.glob("*.pdf"):
            pdf_type = identify_pdf_type(pdf_path.name)
            extractor = PDF_TYPE_HANDLERS.get(pdf_type)

            if not extractor:
                print(f"⚠️ Skipping unknown PDF type: {pdf_path.name}")
                continue

            try:
                extracted = extractor(pdf_path)

                if pdf_type == "np_hx_form":
                    flat_form_data = extract_pdf_form_data(pdf_path) ## If the PDF is a form, also keep the flat values since this is needed for the document header.

                for section, data in extracted.items():
                    section_data_raw[section].update(data)
            except Exception as e:
                print(f"❌ Error extracting from {pdf_path.name}: {e}")

        patient_info = get_patient_info(flat_form_data)
        
        # Run remote AI calls concurrently
        section_data = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_section = {
                executor.submit(get_remote_response, get_ai_instruction(data, section)): section
                for section, data in section_data_raw.items()
            }

            for future in as_completed(future_to_section):
                section = future_to_section[future]
                try:
                    section_data[section] = future.result()
                except Exception as e:
                    section_data[section] = f"Error: {e}"

        # Ensure "Reason for Referral" is the first section after all AI responses are gathered
        if "Reason for Referral" in section_data:
            reason_for_referral = section_data.pop("Reason for Referral")
            section_data = {"Reason for Referral": reason_for_referral, **section_data}
        
        render_summary_html(section_data, folder_path, patient_info, TARGET_SECTIONS)

        elapsed = time.time() - start_time
        print(f"✅ Processed {folder_path.name} in {elapsed:.2f} seconds")

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Failed to process {folder_path.name} after {elapsed:.2f} seconds: {e}")

# --------------------------------------------------
# Main Entry Point
# --------------------------------------------------
def find_all_patient_folders(root_dir):
    return [folder for folder in root_dir.iterdir() if folder.is_dir()]

def main():
    total_start = time.time()
    patient_folders = find_all_patient_folders(ROOT_DIR)

    print(f"Found {len(patient_folders)} patient folders. Processing...")

    # 🔧 DEBUG MODE: disable multiprocessing
    for folder in patient_folders:
        print(f"🔍 Debugging: {folder}")
        process_patient_folder(folder)  # <— pdb.set_trace() will work here

    # with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
    #     pool.map(process_patient_folder, patient_folders)

    total_elapsed = time.time() - total_start
    print(f"\n🏁 All patients processed in {total_elapsed:.2f} seconds.")

if __name__ == '__main__':
    main()
