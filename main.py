from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from xhtml2pdf import pisa
from io import BytesIO

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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
    # Model entegrasyonu yapılacaksa buraya
    failure_result = "Tip 2 (Hiperkapnik)"
    treatment_result = "NIMV"

    return templates.TemplateResponse("result.html", {
        "request": request,
        "failure_result": failure_result,
        "treatment_result": treatment_result
    })

@app.post("/download-pdf/")
async def download_pdf(
    failure_result: str = Form(...),
    treatment_result: str = Form(...)
):
    html_content = f"""
    <html>
    <head><title>PDF Rapor</title></head>
    <body>
        <h2>Solunum Yetmezliği ve Tedavi Raporu</h2>
        <p><strong>Solunum Yetmezliği Tipi:</strong> {failure_result}</p>
        <p><strong>Önerilen Tedavi:</strong> {treatment_result}</p>
        <br><hr><br>
        <p>Bu rapor entube3 karar destek sistemi tarafından otomatik olarak oluşturulmuştur.</p>
    </body>
    </html>
    """
    pdf_stream = BytesIO()
    pisa.CreatePDF(html_content, dest=pdf_stream)
    pdf_stream.seek(0)

    return StreamingResponse(pdf_stream, media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=rapor.pdf"
    })
