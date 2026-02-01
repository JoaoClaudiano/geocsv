from typing import List
from app.models.geology import GeologicalLayer

def validate_layers(layers: List[GeologicalLayer]) -> list[str]:
    errors = []

    # Agrupar por sondagem
    layers_by_location = {}
    for layer in layers:
        layers_by_location.setdefault(layer.location_id, []).append(layer)

    for location_id, loc_layers in layers_by_location.items():
        loc_layers.sort(key=lambda l: l.depth_top)

        for i in range(len(loc_layers)):
            layer = loc_layers[i]

            if layer.depth_base <= layer.depth_top:
                errors.append(
                    f"[{location_id}] Depth Base <= Depth Top ({layer.depth_top}–{layer.depth_base})"
                )

            if i > 0:
                prev = loc_layers[i - 1]
                if layer.depth_top < prev.depth_base:
                    errors.append(
                        f"[{location_id}] Sobreposição entre camadas ({prev.depth_base} e {layer.depth_top})"
                    )

    return errors
