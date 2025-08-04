# 1. main.py is your entry point, like the control tower.

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import EmailStr, AnyUrl
from typing import Optional
import json
from db_config.database import get_db_connection
from models.patient import Patient, PatientUpdate

app = FastAPI()

from routers import patient  # 👈 This imports the router (not the functions)
# app.include_router(patient.router, prefix="/api")  # 👈 This registers the router
app.include_router(patient.router)  # 👈 No prefix

"""FastAPI looks inside routers/patient.py
Finds the object router = APIRouter()
Registers any routes defined using @router.get(...), @router.post(...), etc.
Adds them under the prefix /api
"""


#css
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

#home
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

#frompage
@app.get("/form", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

#submit 
@app.post("/submit", response_class=HTMLResponse)
async def submit_form(
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

    bmi = patient.bmi
    verdict = patient.verdict

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Patients (
                id, name, age, weight, married, allergies,
                contact_details, email, linkedin_url,
                height, bmi, verdict
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id, name, age, weight, married, json.dumps(allergies_json),
            contact_details, str(email), str(linkedin_url),
            height, bmi, verdict
        ))
        conn.commit()

        # return templates.TemplateResponse("form.html", {
        #     "request": request,
        #     "message": f"Patient {name}'s information has been saved."
        # })

        return templates.TemplateResponse("patient_detail.html", {
            "request": request,
            "patient": patient.dict()
            })


    except Exception as e:
        error_msg = str(e)
        
        # Check for primary key violation (duplicate ID)
        if "duplicate key value" in error_msg.lower():
            message = f"⚠️ Patient ID '{id}' already exists. Please use a unique ID."
        else:
            message = f"❌ An error occurred: {error_msg}"

        return templates.TemplateResponse("form.html", {
            "request": request,
            "message": message
        })

    finally:
        cursor.close()
        conn.close()


# ✅ Web page route using your logic
@app.get("/patients", response_class=HTMLResponse)
async def show_patients(request: Request):
    patients = await patient.get_patients()  # Call your existing function
    return templates.TemplateResponse("all_patients.html", {"request": request, "patients": patients})
