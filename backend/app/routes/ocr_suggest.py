from fastapi import APIRouter

from app.services.ocr_table_parser import parse_ocr_text_to_rows
from app.services.ocr_geology_suggester import suggest_layers_from_ocr

router = APIRouter(prefix="/suggest", tags=["OCR Suggestions"])

@router.post("/from-ocr")
def suggest_from_ocr(text_data: dict):
    pages = text_data.get("pages", [])

    rows = parse_ocr_text_to_rows(pages)
    layers = suggest_layers_from_ocr(rows)

    return {
        "rows_detected": rows,
        "suggested_layers": layers
    }
