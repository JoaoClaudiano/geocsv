from fastapi import APIRouter
from app.services.table_mapper import map_table_headers
from app.services.geology_suggester import suggest_layers

router = APIRouter(prefix="/suggest", tags=["Suggestions"])

@router.post("/from-table")
def suggest_from_table(table: dict):
    rows = table.get("rows", [])
    if len(rows) < 2:
        return {"layers": []}

    header = rows[0]
    data_rows = rows[1:]

    mapping = map_table_headers(header)
    layers = suggest_layers(data_rows, mapping)

    return {
        "mapping_detected": mapping,
        "suggested_layers": layers
    }
