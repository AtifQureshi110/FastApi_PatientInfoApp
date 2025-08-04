# utils.py

import json
from models.patient import Patient

def map_row_to_patient(row):
    try:
        allergies = json.loads(row[4]) if row[4] else []
    except (json.JSONDecodeError, TypeError):
        allergies = []

    return Patient(
        name=row[0],
        age=row[1],
        weight=row[2],
        married=bool(row[3]),
        allergies=allergies,
        contact_details=row[5],
        email=row[6],
        linkedin_url=row[7],
        height=row[8],
        id=row[11],  # id is mandatory in your model
    )


