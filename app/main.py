import os
import uvicorn

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from services.pdf_service import extract_text
from services.ocr_service import ocr_pdf
from services.ai_service import ai_to_json
from services.table_service import json_to_rows, normalize_table
from services.export_service import save_csv, save_xlsx


# =========================
# APP
# =========================

app = FastAPI()


# =========================
# STATIC / TEMPLATES
# =========================

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# =========================
# GLOBAL DATA
# =========================

last_table = []


# =========================
# HOME
# =========================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# =========================
# PROCESS PDF
# =========================

@app.post("/process", response_class=HTMLResponse)
async def process_pdf(
    request: Request,
    file: UploadFile = File(...),
    mode: str = Form(...)
):

    global last_table

    os.makedirs("uploads", exist_ok=True)

    path = f"uploads/{file.filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    # -------- extract --------

    text = extract_text(path)

    if not text.strip():
        text = ocr_pdf(path)

    # -------- AI mode --------

    if mode == "ai":

        json_data = ai_to_json(text)

        rows = json_to_rows(json_data)

    else:

        rows = [line.split() for line in text.splitlines()]

    # -------- normalize --------

    rows = normalize_table(rows)

    last_table = rows

    return templates.TemplateResponse(
        "preview.html",
        {
            "request": request,
            "data": rows
        }
    )


# =========================
# DOWNLOAD CSV
# =========================

@app.get("/download/csv")
async def download_csv():

    global last_table

    os.makedirs("outputs", exist_ok=True)

    path = "outputs/output.csv"

    save_csv(last_table, path)

    return FileResponse(
        path,
        filename="output.csv"
    )


# =========================
# DOWNLOAD XLSX
# =========================

@app.get("/download/xlsx")
async def download_xlsx():

    global last_table

    os.makedirs("outputs", exist_ok=True)

    path = "outputs/output.xlsx"

    save_xlsx(last_table, path)

    return FileResponse(
        path,
        filename="output.xlsx"
    )


# =========================
# MAIN (PORT FIX)
# =========================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
