from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import pdfplumber
import pandas as pd
from pdf2image import convert_from_path
import pytesseract

from typing import List


app = FastAPI()


# =========================
# folders
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
TEMPLATES_FOLDER = os.path.join(BASE_DIR, "templates")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# =========================
# templates
# =========================

templates = Jinja2Templates(directory=TEMPLATES_FOLDER)


# =========================
# static / outputs
# =========================

app.mount(
    "/outputs",
    StaticFiles(directory=OUTPUT_FOLDER),
    name="outputs"
)


# =========================
# home
# =========================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "saved_files": None,
            "message": None,
        },
    )


# =========================
# upload
# =========================

@app.post("/", response_class=HTMLResponse)
async def upload_pdf(
    request: Request,
    pdf_file: UploadFile = File(...),
    output_name: str = Form("output_data"),
):

    file_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)

    with open(file_path, "wb") as f:
        f.write(await pdf_file.read())

    tables = extract_tables_from_pdf(file_path)

    if not tables:
        tables = extract_tables_from_pdf_ocr(file_path)

    if not tables:

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "saved_files": None,
                "message": "No data extracted",
            },
        )

    saved_files = process_and_save(tables, output_name)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "saved_files": saved_files,
            "message": None,
        },
    )


# =========================
# extract normal PDF
# =========================

def extract_tables_from_pdf(pdf_path):

    tables = []

    try:

        with pdfplumber.open(pdf_path) as pdf:

            for page in pdf.pages:

                page_tables = page.extract_tables()

                for table in page_tables:

                    tables.append(table)

    except Exception as e:

        print(e)

    return tables


# =========================
# OCR
# =========================

def extract_tables_from_pdf_ocr(pdf_path):

    tables = []

    try:

        images = convert_from_path(pdf_path)

        for img in images:

            text = pytesseract.image_to_string(img, lang="eng+ara")

            lines = [
                line.split()
                for line in text.split("\n")
                if line.strip()
            ]

            if lines:

                tables.append(lines)

    except Exception as e:

        print(e)

    return tables


# =========================
# save
# =========================

def process_and_save(tables: List, output_name: str):

    saved_files = []

    for i, table in enumerate(tables):

        if len(table) > 1:

            df = pd.DataFrame(table[1:], columns=table[0])

        else:

            df = pd.DataFrame(table)

        csv_name = f"{output_name}_{i+1}.csv"
        xlsx_name = f"{output_name}_{i+1}.xlsx"

        csv_path = os.path.join(OUTPUT_FOLDER, csv_name)
        xlsx_path = os.path.join(OUTPUT_FOLDER, xlsx_name)

        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        df.to_excel(xlsx_path, index=False)

        saved_files.append((csv_name, xlsx_name))

    return saved_files


# =========================
# download
# =========================

@app.get("/outputs/{filename}")
async def download_file(filename: str):

    file_path = os.path.join(OUTPUT_FOLDER, filename)

    return FileResponse(file_path)


# =========================
# MAIN (for render)
# =========================

if __name__ == "__main__":

    import uvicorn

    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
    )
