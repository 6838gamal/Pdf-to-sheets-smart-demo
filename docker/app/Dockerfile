FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# تثبيت الأدوات اللازمة للـ OCR وPDF
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    gcc \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# نسخ كل محتويات app داخل الحاوية
COPY ../../app /app

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
