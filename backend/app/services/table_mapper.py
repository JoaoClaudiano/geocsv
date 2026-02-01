from app.services.column_mapper import COLUMN_MAP, normalize

def map_table_headers(header_row: list[str]) -> dict:
    mapping = {}

    normalized_headers = [normalize(h) for h in header_row]

    for field, aliases in COLUMN_MAP.items():
        for i, header in enumerate(normalized_headers):
            for alias in aliases:
                if normalize(alias) in header:
                    mapping[field] = i
                    break

    return mapping
