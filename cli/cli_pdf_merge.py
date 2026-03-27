#!/usr/bin/env python3
"""CLI para unir multiples archivos PDF."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def create_parser():
    try:
        from src.config.settings import PDF_MERGE_OUTPUT_DIR
    except ModuleNotFoundError:
        PDF_MERGE_OUTPUT_DIR = Path("output") / "pdf_unidos"

    parser = argparse.ArgumentParser(description="Unir 2 o mas archivos PDF en uno")
    parser.add_argument("entradas", nargs="+", help="Lista de archivos PDF a unir (min 2)")
    parser.add_argument("--output", "-o", default=str(PDF_MERGE_OUTPUT_DIR / "merge.pdf"), help="Ruta PDF de salida")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mostrar detalle")
    return parser


def main():
    args = create_parser().parse_args()

    try:
        from src.services.pdf_merger import PDFMergerService
    except ModuleNotFoundError as exc:
        print(f"❌ Dependencia faltante: {exc}")
        sys.exit(1)

    if len(args.entradas) < 2:
        print("❌ Debes enviar al menos 2 PDFs")
        sys.exit(1)

    if args.verbose:
        print(f"📚 PDFs a unir: {len(args.entradas)}")
        for item in args.entradas:
            print(f"   - {item}")
        print(f"📤 Salida: {args.output}")

    result = PDFMergerService.merge_pdfs(args.entradas, args.output)
    if result.get("success"):
        print(f"✅ {result['message']}")
        print(f"📁 Archivo: {result['output_path']}")
        sys.exit(0)

    print(f"❌ Error: {result.get('error', 'desconocido')}")
    sys.exit(1)


if __name__ == "__main__":
    main()
