function addLocationRow() {
  const tbody = document.querySelector("#location-table tbody");

  const row = document.createElement("tr");
  row.innerHTML = `
    <td><input /></td>
    <td><input type="number" /></td>
    <td><input type="number" /></td>
    <td><input type="number" /></td>
    <td><input type="number" /></td>
    <td><button onclick="this.parentElement.parentElement.remove()">🗑</button></td>
  `;

  tbody.appendChild(row);
}

function getLocationData() {
  const rows = document.querySelectorAll("#location-table tbody tr");
  return Array.from(rows).map(row => {
    const cells = row.querySelectorAll("input");
    return {
      location_id: cells[0].value,
      east: parseFloat(cells[1].value),
      north: parseFloat(cells[2].value),
      ground_level: parseFloat(cells[3].value),
      final_depth: parseFloat(cells[4].value)
    };
  });
}
