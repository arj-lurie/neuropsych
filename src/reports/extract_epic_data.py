import re
import pdb
import pytesseract
from pdf2image import convert_from_path

def parse_epic_sections(text):
    """
    Parse a block of text into sectioned data from an Epic report.
    Returns a dict of {section_name: {raw_text}} for compatibility.
    """
    sections = {}
    current_section = None
    buffer = []

    # Regex for headers like "=== Section Name ==="
    section_header_re = re.compile(r"^=+\s*(.*?)\s*=+$")

    for line in text.splitlines():
        header_match = section_header_re.match(line)
        if header_match:
            # Save previous section
            if current_section and buffer:
                sections[current_section] = {"text": "\n".join(buffer).strip()}
                buffer = []

            # Start new section
            current_section = header_match.group(1).strip()
        elif current_section:
            buffer.append(line)

    # Save the last section
    if current_section and buffer:
        sections[current_section] = {"text": "\n".join(buffer).strip()}

    return sections

def extract_text_from_pdf(pdf_path):
    """
    OCR-based text extraction from image-based PDFs.
    """
    try:
        # Convert PDF to images
        images = convert_from_path(str(pdf_path))
        full_text = ""

        for img in images:
            text = pytesseract.image_to_string(img)
            full_text += text + "\n"
        
        # Split the extracted full_text by new lines and remove empty lines
        lines = [line.strip() for line in full_text.strip().split("\n") if line.strip()]
        
        # # Print first 10 lines to inspect structure
        # for i, line in enumerate(lines[:10]):  # Print the first 10 lines
        #     print(f"Line {i+1}: {line}")
        
        return lines  # Return the list of lines
        
        # return full_text.strip()
    except Exception as e:
        print(f"❌ OCR failed on {pdf_path.name}: {e}")
        return ""