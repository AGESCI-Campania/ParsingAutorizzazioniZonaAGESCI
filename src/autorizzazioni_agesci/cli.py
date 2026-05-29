"""CLI entry point for autorizzazioni-agesci."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

if __package__:
    from .parser import parse_year
else:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from autorizzazioni_agesci.parser import parse_year

_FIELDS = [
    "codice_socio",
    "nome",
    "gruppo",
    "codice_gruppo",
    "unita",
    "branca",
    "genere_unita",
    "genere",
    "livello_foca",
    "funzione",
    "anno",
]


def _write_csv(records: list[dict], out_path: Path) -> None:
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDS)
        writer.writeheader()
        writer.writerows(records)


def _write_json(records: list[dict], out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="autorizzazioni",
        description="Estrae le autorizzazioni AGESCI dai PDF e le salva in CSV/JSON.",
    )
    parser.add_argument(
        "--anno",
        type=int,
        default=None,
        help="Anno da elaborare (default: il più recente trovato).",
    )
    parser.add_argument(
        "--formato",
        choices=["csv", "json"],
        default="csv",
        help="Formato dell'output: csv (default) o json.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/input"),
        help="Cartella radice degli input (default: data/input).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/output"),
        help="Cartella di destinazione (default: data/output).",
    )
    args = parser.parse_args(argv)

    try:
        records = parse_year(args.input, args.anno)
    except FileNotFoundError as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 1

    if not records:
        print("Nessun record trovato.", file=sys.stderr)
        return 1

    anno = records[0]["anno"]
    args.output.mkdir(parents=True, exist_ok=True)
    out_path = args.output / f"{anno}.{args.formato}"

    if args.formato == "json":
        _write_json(records, out_path)
    else:
        _write_csv(records, out_path)

    print(f"Scritti {len(records)} record in {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
