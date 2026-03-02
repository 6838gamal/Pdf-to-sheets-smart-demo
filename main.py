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

# إعداد المسارات
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# قوالب HTML
templates = Jinja2Templates(directory="templates")

# ملفات ثابتة
app.mount("/outputs", StaticFiles(directory=OUTPUT_FOLDER), name="outputs")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "saved_files": None, "message": None})

@app.post("/", response_class=HTMLResponse)
async def upload_pdf(request: Request, pdf_file: UploadFile = File(...), output_name: str = Form("output_data")):
    file_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
    
    # حفظ الملف المرفوع
    with open(file_path, "wb") as f:
        f.write(await pdf_file.read())

    # استخراج الجداول
    tables = extract_tables_from_pdf(file_path)
    
    # إذا لم توجد جداول نصية، جرب OCR
    if not tables:
        tables = extract_tables_from_pdf_ocr(file_path)
    
    if not tables:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "saved_files": None,
            "message": "لا توجد جداول أو نصوص يمكن استخراجها."
        })
    
    saved_files = process_and_save(tables, output_name)
    return templates.TemplateResponse("index.html", {"request": request, "saved_files": saved_files, "message": None})

def extract_tables_from_pdf(pdf_path):
    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                for table in page_tables:
                    tables.append(table)
    except:
        pass
    return tables

def extract_tables_from_pdf_ocr(pdf_path):
    tables = []
    try:
        images = convert_from_path(pdf_path)
        for img in images:
            text = pytesseract.image_to_string(img, lang="eng+ara")
            # تحويل النص إلى جدول بسيط: كل سطر كسطر جدول، يفترض فواصل بمسافات
            lines = [line.split() for line in text.split("\n") if line.strip()]
            if lines:
                tables.append(lines)
    except:
        pass
    return tables

def process_and_save(tables: List, output_name: str):
    saved_files = []
    for idx, table in enumerate(tables):
        # افترض الصف الأول هو العناوين إذا كان طويلا بما فيه الكفاية
        df = pd.DataFrame(table[1:], columns=table[0]) if len(table) > 1 else pd.DataFrame(table)
        csv_file = os.path.join(OUTPUT_FOLDER, f"{output_name}_table{idx+1}.csv")
        xlsx_file = os.path.join(OUTPUT_FOLDER, f"{output_name}_table{idx+1}.xlsx")
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        df.to_excel(xlsx_file, index=False)
        saved_files.append((csv_file.split("/")[-1], xlsx_file.split("/")[-1]))
    return saved_files

@app.get("/outputs/{filename}")
async def get_file(filename: str):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    return FileResponse(file_path)

# ===== دالة الماين لتشغيل السكربت مباشرة =====
if __name__ == "__main__":
    import uvicorn
    print("تشغيل FastAPI على http://127.0.0.1:8000/")
    uvicorn.run("main:app", port=8000, reload=False)
