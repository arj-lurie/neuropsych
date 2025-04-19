def get_ai_instruction(filled_values):
    """
    Generates an AI instruction message based on the provided filled values.

    Args:
        filled_values (str): The filled values extracted from a PDF.

    Returns:
        str: The AI instruction message.
    """
    # Define the AI instruction message
    ai_message = f"Here are the various fields I extracted from a .pdf: {filled_values}." + """
    Please provide a comprehensive summary based on all the the information in the fields. 
    The very presence of a field indicates that it occurred. For e.g.

    'Newborn Difficulties Jaundice': 'O' -> indicates that the patient had jaundice at birth.
    'Developmental Concerns Feeding': 'O' -> indicates that the patient had feeding concerns at some point in their development.

    Please do not include any personal opinions or interpretations. Your output should be in the form of a paragraph - not bullet points or a list. 
    Please ensure the paragraph includes all the provided details in all the fields.""" 

    return ai_message
