import re

COLUMN_MAP = {
    "location_id": [
        "sondagem", "furo", "bh", "id", "loc", "borehole"
    ],
    "depth_top": [
        "topo", "profundidade inicial", "depth top", "z inicial"
    ],
    "depth_base": [
        "base", "profundidade final", "depth base", "z final"
    ],
    "depth": [
        "profundidade", "depth", "z"
    ],
    "n_spt": [
        "n spt", "nspt", "golpes"
    ],
    "soil_desc": [
        "solo", "descrição", "material", "camada"
    ]
}

def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())
