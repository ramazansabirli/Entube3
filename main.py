
from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import joblib
import numpy as np
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

pipe_failure = joblib.load("pipe_failure.pkl")
pipe_treatment = joblib.load("pipe_treatment.pkl")
failure_label = joblib.load("failure_label.pkl")
treatment_label = joblib.load("treatment_label.pkl")

@app.get("/", response_class=HTMLResponse)
async def form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/form-predict/", response_class=HTMLResponse)
async def predict_from_form(
    request: Request,
    Age: int = Form(...),
    Sex: int = Form(...),
    Weight_kg: float = Form(...),
    Height_cm: float = Form(...),
    RR_pre: int = Form(...),
    HR_pre: int = Form(...),
    SBP_pre: int = Form(...),
    DBP_pre: int = Form(...),
    SpO2_pre: float = Form(...),
    GCS_pre: int = Form(...),
    pH_pre: float = Form(...),
    pCO2_pre: float = Form(...),
    pO2_pre: float = Form(...),
    HCO3_pre: float = Form(...),
    BE_pre: float = Form(...),
    Lactate_pre: float = Form(...),
    FiO2_pre: int = Form(...),
    Accessory_Muscle_Use: int = Form(...),
    Clinical_Diagnosis: int = Form(...),
    Primary_Complaint: int = Form(...)
):
    features = np.array([[Age, Sex, Weight_kg, Height_cm, RR_pre, HR_pre, SBP_pre, DBP_pre,
                          SpO2_pre, GCS_pre, pH_pre, pCO2_pre, pO2_pre, HCO3_pre, BE_pre,
                          Lactate_pre, FiO2_pre, Accessory_Muscle_Use, Clinical_Diagnosis,
                          Primary_Complaint]])
    pred_failure = pipe_failure.predict(features)[0]
    features_with_failure = np.hstack((features, [[pred_failure]]))
    pred_treatment = pipe_treatment.predict(features_with_failure)[0]

    return templates.TemplateResponse("result.html", {
        "request": request,
        "failure_result": failure_label.inverse_transform([pred_failure])[0],
        "treatment_result": treatment_label.inverse_transform([pred_treatment])[0]
    })
