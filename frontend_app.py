import streamlit as st
import requests
import pandas as pd
from io import StringIO, BytesIO

# ------------------------------------------
# Configurações da página
st.set_page_config(
    page_title="Geo CSV - PDF to Civil3D",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Geo CSV - Conversor de Relatórios Geotécnicos PDF para CSV")
st.markdown(
    "Carregue um relatório geotécnico em PDF e gere arquivos CSV compatíveis com Autodesk Civil 3D."
)

# ------------------------------------------
# Sidebar - Dark mode toggle
dark_mode = st.sidebar.checkbox("Dark Mode", value=False)
if dark_mode:
    st.markdown(
        """
        <style>
        body {background-color:#222; color:#eee;}
        table {color:#eee;}
        </style>
        """, unsafe_allow_html=True
    )

# ------------------------------------------
# Upload PDF
st.subheader("1️⃣ Upload do PDF")
uploaded_file = st.file_uploader("Selecione o arquivo PDF", type="pdf")

pdf_text_preview = None

if uploaded_file:
    with st.spinner("Enviando PDF..."):
        try:
            files = {"file": uploaded_file.getvalue()}
            response = requests.post("https://geocsv.streamlit.app/upload/pdf", files={"file": uploaded_file})
            response.raise_for_status()
            data = response.json()
            source_type = "PDF escaneado (OCR)" if data["source"] == "ocr" else "PDF vetorial"
            st.success(f"PDF enviado com sucesso! Tipo: {source_type}")
            pdf_text_preview = data["text_preview"]
        except Exception as e:
            st.error(f"Erro ao enviar PDF: {e}")

# Mostrar preview do PDF (primeiras 2 páginas)
if pdf_text_preview:
    st.subheader("Pré-visualização do PDF (primeiras 2 páginas)")
    for i, page in enumerate(pdf_text_preview["pages"][:2]):
        st.text_area(f"Página {i+1}", page, height=150)

# ------------------------------------------
# 2️⃣ Sugerir camadas via OCR
st.subheader("2️⃣ Sugestão automática de camadas (opcional)")

if pdf_text_preview:
    if st.button("Aplicar sugestão OCR"):
        try:
            response = requests.post(
                "https://geocsv.streamlit.app/suggest/from-ocr",
                json=pdf_text_preview
            )
            response.raise_for_status()
            layers_suggested = response.json()["suggested_layers"]
            st.success(f"{len(layers_suggested)} camadas sugeridas")
        except Exception as e:
            st.error(f"Erro ao gerar sugestões: {e}")
else:
    layers_suggested = []

# ------------------------------------------
# 3️⃣ Tabelas editáveis
st.subheader("3️⃣ Inserir / Editar dados manualmente")

# Locations table
st.markdown("**Tabela de Localizações (Location Details)**")
if "locations_df" not in st.session_state:
    st.session_state["locations_df"] = pd.DataFrame(
        columns=["location_id", "east", "north", "ground_level", "final_depth"]
    )
locations_df = st.experimental_data_editor(st.session_state["locations_df"], num_rows="dynamic")
st.session_state["locations_df"] = locations_df

# Geology table
st.markdown("**Tabela de Geologia (Field Geological Descriptions)**")
if "geology_df" not in st.session_state:
    st.session_state["geology_df"] = pd.DataFrame(
        columns=["location_id", "depth_top", "depth_base", "geology_code", "description"]
    )
geology_df = st.experimental_data_editor(st.session_state["geology_df"], num_rows="dynamic")
st.session_state["geology_df"] = geology_df

# ------------------------------------------
# 4️⃣ Validar dados
st.subheader("4️⃣ Validar dados")
if st.button("Validar"):
    try:
        payload = {
            "locations": locations_df.to_dict(orient="records"),
            "layers": geology_df.to_dict(orient="records")
        }
        response = requests.post("https://geocsv.streamlit.app/data/validate", json=payload)
        response.raise_for_status()
        result = response.json()
        st.json(result)
    except Exception as e:
        st.error(f"Erro ao validar: {e}")

# ------------------------------------------
# 5️⃣ Exportar CSV
st.subheader("5️⃣ Exportar CSV")
if st.button("Exportar CSV"):
    try:
        payload = {
            "locations": locations_df.to_dict(orient="records"),
            "layers": geology_df.to_dict(orient="records")
        }
        response = requests.post("https://geocsv.streamlit.app/export/civil3d", json=payload)
        response.raise_for_status()
        result = response.json()

        # Download CSVs
        loc_csv = result["Location Details.csv"]
        geo_csv = result["Field Geological Descriptions.csv"]

        st.download_button("Download Location Details.csv", loc_csv, file_name="Location Details.csv")
        st.download_button("Download Field Geological Descriptions.csv", geo_csv, file_name="Field Geological Descriptions.csv")
        st.success("CSV gerados com sucesso!")
    except Exception as e:
        st.error(f"Erro ao exportar CSV: {e}")

# ------------------------------------------
# Footer
st.markdown(
    "<hr><p style='text-align:center; font-size:0.8em'>Geo CSV - Desenvolvido por João Claudiano</p>",
    unsafe_allow_html=True
)
