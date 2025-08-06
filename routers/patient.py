"""2. routers/patient.py is a separate REST API module 
(for /patients endpoints).
You don’t need main.py to directly import every route
or function, because you're telling FastAPI to include
a router that already contains all those API paths."""
# routers/patient.py
from fastapi import APIRouter, HTTPException, Request, Form
from models.patient import Patient
import json
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db_config.database import get_db_connection
from pydantic import EmailStr, AnyUrl
from typing import Optional
router = APIRouter()
templates = Jinja2Templates(directory="templates")
from routers.utils import map_row_to_patient

def extract_patient_fields(patient, for_update=False):
    fields = [
        patient.name,
        patient.age,
        patient.weight,
        patient.married,
        json.dumps(patient.allergies),
        patient.contact_details,
        str(patient.email),
        str(patient.linkedin_url),
        patient.height,
        patient.bmi,
        patient.verdict,
    ]
    return fields + [patient.id] if for_update else [patient.id] + fields


def save_patient_to_db(patient, mode="insert"):
    conn = get_db_connection()
    cursor = conn.cursor()

    if mode == "insert":
        query = """
            INSERT INTO Patients (
                id, name, age, weight, married, allergies,
                contact_details, email, linkedin_url,
                height, bmi, verdict
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = extract_patient_fields(patient, for_update=False)

    elif mode == "update":
        query = """
            UPDATE Patients SET
                name=?, age=?, weight=?, married=?, allergies=?,
                contact_details=?, email=?, linkedin_url=?,
                height=?, bmi=?, verdict=?
            WHERE id=?
        """
        values = extract_patient_fields(patient, for_update=True)

    else:
        raise ValueError("Invalid mode. Use 'insert' or 'update'.")

    cursor.execute(query, values)
    conn.commit()
    conn.close()


# 🔁 REST API - Add a new patient
@router.post("/patients")
async def create_patient(patient: Patient):
    try:
        # To insert a new patient
        save_patient_to_db(patient, mode="insert")
        return {"message": f"Patient {patient.name} added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patients")
async def get_patients():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Patients")
        rows = cursor.fetchall()
        patients = [map_row_to_patient(row).dict() for row in rows]
        return patients
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/update", response_class=HTMLResponse)
async def update_page(request: Request, message: Optional[str] = None):
    return templates.TemplateResponse("update_patient.html", {
        "request": request,
        "message": message
    })

# @router.post("/search_patient", response_class=HTMLResponse)
# def search_patient(request: Request, id: str = Form(...)):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
#         cursor.execute("SELECT * FROM Patients WHERE id = ?", (id,))
#         row = cursor.fetchone()
#         # 🔍 Add this line to debug what is fetched
#         if not row:
#             return templates.TemplateResponse("update_patient.html", {
#                 "request": request, 
#                 "error": f"No patient found with ID {id}"})
        
#         patient = map_row_to_patient(row)
#         return templates.TemplateResponse("update_patient.html", {
#             "request": request, 
#             "patient": patient,
#             # "message": f"Patient with ID: {id} found. Please choose an action: click 'Update' to modify the record or 'Delete' to remove it.",
#             # "show_options_only": True , # 👈 added this flag
#             # "show_form": False
#         })

#     finally:
#         cursor.close()
#         conn.close()

@router.post("/search_patient", response_class=HTMLResponse)
def search_patient(request: Request, id: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Patients WHERE id = ?", (id,))
        row = cursor.fetchone()
        print("Fetched row:", row)  # Debug line

        if not row:
            return templates.TemplateResponse("update_patient.html", {
                "request": request, 
                "error": f"No patient found with ID {id}"})
        
        patient = map_row_to_patient(row)
        
        return templates.TemplateResponse("update_patient.html", {
            "request": request,
            "patient": patient,
            "message": f"Patient with ID {id} found. Do you want to update?",
            "show_options_only": True
        })
    finally:
        cursor.close()
        conn.close()


@router.post("/select_action")
def select_action(request: Request, action: str = Form(...), id: str = Form(...)):
    if action == "update":
        # Just show the update form
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            patient = {
                "id": row[0],
                "name": row[1],
                "city": row[2],
                "age": row[3],
                "gender": row[4],
                "height": row[5],
                "weight": row[6],
                "bmi": row[7],
                "verdict": row[8],
            }
            return templates.TemplateResponse("update_patient.html", {
                "request": request,
                "patient": patient,
                "show_form": True
            })
    elif action == "delete":
        return templates.TemplateResponse("update_patient.html", {
            "request": request,
            "confirm_delete": True,
            "id": id
        })

# @router.post("/delete_patient")
# def delete_patient(request: Request, id: str = Form(...)):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM patients WHERE id = ?", (id,))
#     conn.commit()
#     conn.close()

#     return templates.TemplateResponse("update_patient.html", {
#         "request": request,
#         "message": f"Patient with ID {id} deleted successfully."
#     })


@router.post("/delete_patient")
def delete_patient(request: Request, id: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return templates.TemplateResponse("update_patient.html", {
        "request": request,
        "message": f"Patient with ID {id} deleted successfully."
    })


@router.post("/update_patient")
async def update_patient(
    request: Request,
    id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    married: Optional[bool] = Form(False),
    allergies: str = Form(...),
    contact_details: str = Form(...),
    email: EmailStr = Form(...),
    linkedin_url: AnyUrl = Form(...),
    height: float = Form(...)
):
    try:
        allergies_json = json.loads(allergies) if allergies.strip().startswith("[") else [a.strip() for a in allergies.split(",")]
    except:
        allergies_json = [allergies.strip()]

    # ✅ Reuse the same Patient model to calculate BMI/Verdict
    patient = Patient(
        id=id,
        name=name,
        age=age,
        weight=weight,
        married=married,
        allergies=allergies_json,
        contact_details=contact_details,
        email=email,
        linkedin_url=linkedin_url,
        height=height
    )
    print(patient)  # ✅ Add this line to inspect the Patient object
    bmi = patient.bmi
    verdict = patient.verdict
    try:
        save_patient_to_db(patient, mode="update")
        return RedirectResponse(url="/update?message=Patient updated successfully!", 
                                status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# this is new router

@router.post("/show_update_form")
async def show_update_form(request: Request, id: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Patients WHERE id = ?", (id,))
    row = cursor.fetchone()

    if row:
        patient = map_row_to_patient(row)
        return templates.TemplateResponse("update_patient.html", {
            "request": request,
            "patient": patient,
            "show_form": True
        })
    else:
        return templates.TemplateResponse("update_patient.html", {
            "request": request,
            "message": f"No patient found with ID {id}",
            "show_form": False
        })
