from pdf2image import convert_from_path
import pytesseract


def ocr_pdf(pdf_path):

    text = ""

    images = convert_from_path(pdf_path)

    for img in images:

        t = pytesseract.image_to_string(img)

        text += t + "\n"

    return text
