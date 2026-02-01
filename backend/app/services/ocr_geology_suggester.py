def suggest_layers_from_ocr(rows: list[dict], location_id="BH-01") -> list[dict]:
    layers = []

    rows = sorted(rows, key=lambda r: r["depth"])

    for i in range(len(rows) - 1):
        layers.append({
            "location_id": location_id,
            "depth_top": rows[i]["depth"],
            "depth_base": rows[i + 1]["depth"],
            "geology_code": "",
            "description": rows[i]["description"]
        })

    return layers
