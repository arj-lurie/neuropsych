from docx import Document
import os
import pdb
import time
import tiktoken
from ai_configuration_remote import get_remote_response
from ai_instructions import get_ai_instruction_single_file, merge_theme_summaries
import json
# Choose the right encoding based on model
encoding = tiktoken.encoding_for_model("gpt-4o-mini")  # or "gpt-3.5-turbo"

# Last request time and total token count
last_request_time = None
tokens_sent_last_request = 0

# Token limit
token_limit = 20000

# Function to wait if necessary based on token count and time elapsed
def wait_if_needed(current_tokens):
    global last_request_time, tokens_sent_last_request
    
    # Check if there's a previous request
    if last_request_time is not None:
        # Calculate the time passed since the last request
        time_since_last_request = time.time() - last_request_time
        
        # If the time since last request is less than 60 seconds, we may need to wait
        if time_since_last_request < 60:
            # If the current request will exceed the token limit, wait for the required time
            if tokens_sent_last_request + current_tokens > token_limit:
                time_to_wait = 60 - time_since_last_request
                print(f"Waiting for {time_to_wait:.2f} seconds to avoid exceeding token limit.")
                time.sleep(time_to_wait)  # Wait until 60 seconds have passed

    # Update the last request time and token count
    last_request_time = time.time()
    tokens_sent_last_request = current_tokens

def wait_for_time(seconds: int):
    print(f"Waiting for {seconds} seconds...")
    for remaining in range(seconds, 0, -1):
        print(f"{remaining}...", end='', flush=True)
        time.sleep(1)
    print("Done waiting.\n")

def count_tokens(text):
    return len(encoding.encode(text))

def verify_entries_count_tokens(entries):
    total_token_count = 0
    for entry in entries:
        print(f"\n--- {entry['filename']} ---")
        
        # Split into lines and print the first 5 non-empty lines
        lines = entry['recommendations'].split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        for line in non_empty_lines[:5]:
            print(line)

        print("...")  # Indicate truncation

        token_count = count_tokens(entry['recommendations'])
        print(f"{entry['filename']}: {token_count} tokens")
        total_token_count += token_count

    print("Total tokens across all recommendations: ", total_token_count)

def load_documents_from_folder(folder_path):
    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".docx"):
            path = os.path.join(folder_path, filename)
            doc = Document(path)
            full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            docs.append({'filename': filename, 'text': full_text})
    return docs

import re

def extract_recommendations(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    recommendations = []
    start_collecting = False

    for sentence in sentences:
        lower_sentence = sentence.lower()
        
        if not start_collecting:
            if "based on" in lower_sentence and "recommendations are" in lower_sentence:
                start_collecting = True
                recommendations.append(sentence)
        elif "follow-up" in lower_sentence:
            break
        elif start_collecting:
            recommendations.append(sentence)
    
    return " ".join(recommendations).strip() if recommendations else None

# --- Main execution ---
folder_path = '../../data/full_reports'
documents = load_documents_from_folder(folder_path)

# Extract recommendations from all documents
recommendation_entries = []

for doc in documents:
    rec_text = extract_recommendations(doc['text'])
    if rec_text:
        recommendation_entries.append({
            'filename': doc['filename'],
            'recommendations': rec_text
        })

# Print and verify extracted data
# verify_entries_count_tokens(recommendation_entries)
# pdb.set_trace()

all_summaries = []
os.makedirs("results", exist_ok=True)

for entry in recommendation_entries:
    print(f"\n--- {entry['filename']} ---")
    print(entry['recommendations'])
    
    current_tokens = count_tokens(entry['recommendations'])
    print(f"Tokens: {current_tokens}")

    # Define a safe output file path
    filename_no_ext = os.path.splitext(entry['filename'])[0]
    output_path = f"results/{filename_no_ext}.json"

    # Ensure we wait if needed (if using llama-3.3-70b or related model)
    wait_if_needed(current_tokens * 1.75) #Adding a 75% buffer to the token count    
    
    result = get_remote_response(get_ai_instruction_single_file(entry['recommendations'], entry['filename']))
    # wait_for_time(60)  # Wait for 60 seconds after each request if using deepseek.

    # Save result string to file
    with open(output_path, "w") as f:
        f.write(result)

    # Append the result to the summaries list
    all_summaries.append(result)