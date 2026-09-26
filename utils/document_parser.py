import io
import zipfile
import xml.etree.ElementTree as ET

try:
    import pymupdf as fitz
except ImportError:
    import fitz


def parse_document(file_bytes: bytes, file_name: str) -> str:
    """
    Extract text from a document based on its extension.
    Supports: .pdf, .docx, .doc, .txt, .md, .csv, .rtf
    """
    ext = file_name.lower().split('.')[-1]
    
    if ext == 'pdf':
        return _parse_pdf(file_bytes)
    elif ext == 'docx':
        return _parse_docx(file_bytes)
    elif ext in ['txt', 'md', 'csv', 'rtf', 'log']:
        return _parse_text(file_bytes)
    else:
        # Fallback: attempt UTF-8 text decoding first before failing
        try:
            return _parse_text(file_bytes)
        except Exception:
            return f"[Unsupported document type: .{ext}]"


def _parse_pdf(file_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            t = page.get_text()
            if t:
                text_parts.append(t.strip())
        return "\n\n".join(text_parts)
    except Exception as e:
        return f"[Error parsing PDF: {e}]"


def _parse_docx(file_bytes: bytes) -> str:
    """Extract text from Word .docx file using standard library zipfile + XML."""
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            if 'word/document.xml' not in z.namelist():
                return "[Error parsing DOCX: word/document.xml missing]"
            xml_content = z.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            
            paragraphs = []
            # In OpenXML, paragraphs are w:p
            for p in tree.iter():
                if p.tag.endswith('}p'):
                    texts = [node.text for node in p.iter() if node.tag.endswith('}t') and node.text]
                    if texts:
                        paragraphs.append(''.join(texts))
            
            if not paragraphs:
                # Fallback: collect all text elements
                texts = [node.text for node in tree.iter() if node.tag.endswith('}t') and node.text]
                return '\n'.join(texts)
                
            return '\n\n'.join(paragraphs)
    except Exception as e:
        return f"[Error parsing DOCX: {e}]"


def _parse_text(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return file_bytes.decode('latin-1', errors='replace')
