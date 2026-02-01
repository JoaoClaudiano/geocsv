// URL do backend no Streamlit Cloud
const API_URL = "https://geocsv.streamlit.app";

// ----------------- Funções utilitárias -----------------
async function postData(endpoint, data) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`Erro HTTP ${response.status}`);
    }

    return await response.json();
  } catch (err) {
    console.error(`Erro ao enviar para ${endpoint}:`, err);
    alert(`Erro ao enviar para ${endpoint}: ${err}`);
  }
}

function getLocationData() {
  const rows = document.querySelectorAll("#location-table tbody tr");
  return Array.from(rows).map(row => {
    const inputs = row.querySelectorAll("input");
    return {
      location_id: inputs[0].value,
      east: inputs[1].value,
      north: inputs[2].value,
      ground_level: inputs[3].value,
      final_depth: inputs[4].value
    };
  });
}

function getGeologyData() {
  const rows = document.querySelectorAll("#geology-table tbody tr");
  return Array.from(rows).map(row => {
    const inputs = row.querySelectorAll("input, select");
    return {
      location_id: inputs[0].value,
      depth_top: inputs[1].value,
      depth_base: inputs[2].value,
      geology_code: inputs[3].value,
      description: inputs[4].value
    };
  });
}

function downloadFile(filename, content) {
  const blob = new Blob([content], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ----------------- Função upload PDF -----------------
async function uploadPDF() {
  const input = document.getElementById("pdf-input");
  if (!input.files.length) {
    alert("Selecione um PDF");
    return;
  }

  const formData = new FormData();
  formData.append("file", input.files[0]);

  try {
    const response = await fetch(`${API_URL}/upload/pdf`, {
      method: "POST",
      body: formData
    });

    if (!response.ok) throw new Error(`Erro HTTP ${response.status}`);

    const data = await response.json();
    window.lastPdfText = data.text_preview; // salva para sugestão OCR

    document.getElementById("pdf-status").innerText =
      `Fonte do PDF: ${data.source === "ocr" ? "PDF escaneado (OCR)" : "PDF vetorial"}`;

    document.getElementById("output").textContent =
      JSON.stringify(data.text_preview.pages.slice(0, 2), null, 2);
  } catch (err) {
    console.error("Erro ao enviar PDF:", err);
    alert(`Erro ao enviar PDF: ${err}`);
  }
}

// ----------------- Aplicar sugestão OCR -----------------
async function applyOcrSuggestion() {
  if (!window.lastPdfText) {
    alert("Nenhum PDF carregado");
    return;
  }

  const response = await postData("/suggest/from-ocr", window.lastPdfText);
  if (!response) return;

  response.suggested_layers.forEach(layer => {
    addGeologyRow();
    const row = document.querySelector("#geology-table tbody tr:last-child");
    const inputs = row.querySelectorAll("input, select");

    inputs[0].value = layer.location_id || "";
    inputs[1].value = layer.depth_top || "";
    inputs[2].value = layer.depth_base || "";
    inputs[3].value = layer.geology_code || "";
    inputs[4].value = layer.description || "";
  });
}

// ----------------- Validar dados -----------------
async function validateData() {
  const locations = getLocationData();
  const layers = getGeologyData();

  const result = await postData("/data/validate", { locations, layers });
  document.getElementById("output").textContent = JSON.stringify(result, null, 2);
}

// ----------------- Exportar CSV -----------------
async function exportCSV() {
  const locations = getLocationData();
  const layers = getGeologyData();

  const result = await postData("/export/civil3d", { locations, layers });
  if (!result) return;

  downloadFile("Location Details.csv", result["Location Details.csv"]);
  downloadFile("Field Geological Descriptions.csv", result["Field Geological Descriptions.csv"]);

  document.getElementById("output").textContent = "CSV gerados com sucesso!";
}

// ----------------- Adicionar linhas -----------------
function addGeologyRow() {
  const tbody = document.querySelector("#geology-table tbody");
  const row = tbody.insertRow();
  for (let i = 0; i < 5; i++) {
    const cell = row.insertCell();
    const input = document.createElement("input");
    cell.appendChild(input);
  }
}

function addLocationRow() {
  const tbody = document.querySelector("#location-table tbody");
  const row = tbody.insertRow();
  for (let i = 0; i < 5; i++) {
    const cell = row.insertCell();
    const input = document.createElement("input");
    cell.appendChild(input);
  }
}

// ----------------- Dark Mode -----------------
const toggleBtn = document.getElementById("dark-mode-toggle");
toggleBtn.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");
  toggleBtn.textContent = document.body.classList.contains("dark-mode") ? "Light Mode" : "Dark Mode";
});
