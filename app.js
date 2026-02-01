// ===============================================
// app.js — frontend para GeoCSV Bridge
// ===============================================

// URL do backend (local para testes)
const API_URL = "http://localhost:8000";

// ===============================================
// Funções auxiliares
// ===============================================

function getLocationData() {
  const rows = document.querySelectorAll("#location-table tbody tr");
  return Array.from(rows).map(row => {
    const inputs = row.querySelectorAll("input, select");
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

async function postData(endpoint, payload) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error("Erro na requisição");
    return await response.json();
  } catch (err) {
    console.error(err);
    alert("Erro na comunicação com o backend. Veja o console.");
  }
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

// ===============================================
// Validação e exportação CSV
// ===============================================

async function validateData() {
  const locations = getLocationData();
  const layers = getGeologyData();

  const result = await postData("/data/validate", { locations, layers });
  document.getElementById("output").textContent =
    JSON.stringify(result, null, 2);
}

async function exportCSV() {
  const locations = getLocationData();
  const layers = getGeologyData();

  const result = await postData("/export/civil3d", { locations, layers });

  if (!result) return;

  document.getElementById("output").textContent =
    "CSV gerados com sucesso!";

  downloadFile("Location Details.csv", result["Location Details.csv"]);
  downloadFile(
    "Field Geological Descriptions.csv",
    result["Field Geological Descriptions.csv"]
  );
}

// ===============================================
// Upload PDF e OCR
// ===============================================

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

    if (!response.ok) throw new Error("Erro no upload do PDF");

    const data = await response.json();

    // salvar globalmente para sugestões OCR
    window.lastPdfText = data.text_preview;

    // atualizar status
    document.getElementById("pdf-status").innerText =
      `Fonte do PDF: ${data.source === "ocr" ? "PDF escaneado (OCR)" : "PDF vetorial"}`;

    // mostrar preview das duas primeiras páginas
    document.getElementById("output").textContent =
      JSON.stringify(data.text_preview.pages.slice(0, 2), null, 2);

  } catch (error) {
    console.error("Erro ao enviar PDF:", error);
    alert("Erro ao enviar PDF. Veja o console.");
  }
}

// ===============================================
// Aplicar sugestões do OCR
// ===============================================

async function applyOcrSuggestion() {
  if (!window.lastPdfText) {
    alert("Nenhum PDF OCR carregado");
    return;
  }

  const response = await postData("/suggest/from-ocr", window.lastPdfText);
  if (!response) return;

  response.suggested_layers.forEach(layer => {
    addGeologyRow(); // função já existente para adicionar linha
    const row = document.querySelector("#geology-table tbody tr:last-child");
    const inputs = row.querySelectorAll("input, select");

    inputs[0].value = layer.location_id;
    inputs[1].value = layer.depth_top;
    inputs[2].value = layer.depth_base;
    inputs[3].value = layer.geology_code;
    inputs[4].value = layer.description;
  });
}

// ===============================================
// Aplicar sugestões manuais de tabela
// ===============================================

async function applySuggestion(table) {
  const response = await postData("/suggest/from-table", table);
  if (!response) return;

  response.suggested_layers.forEach(layer => {
    addGeologyRow();
    const row = document.querySelector("#geology-table tbody tr:last-child");
    const inputs = row.querySelectorAll("input, select");

    inputs[0].value = layer.location_id;
    inputs[1].value = layer.depth_top;
    inputs[2].value = layer.depth_base;
    inputs[3].value = layer.geology_code;
    inputs[4].value = layer.description;
  });
}



