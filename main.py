from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from xhtml2pdf import pisa
from io import BytesIO

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Hesaplama fonksiyonları
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)

def calculate_pf_ratio(pao2, fio2):
    if fio2 == 0:
        return 0
    return round(pao2 / (fio2 / 100), 2)

def calculate_a_a_gradient(fio2, pao2, paco2, age):
    alveolar_o2 = fio2 / 100 * (760 - 47) - (paco2 / 0.8)
    gradient = alveolar_o2 - pao2
    return round(gradient, 2)

def interpret_paco2(paco2):
    if paco2 < 35:
        return "Düşük (Hipokapni)"
    elif paco2 > 45:
        return "Yüksek (Hiperkapni)"
    else:
        return "Normal"

def check_compensation(ph, paco2, hco3):
    expected_hco3 = 24 + (paco2 - 40) * 0.1
    expected_paco2 = 40 - 1.2 * (24 - hco3)
    delta_hco3 = abs(hco3 - expected_hco3)
    delta_paco2 = abs(paco2 - expected_paco2)
    return {
        "Beklenen HCO3": round(expected_hco3, 2),
        "Beklenen pCO2": round(expected_paco2, 2),
        "HCO3 kompanzasyonu": "Uygun" if delta_hco3 <= 2 else "Uygun değil",
        "pCO2 kompanzasyonu": "Uygun" if delta_paco2 <= 2 else "Uygun değil"
    }

# Ana form
@app.get("/", response_class=HTMLResponse)
async def form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# Tahmin ve hesaplama işlemleri
@app.post("/form-predict/", response_class=HTMLResponse)
async def predict_from_form(
    request: Request,
    Age: int = Form(...),
    Sex: int = Form(...),
    Weight_kg: float = Form(...),
    Height_cm: float = Form(...),
    HR_gelis: int = Form(...),
    RR_gelis: int = Form(...),
    SBP_gelis: int = Form(...),
    DBP_gelis: int = Form(...),
    SpO2_gelis: float = Form(...),
    GCS_gelis: int = Form(...),
    pH_gelis: float = Form(...),
    pCO2_gelis: float = Form(...),
    pO2_gelis: float = Form(...),
    HCO3_gelis: float = Form(...),
    BE_gelis: float = Form(...),
    Lactate_gelis: float = Form(...),
    FiO2_gelis: int = Form(...),
    HR_pre: int = Form(...),
    RR_pre: int = Form(...),
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
    Respiratory_Rate: int = Form(...),
    Accessory_Muscle_Use: int = Form(...),
    Current_Treatment: str = Form(...),
    Clinical_Diagnosis: str = Form(...),
    Primary_Complaint: str = Form(...)
):
    failure_result = "Tip 2 (Hiperkapnik)"
    treatment_result = "NIMV"

    bmi = calculate_bmi(Weight_kg, Height_cm)
    pf_ratio = calculate_pf_ratio(pO2_pre, FiO2_pre)
    aagradient = calculate_a_a_gradient(FiO2_pre, pO2_pre, pCO2_pre, Age)
    pco2_comment = interpret_paco2(pCO2_pre)
    compensation = check_compensation(pH_pre, pCO2_pre, HCO3_pre)

    return templates.TemplateResponse("result.html", {
        "request": request,
        "failure_result": failure_result,
        "treatment_result": treatment_result,
        "bmi": bmi,
        "pf_ratio": pf_ratio,
        "aagradient": aagradient,
        "pco2_comment": pco2_comment,
        "compensation": compensation
    })

# PDF çıktısı
@app.post("/download-pdf/")
async def download_pdf(
    failure_result: str = Form(...),
    treatment_result: str = Form(...)
):
    html_content = f"""
    <html><body>
    <h2>Solunum Yetmezliği ve Tedavi Raporu</h2>
    <p><strong>Solunum Yetmezliği Tipi:</strong> {failure_result}</p>
    <p><strong>Önerilen Tedavi:</strong> {treatment_result}</p>
    <p>Bu rapor entube3 karar destek sistemi tarafından oluşturulmuştur.</p>
    </body></html>
    """
    pdf_stream = BytesIO()
    pisa.CreatePDF(html_content, dest=pdf_stream)
    pdf_stream.seek(0)
    return StreamingResponse(pdf_stream, media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=rapor.pdf"
    })
