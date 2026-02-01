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
