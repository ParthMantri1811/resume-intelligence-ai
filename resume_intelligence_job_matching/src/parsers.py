from io import BytesIO
from pathlib import Path
import fitz
from docx import Document

def extract_text(data: bytes, filename: str) -> str:
    ext=Path(filename).suffix.lower()
    if ext==".pdf":
        doc=fitz.open(stream=data,filetype="pdf")
        return "\n".join(page.get_text("text") for page in doc)
    if ext==".docx":
        doc=Document(BytesIO(data))
        parts=[p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows: parts.append(" | ".join(c.text for c in row.cells))
        return "\n".join(parts)
    if ext==".txt": return data.decode("utf-8",errors="ignore")
    raise ValueError("Unsupported file type.")
