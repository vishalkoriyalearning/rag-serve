from pdfminer.high_level import extract_text
from io import BytesIO

def extract_pdf_text(file_bytes: bytes) -> str:
    return extract_text(BytesIO(file_bytes))
