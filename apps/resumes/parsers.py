from django.core.exceptions import ValidationError
import pdfplumber
import fitz
from docx import Document
from pathlib import Path

def extract_text_from_pdf(file_path):
    """Extract text from PDF using PyMuPDF (fitz) with pdfplumber fallback."""
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

    if not text.strip():
        raise ValidationError("Could not extract selectable text from PDF. Scanned/image-only PDFs are not supported.")

    return text.strip()

def extract_text_from_docx(file_path):
    """Extract text from DOCX file."""
    try:
        doc = Document(file_path)
        full_text = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(full_text)
    except Exception as e:
        raise ValidationError(f"Failed to parse DOCX file: {str(e)}")

def extract_text_from_txt(file_path):
    """Extract text from plain text (.txt) file with UTF-8 / Latin-1 fallback."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read().strip()
    except Exception as e:
        raise ValidationError(f"Failed to parse text file: {str(e)}")

def parse_resume_file(file_path):
    """Detect file extension and extract raw plain text."""
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif extension == '.docx':
        return extract_text_from_docx(file_path)
    elif extension == '.txt':
        return extract_text_from_txt(file_path)
    elif extension == '.doc':
        raise ValidationError("Legacy '.doc' format is not supported. Please convert your file to modern '.docx' or '.pdf'.")
    else:
        raise ValidationError(f"Unsupported file format '{extension}'. Please upload a PDF, DOCX, or TXT file.")