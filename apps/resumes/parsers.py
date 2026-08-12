from django.core.exceptions import ValidationError
import pdfplumber
import fitz
from docx import Document
from pathlib import Path

def extract_text_from_pdf(file_path):
    """Extract text from PDF using PyMuPDF with pdfplumber fallback."""
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
        doc.close()
    except Exception:
        pass

    if not text.strip():
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"

        except Exception as e:
            raise ValidationError(f"Failed to parse PDF file: {str(e)}")

    return text.strip()

def extract_text_from_docx(file_path):
    """Extract text from DOCX file."""
    try:
        doc = Document(file_path)
        full_text = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(full_text)
    except Exception as e:
        raise ValidationError(f"Failed to parse DOCX file: {str(e)}")

def parse_resume_file(file_path):
    # detect file type and extract raw text
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif extension in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format '{extension}'. Please upload a PDF or DOCX file.")