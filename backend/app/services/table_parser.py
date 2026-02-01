import camelot

def extract_tables(pdf_path: str) -> list:
    tables = camelot.read_pdf(pdf_path, pages="all")

    extracted = []

    for i, table in enumerate(tables):
        extracted.append({
            "table_id": i + 1,
            "rows": table.df.values.tolist()
        })

    return extracted
