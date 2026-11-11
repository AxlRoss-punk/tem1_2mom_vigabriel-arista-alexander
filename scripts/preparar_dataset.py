#!/usr/bin/env python3
"""Crea una copia UTF-8 sin BOM y demuestra que conserva el CSV original."""

import argparse
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADER = [
    "Row ID", "Order ID", "Order Date", "Ship Date", "Ship Mode",
    "Customer ID", "Customer Name", "Segment", "Country", "City", "State",
    "Postal Code", "Region", "Product ID", "Category", "Sub-Category",
    "Product Name", "Sales", "Quantity", "Discount", "Profit",
]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def parse_csv(text):
    rows = list(csv.reader(io.StringIO(text, newline=""), strict=True))
    if not rows or rows[0] != HEADER:
        raise ValueError("La cabecera no coincide con las 21 columnas esperadas.")
    for position, row in enumerate(rows[1:], 1):
        if len(row) != len(HEADER):
            raise ValueError(f"El registro {position} no tiene 21 campos.")
        if any("\r" in field or "\n" in field for field in row):
            raise ValueError("Hay campos multilínea; revisar la estrategia de ingesta.")
        for index in (2, 3):
            datetime.strptime(row[index], "%m/%d/%Y")
    if len(rows) - 1 != 9994:
        raise ValueError("El archivo no contiene los 9.994 registros esperados.")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "datos/preparados/superstore_utf8.csv")
    parser.add_argument("--report", type=Path,
                        default=ROOT / "evidencias/preparacion_ingesta.json")
    args = parser.parse_args()
    source, output, report = (p.resolve() for p in
                              (args.source, args.output, args.report))
    if len({source, output, report}) != 3:
        parser.error("Origen, copia e informe deben tener rutas diferentes.")
    for destination in (output, report):
        if ROOT not in destination.parents:
            parser.error("Los destinos deben quedar dentro de este repositorio.")
        if destination.exists():
            parser.error(f"Se rechaza sobrescribir un archivo existente: {destination}")

    original_bytes = source.read_bytes()
    original_hash = sha256(original_bytes)
    text = original_bytes.decode("cp1252", errors="strict")
    if text.encode("cp1252", errors="strict") != original_bytes:
        raise ValueError("La interpretación Windows-1252 no es reversible.")
    original_rows = parse_csv(text)
    utf8_bytes = text.encode("utf-8", errors="strict")
    if utf8_bytes.startswith(b"\xef\xbb\xbf"):
        raise ValueError("La copia no debe contener BOM.")

    output.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as destination:
        destination.write(utf8_bytes)

    saved_bytes = output.read_bytes()
    saved_text = saved_bytes.decode("utf-8", errors="strict")
    saved_rows = parse_csv(saved_text)
    if saved_text != text or saved_rows != original_rows:
        raise ValueError("La copia no conserva todos los valores del origen.")
    if sha256(source.read_bytes()) != original_hash:
        raise ValueError("El hash del original cambió durante la operación.")

    data = saved_rows[1:]
    metrics = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "source_encoding_assumption": "Windows-1252, inferida del contenido",
        "source_sha256": original_hash,
        "source_bytes": len(original_bytes),
        "output": str(output.relative_to(ROOT)),
        "output_encoding": "UTF-8 sin BOM",
        "output_sha256": sha256(saved_bytes),
        "output_bytes": len(saved_bytes),
        "data_records": len(data),
        "columns": HEADER,
        "header_preserved": True,
        "line_endings_preserved": True,
        "all_fields_equal": saved_rows == original_rows,
        "source_unchanged": True,
        "empty_fields": sum(field == "" for row in data for field in row),
        "product_fields_with_commas": sum("," in row[16] for row in data),
        "product_fields_with_quotes": sum('"' in row[16] for row in data),
        "product_fields_with_nbsp": sum("\u00a0" in row[16] for row in data),
        "product_fields_with_outer_spaces": sum(
            row[16] != row[16].strip() for row in data),
        "four_digit_postal_records": sum(len(row[11]) == 4 for row in data),
        "leading_zero_postal_records": sum(row[11].startswith("0") for row in data),
        "transformations": ["Recodificación reversible de Windows-1252 a UTF-8"],
        "values_cleaned": False,
    }
    with report.open("x", encoding="utf-8", newline="\n") as destination:
        json.dump(metrics, destination, ensure_ascii=False, indent=2)
        destination.write("\n")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
