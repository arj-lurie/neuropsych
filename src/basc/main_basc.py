import os
from create_basc_table import read_basc_report, create_labels, extract_text_between_pages, extract_numbers_and_map_labels, extract_test_date_and_relationship, generate_html_table, generate_combined_html_table
from visualize_basc_table import create_graph, create_combined_graph
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import time
import pdb

# Function to process a single PDF file
def process_pdf(fpath):
    start_time = time.time()  # Start timer for the single file
    text = read_basc_report(fpath)
    
    # Setup the labels and structured data
    labels, structured_data = create_labels()

    # Extract the pages of interest for the BASC Table
    pages_of_interest = extract_text_between_pages(text, 'VALIDITY INDEX SUMMARY', 'Percentile')

    # Extract the T-Score values and map them to the labels
    data = extract_numbers_and_map_labels(pages_of_interest, labels)
    
    rater_poi = extract_text_between_pages(text, 'Interpretive Summary Report', 'Norm Group 1:')
    rater_data = extract_test_date_and_relationship(rater_poi)
    rater_label = rater_data['Test Date'] + ', (' + rater_data['Relationship'] + ')'

    # Write the data to the Word document
    filename_without_extension, _ = os.path.splitext(os.path.basename(fpath))
    fname = filename_without_extension + '.html'
    
    file_directory = os.path.dirname(fpath)
    output_path = os.path.join(file_directory, fname)
    
    # write_to_docx(data, structured_data, output_path) # Deprecated, since we are now producing HTML reports

    html_table =  generate_html_table(data, structured_data, rater_label)
    create_graph(data, structured_data, html_table, output_file= output_path)

    end_time = time.time()  # End timer for the single file
    processing_time = end_time - start_time  # Calculate the processing time for the file
    print(f"Processed {fpath} in {processing_time:.2f} seconds")

# Function to process all PDFs in a given folder in parallel
def process_pdfs_in_folder(folder_path):
    # Get a list of all .pdf files in the folder
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.pdf')]
    total_files = len(pdf_files)  # Total number of files in the folder

    total_start_time = time.time()  # Start total time timer

    # Use ProcessPoolExecutor to process the files in parallel
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        executor.map(process_pdf, pdf_files)
    
    total_end_time = time.time()  # End total time timer
    total_processing_time = total_end_time - total_start_time  # Calculate the total time
    print(f"Total processing time for all files: {total_processing_time:.2f} seconds")

# def process_subfolder(folder_path):
#     start_time = time.time()
#     pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    
#     all_data = {}  # filename (no extension) -> data dict
#     all_labels = set()  # track all unique labels across files

#     for fpath in pdf_files:
#         text = read_basc_report(fpath)

#         rater_poi = extract_text_between_pages(text, 'Behavior Assessment System for Children', 'Norm Group 1:')
#         rater_data = extract_test_date_and_relationship(rater_poi)
#         rater_label = rater_data['Test Date'] + ', (' + rater_data['Relationship'] + ')'

#         labels, structured_data = create_labels(rater_data['Type'])        
#         # pdb.set_trace()

#         pages_of_interest = extract_text_between_pages(text, 'VALIDITY INDEX SUMMARY', 'Percentile')
#         data = extract_numbers_and_map_labels(pages_of_interest, labels)
#         all_labels.update(data.keys())  # track all labels used in any file
        
#         filename_without_extension = os.path.splitext(os.path.basename(fpath))[0]

#         report_data = {
#             'data': data,
#             'rater_label': rater_label
#         }

#         all_data[filename_without_extension] = report_data

#     # Create combined HTML and graph
#     combined_html = generate_combined_html_table(all_data, structured_data)
#     output_file = os.path.join(folder_path, 'combined_report.html')
#     create_combined_graph(all_data, structured_data, combined_html, output_file=output_file)

#     end_time = time.time()
#     print(f"Processed folder: {folder_path} in {end_time - start_time:.2f} seconds")

from collections import defaultdict

def process_subfolder(folder_path):
    start_time = time.time()
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    
    all_data = {}  # filename (no extension) -> data dict
    all_labels = set()  # track all unique labels across files
    all_structured_data = {}  # to hold structured data of each file for merging later

    for fpath in pdf_files:
        text = read_basc_report(fpath)

        rater_poi = extract_text_between_pages(text, 'Behavior Assessment System for Children', 'Norm Group 1:')
        rater_data = extract_test_date_and_relationship(rater_poi)
        rater_label = rater_data['Test Date'] + ', (' + rater_data['Relationship'] + ')'

        labels, structured_data = create_labels(rater_data['Type'])        

        pages_of_interest = extract_text_between_pages(text, 'VALIDITY INDEX SUMMARY', 'Percentile')
        data = extract_numbers_and_map_labels(pages_of_interest, labels)

        all_labels.update(data.keys())  # track all labels used in any file
        
        filename_without_extension = os.path.splitext(os.path.basename(fpath))[0]

        report_data = {
            'data': data,
            'rater_label': rater_label
        }

        all_data[filename_without_extension] = report_data
        all_structured_data[filename_without_extension] = structured_data

    # Combine the structured_data from all files, preserving order and avoiding duplicates
    combined_structured_data = defaultdict(list)

    for file, structured_data in all_structured_data.items():
        for scale, subscales in structured_data.items():
            if scale not in combined_structured_data:
                combined_structured_data[scale] = []

            # Add subscales without duplicates, preserving order
            for subscale in subscales:
                if subscale not in combined_structured_data[scale]:
                    combined_structured_data[scale].append(subscale)

    # Create the combined HTML table
    combined_html = generate_combined_html_table(all_data, combined_structured_data)  # Pass combined_structured_data here

    # Generate the combined graph
    output_file = os.path.join(folder_path, 'combined_report.html')
    create_combined_graph(all_data, combined_structured_data, combined_html, output_file=output_file)

    end_time = time.time()
    print(f"Processed folder: {folder_path} in {end_time - start_time:.2f} seconds")


def process_all_subfolders(root_folder):
    subfolders = [os.path.join(root_folder, name) for name in os.listdir(root_folder)
                  if os.path.isdir(os.path.join(root_folder, name))]

    for subfolder in subfolders:
        process_subfolder(subfolder)

def process_all_subfolders_parallel(root_folder):
    subfolders = [os.path.join(root_folder, name) for name in os.listdir(root_folder)
                  if os.path.isdir(os.path.join(root_folder, name))]

    total_start = time.time()

    # Process each subfolder in parallel
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        executor.map(process_subfolder, subfolders)

    total_end = time.time()
    print(f"✅ All subfolders processed in {total_end - total_start:.2f} seconds.")

if __name__ == "__main__":
    # Call the function with the folder path where the PDFs are located
    folder_path = '../../data/basc_poc/'  # Specify your folder path here
    
    # process_pdf('../../data/basc_test/P15/BASC-P5.pdf') # Individual PDF File Debugging

    # process_all_subfolders(folder_path) # In Series (Sequential)
    process_all_subfolders_parallel(folder_path) # In Parallel (Concurrent)
