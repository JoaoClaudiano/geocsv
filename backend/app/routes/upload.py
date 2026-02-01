import tempfile
from fastapi import APIRouter, UploadFile, File

from app.services.pdf_dispatcher import read_pdf_smart
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

    text_data = read_pdf_smart(tmp_path)

    tables = []
    if text_data.get("source") == "vector":
        tables = extract_tables(tmp_path)

    return {
        "filename": file.filename,
        "source": text_data.get("source"),
        "text_preview": text_data,
        "tables": tables
    }
