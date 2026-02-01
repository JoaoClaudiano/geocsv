from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import io
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
import csv

# Criar app primeiro
app = FastAPI(
    title="Geo CSV",
    description="Conversor de relatórios geotécnicos PDF para CSV compatível com Autodesk Civil 3D",
    version="0.1.0"
)

# CORS (permitir frontend do GitHub Pages)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois pode restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- HEALTH CHECK -----------------
@app.get("/")
def health_check():
    return {"status": "ok", "service": "Geo CSV"}

# ----------------- UPLOAD PDF -----------------
@app.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    content = await file.read()
    text_pages = []

    try:
        # Tenta abrir PDF vetorial
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                text_pages.append(page.extract_text() or "")
        source = "vetorial"
    except Exception:
        # PDF escaneado → OCR
        images = convert_from_bytes(content)
        for img in images:
            text_pages.append(pytesseract.image_to_string(img))
        source = "ocr"

    return JSONResponse({
        "source": source,
        "filename": file.filename,
        "text_preview": {
            "pages": text_pages
        }
    })

# ----------------- SUGESTÃO OCR -----------------
@app.post("/suggest/from-ocr")
async def suggest_from_ocr(text_data: dict):
    """
    Recebe JSON com texto do PDF e retorna lista de camadas sugeridas.
    """
    suggested_layers = []

    pages = text_data.get("pages", [])
    for page in pages:
        lines = page.split("\n")
        for line in lines:
            # heurística simples: procurar BH-xx e números
            if "BH-" in line:
                parts = line.split()
                loc_id = parts[0]
                depth_top = parts[1] if len(parts) > 1 else "0"
                depth_base = parts[2] if len(parts) > 2 else "1"
                geology_code = parts[3] if len(parts) > 3 else "ARG"
                description = " ".join(parts[4:]) if len(parts) > 4 else ""
                suggested_layers.append({
                    "location_id": loc_id,
                    "depth_top": depth_top,
                    "depth_base": depth_base,
                    "geology_code": geology_code,
                    "description": description
                })

    return {"suggested_layers": suggested_layers}

# ----------------- VALIDAR DADOS -----------------
@app.post("/data/validate")
async def validate_data(payload: dict):
    locations = payload.get("locations", [])
    layers = payload.get("layers", [])
    errors = []

    # Exemplo: verificar se Location IDs batem
    location_ids = {loc.get("location_id") for loc in locations}
    for layer in layers:
        if layer.get("location_id") not in location_ids:
            errors.append(f"Layer Location ID {layer.get('location_id')} não encontrado em Locations.")

    return {"valid": len(errors) == 0, "errors": errors}

# ----------------- EXPORTAR CSV CIVIL 3D -----------------
@app.post("/export/civil3d")
async def export_civil3d(payload: dict):
    locations = payload.get("locations", [])
    layers = payload.get("layers", [])

    # Gera CSV Location Details
    loc_output = io.StringIO()
    loc_writer = csv.writer(loc_output)
    loc_writer.writerow(["Location ID", "East", "North", "Ground Level", "Final Depth"])
    for loc in locations:
        loc_writer.writerow([
            loc.get("location_id", ""),
            loc.get("east", ""),
            loc.get("north", ""),
            loc.get("ground_level", ""),
            loc.get("final_depth", "")
        ])

    # Gera CSV Field Geological Descriptions
    geo_output = io.StringIO()
    geo_writer = csv.writer(geo_output)
    geo_writer.writerow(["Location ID", "Depth Top", "Depth Base", "Geology Code", "Description"])
    for layer in layers:
        geo_writer.writerow([
            layer.get("location_id", ""),
            layer.get("depth_top", ""),
            layer.get("depth_base", ""),
            layer.get("geology_code", ""),
            layer.get("description", "")
        ])

    return {
        "Location Details.csv": loc_output.getvalue(),
        "Field Geological Descriptions.csv": geo_output.getvalue()
    }
