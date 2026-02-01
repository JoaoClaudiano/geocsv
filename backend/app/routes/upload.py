import tempfile
from fastapi import APIRouter, UploadFile, File

from app.services.pdf_reader import extract_text
from app.services.table_parser import extract_tables

router = APIRouter(prefix="/upload", tags=["PDF Upload"])

@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Arquivo não é PDF"}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    text_data = extract_text(tmp_path)
    table_data = extract_tables(tmp_path)

    return {
        "filename": file.filename,
        "text_preview": text_data,
        "tables": table_data
    }
