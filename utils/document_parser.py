import io
import fitz  # PyMuPDF

def parse_document(file_bytes: bytes, file_name: str) -> str:
    """
    Extract text from a document based on its extension.
    Currently supports: .pdf, .txt
    """
    ext = file_name.lower().split('.')[-1]
    
    if ext == 'pdf':
        return _parse_pdf(file_bytes)
    elif ext in ['txt', 'md', 'csv']:
        return _parse_text(file_bytes)
    else:
        # Fallback for unsupported formats
        return f"[Unsupported document type: {ext}]"

def _parse_pdf(file_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        return "\n".join(text_parts)
    except Exception as e:
        return f"[Error parsing PDF: {e}]"

def _parse_text(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        # Try a more forgiving decoding if utf-8 fails
        return file_bytes.decode('latin-1', errors='replace')
