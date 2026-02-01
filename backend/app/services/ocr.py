import pytesseract
from pdf2image import convert_from_path

def ocr_pdf(pdf_path: str) -> dict:
    pages = convert_from_path(pdf_path, dpi=300)

    extracted_pages = []

    for i, image in enumerate(pages):
        text = pytesseract.image_to_string(
            image,
            lang="por"
        )

        extracted_pages.append({
            "page": i + 1,
            "text": text.strip()
        })

    return {
        "pages": extracted_pages,
        "pages_count": len(extracted_pages),
        "source": "ocr"
    }
