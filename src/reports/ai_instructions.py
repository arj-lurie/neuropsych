from example_sections import example_sections
import pdb

def get_ai_instruction(filled_values, section):
    """
    Generates an AI instruction message based on the provided filled values.

    Args:
        filled_values (str): The filled values extracted from a PDF.

    Returns:
        str: The AI instruction message.
    """    
    section_example = example_sections.get(section, "No example available for this section.")
    
    if section_example == "No example available for this section.":
        print(f"No example data available for {section}")
        pdb.set_trace()

    # Define the AI instruction message
    ai_message = f"Here are the various fields/lines I extracted from a .pdf: {filled_values}." + """
    Please provide a comprehensive summary based on all the the information in the fields. 
    The very presence of a field indicates that it occurred. For e.g.

    'Newborn Difficulties Jaundice': 'O' -> indicates that the patient had jaundice at birth.
    'Developmental Concerns Feeding': 'O' -> indicates that the patient had feeding concerns at some point in their development.

    Use the example below as a strict template. Your output **must** match its structure, length, and tone as closely as possible. 
    Do not add extra details or change the formatting:
    ``` """ + f"{section_example}" + " ```"

    return ai_message