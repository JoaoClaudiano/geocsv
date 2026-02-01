import streamlit as st
import pandas as pd
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from io import BytesIO
import camelot
import re

# -------------------------------
# Configuração da página
st.set_page_config(
    page_title="Geo CSV",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Geo CSV - PDF → CSV para Civil 3D")
st.markdown(
    "Converta relatórios geotécnicos PDF em arquivos CSV compatíveis com Autodesk Civil 3D."
)

# -------------------------------
# Sidebar - Dark Mode
dark_mode = st.sidebar.checkbox("Dark Mode", value=False)
if dark_mode:
    st.markdown(
        """
        <style>
        body {background-color:#222; color:#eee;}
        table, th, td {color:#eee;}
        </style>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# Upload PDF
st.subheader("1️⃣ Upload do PDF")
uploaded_file = st.file_uploader("Selecione o arquivo PDF", type="pdf")

pdf_text_preview = None

def extract_text(pdf_bytes):
    """Tenta ler texto vetorial; se vazio, aplica OCR."""
    text_pages = []
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text_pages.append(page.extract_text() or "")
    combined_text = "\n".join(text_pages).strip()
    if combined_text:
        return "vetorial", text_pages
    # fallback OCR
    images = convert_from_bytes(pdf_bytes)
    ocr_pages = []
    for img in images:
        ocr_pages.append(pytesseract.image_to_string(img))
    return "ocr", ocr_pages

def parse_pdf_to_tables(pdf_text_pages):
    """
    Extrai locations e geologia, separando por location_id.
    """
    locations = []
    geologies = []

    combined_text = "\n".join(pdf_text_pages)

    # Detecta blocos de sondagem
    sondagem_blocks = re.split(r"(SP-\d+)", combined_text)
    # o split retorna ['', 'SP-04', ' conteúdo ', 'SP-05', ' conteúdo ', ...]
    for i in range(1, len(sondagem_blocks), 2):
        location_id = sondagem_blocks[i].strip()
        content = sondagem_blocks[i+1].strip()

        # Extrai coordenadas (E e N)
        coord_match = re.search(r"E[:\s]+([\d.,]+).*?N[:\s]+([\d.,]+)", content, re.DOTALL)
        east = float(coord_match.group(1).replace(",", ".")) if coord_match else None
        north = float(coord_match.group(2).replace(",", ".")) if coord_match else None
        locations.append({
            "location_id": location_id,
            "east": east,
            "north": north,
            "ground_level": None,
            "final_depth": None
        })

        # Extrai camadas geológicas
        # Exemplo: linhas com profundidade top/base e descrição
        layer_matches = re.findall(r"([\d.,]+)\s*-\s*([\d.,]+)\s*-\s*(.*)", content)
        for lm in layer_matches:
            try:
                geologies.append({
                    "location_id": location_id,
                    "depth_top": float(lm[0].replace(",", ".")),
                    "depth_base": float(lm[1].replace(",", ".")),
                    "geology_code": "",
                    "description": lm[2].strip()
                })
            except:
                continue

    return pd.DataFrame(locations), pd.DataFrame(geologies)

if uploaded_file:
    with st.spinner("Processando PDF..."):
        pdf_bytes = uploaded_file.read()
        source_type, pdf_text_preview = extract_text(pdf_bytes)
        st.success(f"PDF processado! Tipo: {source_type.upper()}")

        # Tenta camelot se PDF for vetorial
        locations_df = None
        geology_df = None
        if source_type == "vetorial":
            try:
                tables = camelot.read_pdf(BytesIO(pdf_bytes), pages='all', flavor='stream')
                if tables:
                    st.info(f"{len(tables)} tabela(s) detectada(s) via Camelot")
                    # Aqui você pode escolher a primeira tabela ou implementar lógica para várias
                    table = tables[0].df
                    table.columns = ["location_id", "depth_top", "depth_base", "geology_code", "description"]
                    geology_df = table
            except:
                st.warning("Falha ao extrair tabela com Camelot, usando parsing de texto.")

        if geology_df is None:
            # Fallback para parsing de texto
            locations_df, geology_df = parse_pdf_to_tables(pdf_text_preview)

        st.session_state["locations_df"] = locations_df
        st.session_state["geology_df"] = geology_df

# -------------------------------
# 3️⃣ Tabelas editáveis
st.subheader("3️⃣ Inserir / Editar dados manualmente")

# Locations
st.markdown("**Tabela de Localizações (Location Details)**")
if "locations_df" not in st.session_state:
    st.session_state["locations_df"] = pd.DataFrame(
        columns=["location_id", "east", "north", "ground_level", "final_depth"]
    )
locations_df = st.data_editor(
    st.session_state["locations_df"], num_rows="dynamic"
)
st.session_state["locations_df"] = locations_df

# Geology
st.markdown("**Tabela de Geologia (Field Geological Descriptions)**")
if "geology_df" not in st.session_state:
    st.session_state["geology_df"] = pd.DataFrame(
        columns=["location_id", "depth_top", "depth_base", "geology_code", "description"]
    )
geology_df = st.data_editor(
    st.session_state["geology_df"], num_rows="dynamic"
)
st.session_state["geology_df"] = geology_df

# -------------------------------
# 4️⃣ Validar dados
st.subheader("4️⃣ Validar dados")
if st.button("Validar"):
    try:
        loc_ids = set(st.session_state["locations_df"]["location_id"])
        errors = []
        for i, row in st.session_state["geology_df"].iterrows():
            if row["location_id"] not in loc_ids:
                errors.append(f"Geology row {i+1}: location_id não existe em Locations")
        if errors:
            st.error("\n".join(errors))
        else:
            st.success("Todos os dados estão válidos!")
    except Exception as e:
        st.error(f"Erro na validação: {e}")

# -------------------------------
# 5️⃣ Exportar CSV
st.subheader("5️⃣ Exportar CSV")
if st.button("Exportar CSV"):
    try:
        loc_csv = st.session_state["locations_df"].to_csv(index=False)
        geo_csv = st.session_state["geology_df"].to_csv(index=False)
        st.download_button("Download Location Details.csv", loc_csv, file_name="Location Details.csv")
        st.download_button("Download Field Geological Descriptions.csv", geo_csv, file_name="Field Geological Descriptions.csv")
        st.success("CSV gerados com sucesso!")
    except Exception as e:
        st.error(f"Erro ao exportar CSV: {e}")

# -------------------------------
# Footer
st.markdown(
    "<hr><p style='text-align:center; font-size:0.8em'>Geo CSV - Desenvolvido por João Claudiano</p>",
    unsafe_allow_html=True
)
