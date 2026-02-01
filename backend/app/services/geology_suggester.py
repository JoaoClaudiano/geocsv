def suggest_layers(rows, mapping, location_id="BH-01"):
    layers = []

    depth_col = mapping.get("depth")
    soil_col = mapping.get("soil_desc")

    if depth_col is None or soil_col is None:
        return []

    for i in range(len(rows) - 1):
        depth_top = rows[i][depth_col]
        depth_base = rows[i + 1][depth_col]
        desc = rows[i][soil_col]

        try:
            layers.append({
                "location_id": location_id,
                "depth_top": float(depth_top),
                "depth_base": float(depth_base),
                "geology_code": "",
                "description": desc
            })
        except ValueError:
            continue

    return layers
