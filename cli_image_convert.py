#!/usr/bin/env python3
"""CLI para convertir imagenes entre formatos."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def create_parser():
    try:
        from src.config.settings import IMAGE_CONVERT_OUTPUT_DIR
    except ModuleNotFoundError:
        IMAGE_CONVERT_OUTPUT_DIR = Path("output") / "imagenes_convertidas"

    parser = argparse.ArgumentParser(description="Convertir imagenes a otro formato")
    parser.add_argument("entradas", nargs="+", help="Archivos o carpetas de imagenes")
    parser.add_argument("--to", "-t", required=True, help="Formato destino: jpg,png,webp,avif,ico,bmp,tiff")
    parser.add_argument("--output", "-o", default=str(IMAGE_CONVERT_OUTPUT_DIR), help="Directorio salida")
    parser.add_argument("--quality", "-q", type=int, default=95, help="Calidad para formatos con compresion")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mostrar detalle")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        from src.services.image_format_converter import ImageFormatConverter
    except ModuleNotFoundError as exc:
        print(f"❌ Dependencia faltante: {exc}")
        sys.exit(1)

    images = []
    for entry in args.entradas:
        try:
            found = ImageFormatConverter.list_images_from_path(entry)
            images.extend(str(p) for p in found)
            if args.verbose:
                print(f"📂 {entry}: {len(found)} imagen(es)")
        except Exception as exc:
            print(f"⚠️ Omitido '{entry}': {exc}")

    if not images:
        print("❌ No se encontraron imagenes validas")
        sys.exit(1)

    def progress(current, total, filename):
        if args.verbose:
            print(f"   [{current}/{total}] {filename}")

    result = ImageFormatConverter.convert_images(
        image_paths=images,
        output_dir=args.output,
        target_format=args.to,
        quality=args.quality,
        progress_callback=progress,
    )

    if result.get("success"):
        print(f"✅ {result['message']}")
        print(f"📁 Salida: {result['output_directory']}")
        sys.exit(0)

    print(f"❌ Error: {result.get('error', 'desconocido')}")
    sys.exit(1)


if __name__ == "__main__":
    main()
