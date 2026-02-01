from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import parse
app.include_router(parse.router)

from app.routes import upload
app.include_router(upload.router)

app = FastAPI(
    title="Geo CSV",
    description="Conversor de relatórios geotécnicos PDF para CSV compatível com Autodesk Civil 3D",
    version="0.1.0"
)

# CORS (frontend no GitHub Pages)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois restringimos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Geo CSV"}
