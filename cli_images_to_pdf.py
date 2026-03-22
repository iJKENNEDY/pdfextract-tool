#!/usr/bin/env python3
"""Convertidor CLI de imagenes a PDF."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def create_parser():
    """Crea parser de argumentos."""
    try:
        from src.config.settings import IMAGE_TO_PDF_OUTPUT_DIR
    except ModuleNotFoundError:
        IMAGE_TO_PDF_OUTPUT_DIR = Path("output") / "pdf_generados_desde_imagenes"

    parser = argparse.ArgumentParser(
        description="Convertir una o varias imagenes a PDF"
    )
    parser.add_argument(
        "entradas",
        nargs="+",
        help="Rutas de imagenes o directorios con imagenes",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=str(IMAGE_TO_PDF_OUTPUT_DIR),
        help="Directorio de salida para PDFs generados",
    )
    parser.add_argument(
        "--name",
        "-n",
        default="imagenes_convertidas",
        help="Nombre base del PDF de salida",
    )
    parser.add_argument(
        "--range",
        "-r",
        dest="range_str",
        default="",
        help="Rango de hojas a incluir (ej: 1-3,5). Vacio = todas",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Mostrar informacion detallada",
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        from src.services.image_to_pdf_converter import ImageToPDFConverter
    except ModuleNotFoundError as exc:
        print(f"❌ Dependencia faltante: {exc}. Instala los requisitos del proyecto.")
        sys.exit(1)

    all_images = []
    for input_path in args.entradas:
        try:
            found = ImageToPDFConverter.list_images_from_path(input_path)
            all_images.extend(str(p) for p in found)
            if args.verbose:
                print(f"📂 {input_path}: {len(found)} imagen(es)")
        except Exception as exc:
            print(f"⚠️  Omitiendo '{input_path}': {exc}")

    if not all_images:
        print("❌ No se encontraron imagenes validas para convertir")
        sys.exit(1)

    if args.verbose:
        print(f"🧩 Total imagenes detectadas: {len(all_images)}")
        print(f"📄 Rango: {args.range_str or 'todo'}")
        print(f"📁 Salida: {args.output}")
        print(f"📝 Nombre base: {args.name}")

    def progress(current, total, filename):
        if args.verbose:
            print(f"   [{current}/{total}] {filename}")

    result = ImageToPDFConverter.convert_images_to_pdf(
        image_paths=all_images,
        output_dir=args.output,
        output_name=args.name,
        range_str=args.range_str,
        progress_callback=progress,
    )

    if result.get("success"):
        print(f"✅ {result['message']}")
        print(f"📁 Archivo generado: {result['output_path']}")
        sys.exit(0)

    print(f"❌ Error: {result.get('error', 'Error desconocido')}")
    sys.exit(1)


if __name__ == "__main__":
    main()
