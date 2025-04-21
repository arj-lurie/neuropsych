from datetime import datetime

def get_patient_info(filled_values):
    # Parse dates
    dob_str = filled_values.get("Pt DOB")
    eval_date_str = filled_values.get("Form Date")

    try:
        dob = datetime.strptime(dob_str, "%m/%d/%Y")
        eval_date = datetime.strptime(eval_date_str, "%m/%d/%Y")

        # Compute difference
        years = eval_date.year - dob.year
        months = eval_date.month - dob.month
        days = eval_date.day - dob.day

        # Adjust if negative month/day
        if days < 0:
            months -= 1
        if months < 0:
            years -= 1
            months += 12

        age_at_eval = f"{years}-years, {months}-months"
    except Exception as e:
        age_at_eval = "Unknown"

    # Build patient_info dictionary
    patient_info = {
        "name": filled_values.get("Pt Name", "Unknown"),
        "medical_record_no": "#########",  # Placeholder or real value if available
        "date_of_birth": dob_str or "N/A",
        "dates_of_service": eval_date_str or "N/A",
        "age_at_evaluation": age_at_eval,
        "examiners": ["Stephanie K. Powell, Ph.D.", "Monica O. Thomas, M.A."]
    }

    return patient_info