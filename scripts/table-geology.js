function addGeologyRow() {
  const tbody = document.querySelector("#geology-table tbody");

  const row = document.createElement("tr");
  row.innerHTML = `
    <td><input /></td>
    <td><input type="number" /></td>
    <td><input type="number" /></td>
    <td>
      <select>
        <option value="">---</option>
        <option value="ARG">ARG</option>
        <option value="ARE">ARE</option>
        <option value="SIL">SIL</option>
      </select>
    </td>
    <td><input /></td>
    <td><button onclick="this.parentElement.parentElement.remove()">🗑</button></td>
  `;

  tbody.appendChild(row);
}

function getGeologyData() {
  const rows = document.querySelectorAll("#geology-table tbody tr");
  return Array.from(rows).map(row => {
    const inputs = row.querySelectorAll("input, select");
    return {
      location_id: inputs[0].value,
      depth_top: parseFloat(inputs[1].value),
      depth_base: parseFloat(inputs[2].value),
      geology_code: inputs[3].value,
      description: inputs[4].value
    };
  });
}
