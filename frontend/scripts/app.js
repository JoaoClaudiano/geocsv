async function validateData() {
  const locations = getLocationData();
  const layers = getGeologyData();

  const result = await postData("/data/validate", {
    locations,
    layers
  });

  document.getElementById("output").textContent =
    JSON.stringify(result, null, 2);
}

async function exportCSV() {
  const locations = getLocationData();
  const layers = getGeologyData();

  const result = await postData("/export/civil3d", {
    locations,
    layers
  });

  document.getElementById("output").textContent = result["Location Details.csv"];

  downloadFile("Location Details.csv", result["Location Details.csv"]);
  downloadFile(
    "Field Geological Descriptions.csv",
    result["Field Geological Descriptions.csv"]
  );
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

async function uploadPDF() {
  const input = document.getElementById("pdf-input");
  if (!input.files.length) {
    alert("Selecione um PDF");
    return;
  }

  const formData = new FormData();
  formData.append("file", input.files[0]);

  const response = await fetch(`${API_URL}/upload/pdf`, {
    method: "POST",
    body: formData
  });

  const data = await response.json();

  document.getElementById("output").textContent =
    JSON.stringify(data, null, 2);
}

async function applySuggestion(table) {
  const response = await postData("/suggest/from-table", table);

  response.suggested_layers.forEach(layer => {
    addGeologyRow();
    const row = document.querySelector(
      "#geology-table tbody tr:last-child"
    );
    const inputs = row.querySelectorAll("input, select");

    inputs[0].value = layer.location_id;
    inputs[1].value = layer.depth_top;
    inputs[2].value = layer.depth_base;
    inputs[4].value = layer.description;
  });
}

