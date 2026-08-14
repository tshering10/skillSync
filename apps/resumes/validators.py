import os
from django.core.exceptions import ValidationError

# Maximum allowed file size in Megabytes
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt']
DISALLOWED_EXTENSIONS_MAP = {
    '.doc': "Legacy '.doc' format is not supported. Please convert and upload a '.docx', '.pdf', or '.txt' file.",
    '.exe': "Executable files are strictly forbidden.",
    '.sh': "Script files are strictly forbidden.",
    '.bat': "Script files are strictly forbidden.",
    '.zip': "Archive files are not supported. Please upload an uncompressed PDF, DOCX, or TXT file.",
    '.rar': "Archive files are not supported. Please upload an uncompressed PDF, DOCX, or TXT file.",
}


def validate_file_size(file_obj):
    """
    Validates that the uploaded file does not exceed the maximum allowed size (5MB)
    and is not completely empty.
    """
    if not file_obj:
        raise ValidationError("No file was uploaded.")

    if file_obj.size == 0:
        raise ValidationError("Uploaded file is empty (0 bytes).")

    if file_obj.size > MAX_FILE_SIZE_BYTES:
        size_in_mb = round(file_obj.size / (1024 * 1024), 2)
        raise ValidationError(
            f"File size ({size_in_mb}MB) exceeds the maximum allowed limit of {MAX_FILE_SIZE_MB}MB."
        )


def validate_file_extension(file_obj):
    """
    Validates that the file has a permitted extension (.pdf, .docx, .txt).
    """
    filename = getattr(file_obj, 'name', '')
    if not filename:
        raise ValidationError("Uploaded file has no filename.")

    _, ext = os.path.splitext(filename.lower())

    if ext in DISALLOWED_EXTENSIONS_MAP:
        raise ValidationError(DISALLOWED_EXTENSIONS_MAP[ext])

    if ext not in ALLOWED_EXTENSIONS:
        allowed_str = ", ".join(ALLOWED_EXTENSIONS)
        raise ValidationError(
            f"Unsupported file extension '{ext}'. Allowed extensions are: {allowed_str}."
        )


def validate_resume_file(file_obj):
    """
    Composite validator running both size and extension checks.
    """
    validate_file_size(file_obj)
    validate_file_extension(file_obj)
