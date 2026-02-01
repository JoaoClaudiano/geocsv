import re

def looks_like_depth(value: str) -> bool:
    return bool(re.match(r"^\d+[.,]?\d*$", value))

def clean_number(value: str) -> float | None:
    try:
        return float(value.replace(",", "."))
    except:
        return None

def parse_ocr_text_to_rows(pages: list[dict]) -> list[dict]:
    """
    Recebe páginas OCR e tenta reconstruir linhas estruturadas:
    profundidade | Nspt | descrição
    """
    rows = []

    for page in pages:
        lines = page["text"].splitlines()

        for line in lines:
            parts = re.split(r"\s{2,}", line.strip())

            if len(parts) < 3:
                continue

            depth = clean_number(parts[0])
            nspt = clean_number(parts[1])

            if depth is None or nspt is None:
                continue

            description = " ".join(parts[2:])

            rows.append({
                "depth": depth,
                "n_spt": nspt,
                "description": description
            })

    return rows
