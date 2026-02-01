import streamlit as st
import pandas as pd
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from io import BytesIO, StringIO
import camelot
import os

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
source_type = None
ocr_text = None

def extract_text(pdf_bytes):
    # Tenta pdf vetorial
    text_pages = []
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text_pages.append(page.extract_text() or "")
    text_combined = "\n".join(text_pages).strip()
    if text_combined:
        return "vetorial", text_pages
    # Se vazio, aplica OCR
    images = convert_from_bytes(pdf_bytes)
    ocr_pages = []
    for img in images:
        ocr_pages.append(pytesseract.image_to_string(img))
    return "ocr", ocr_pages

if uploaded_file:
    with st.spinner("Processando PDF..."):
        try:
            pdf_bytes = uploaded_file.read()
            source_type, pdf_text_preview = extract_text(pdf_bytes)
            st.success(f"PDF processado! Tipo: {source_type.upper()}")
        except Exception as e:
            st.error(f"Erro ao processar PDF: {e}")

# Preview das primeiras 2 páginas
if pdf_text_preview:
    st.subheader("Pré-visualização do PDF (primeiras 2 páginas)")
    for i, page in enumerate(pdf_text_preview[:2]):
        st.text_area(f"Página {i+1}", page, height=150)

# -------------------------------
# 2️⃣ Sugestão automática de camadas
st.subheader("2️⃣ Sugestão de camadas (OCR)")
suggested_layers = []

if pdf_text_preview and st.button("Aplicar sugestão automática"):
    with st.spinner("Gerando sugestões..."):
        try:
            text_for_suggestion = "\n".join(pdf_text_preview)
            # Aqui você aplica sua lógica de parse
            # Exemplo dummy: uma camada fictícia
            suggested_layers = [
                {
                    "location_id": "BH-01",
                    "depth_top": 0.0,
                    "depth_base": 2.5,
                    "geology_code": "ARG",
                    "description": "Argila"
                }
            ]
            st.success(f"{len(suggested_layers)} camada(s) sugerida(s)")
        except Exception as e:
            st.error(f"Erro ao gerar sugestão: {e}")

# -------------------------------
# 3️⃣ Tabelas editáveis
st.subheader("3️⃣ Inserir / Editar dados manualmente")

# Locations
st.markdown("**Tabela de Localizações (Location Details)**")
if "locations_df" not in st.session_state:
    st.session_state["locations_df"] = pd.DataFrame(
        columns=["location_id", "east", "north", "ground_level", "final_depth"]
    )

# Atualização necessária para Streamlit recente
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

# Preenche com sugestões
if suggested_layers and st.button("Adicionar sugestões à tabela"):
    for layer in suggested_layers:
        st.session_state["geology_df"] = pd.concat([
            st.session_state["geology_df"], pd.DataFrame([layer])
        ], ignore_index=True)

geology_df = st.data_editor(
    st.session_state["geology_df"], num_rows="dynamic"
)
st.session_state["geology_df"] = geology_df

# -------------------------------
# 4️⃣ Validar dados
st.subheader("4️⃣ Validar dados")
if st.button("Validar"):
    try:
        # Exemplo: validação simples
        loc_ids = set(locations_df["location_id"])
        errors = []
        for i, row in geology_df.iterrows():
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
        # Locations CSV
        loc_csv = locations_df.to_csv(index=False)
        geo_csv = geology_df.to_csv(index=False)
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
