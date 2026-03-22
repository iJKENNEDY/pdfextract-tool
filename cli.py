#!/usr/bin/env python3
"""CLI unificada para PDF Extract Tool."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def _load_defaults():
    try:
        from src.config.settings import (
            IMAGE_CONVERT_OUTPUT_DIR,
            IMAGE_OUTPUT_DIR,
            IMAGE_TO_PDF_OUTPUT_DIR,
            PDF_TO_JPG_CONFIG,
        )

        return {
            "img_out": str(IMAGE_OUTPUT_DIR),
            "img2pdf_out": str(IMAGE_TO_PDF_OUTPUT_DIR),
            "img_convert_out": str(IMAGE_CONVERT_OUTPUT_DIR),
            "zoom": PDF_TO_JPG_CONFIG.get("zoom", 2.0),
            "quality": PDF_TO_JPG_CONFIG.get("quality", 95),
        }
    except ModuleNotFoundError:
        return {
            "img_out": "output/imagenes_jpg",
            "img2pdf_out": "output/pdf_generados_desde_imagenes",
            "img_convert_out": "output/imagenes_convertidas",
            "zoom": 2.0,
            "quality": 95,
        }


def build_parser() -> argparse.ArgumentParser:
    defaults = _load_defaults()
    parser = argparse.ArgumentParser(description="CLI unificada: extract, pdf2jpg, img2pdf, imgconvert")
    sub = parser.add_subparsers(dest="command", required=True)

    p_extract = sub.add_parser("extract", help="Extraer paginas de PDF")
    p_extract.add_argument("entrada", help="PDF de entrada")
    p_extract.add_argument("salida", help="PDF de salida")
    p_extract.add_argument("paginas", help="Rango: 1-3,5,7-9")
    p_extract.add_argument("-v", "--verbose", action="store_true")

    p_pdf2jpg = sub.add_parser("pdf2jpg", help="Convertir PDF(s) a JPG")
    p_pdf2jpg.add_argument("entrada", help="PDF o carpeta con PDFs")
    p_pdf2jpg.add_argument("-o", "--output", default=defaults["img_out"], help="Directorio salida")
    p_pdf2jpg.add_argument("-z", "--zoom", type=float, default=defaults["zoom"], help="Zoom 1.0-4.0")
    p_pdf2jpg.add_argument("-q", "--quality", type=int, default=defaults["quality"], help="Calidad 1-100")
    p_pdf2jpg.add_argument("-r", "--range", dest="pages_range", default="", help="Rango de paginas")
    p_pdf2jpg.add_argument("-v", "--verbose", action="store_true")

    p_img2pdf = sub.add_parser("img2pdf", help="Convertir imagen(es) a PDF")
    p_img2pdf.add_argument("entradas", nargs="+", help="Imagenes o carpetas")
    p_img2pdf.add_argument("-o", "--output", default=defaults["img2pdf_out"], help="Directorio salida")
    p_img2pdf.add_argument("-n", "--name", default="imagenes_convertidas", help="Nombre base del PDF")
    p_img2pdf.add_argument("-r", "--range", dest="range_str", default="", help="Rango de hojas")
    p_img2pdf.add_argument("-v", "--verbose", action="store_true")

    p_imgconvert = sub.add_parser("imgconvert", help="Convertir imagen(es) entre formatos")
    p_imgconvert.add_argument("entradas", nargs="+", help="Imagenes o carpetas")
    p_imgconvert.add_argument("-t", "--to", required=True, help="Formato destino (jpg,png,webp,avif,ico,bmp,tiff)")
    p_imgconvert.add_argument("-o", "--output", default=defaults["img_convert_out"], help="Directorio salida")
    p_imgconvert.add_argument("-q", "--quality", type=int, default=95, help="Calidad para formatos con compresion")
    p_imgconvert.add_argument("-v", "--verbose", action="store_true")

    return parser


def run_extract(args) -> int:
    try:
        from src.services.pdf_extractor import PDFExtractor
    except ModuleNotFoundError as exc:
        print(f"❌ Dependencia faltante: {exc}")
        return 1

    in_path = Path(args.entrada)
    if not in_path.exists():
        print(f"❌ Error: no existe '{args.entrada}'")
        return 1

    if args.verbose:
        print(f"📄 Entrada: {args.entrada}")
        print(f"📤 Salida: {args.salida}")
        print(f"📋 Paginas: {args.paginas}")

    result = PDFExtractor.extract_from_string(args.entrada, args.salida, args.paginas)
    if result.get("success"):
        print(f"✅ {result['message']}")
        print(f"📁 Archivo: {result['output_path']}")
        return 0
    print(f"❌ Error: {result.get('error', 'desconocido')}")
    return 1


def run_pdf2jpg(args) -> int:
    try:
        from src.services.pdf_converter import PDFToImageConverter
    except ModuleNotFoundError as exc:
        print(f"❌ Dependencia faltante: {exc}")
        return 1

    src_path = Path(args.entrada)
    if not src_path.exists():
        print(f"❌ Error: no existe '{args.entrada}'")
        return 1

    pages_range = args.pages_range.strip() or None
    if src_path.is_file():
        result = PDFToImageConverter.convert_pdf_to_jpg(
            str(src_path),
            args.output,
            zoom=args.zoom,
            quality=args.quality,
            pages_range=pages_range,
        )
    else:
        if pages_range:
            print("⚠️ Aviso: --range solo aplica a un PDF individual. Se ignorara en modo carpeta.")
        result = PDFToImageConverter.convert_batch_pdfs(
            str(src_path),
            args.output,
            zoom=args.zoom,
            quality=args.quality,
        )

    if result.get("success"):
        print(f"✅ {result['message']}")
        print(f"📁 Salida: {result['output_directory']}")
        return 0
    print(f"❌ Error: {result.get('error', 'desconocido')}")
    return 1


def run_img2pdf(args) -> int:
    try:
        from src.services.image_to_pdf_converter import ImageToPDFConverter
    except ModuleNotFoundError as exc:
        print(f"❌ Dependencia faltante: {exc}")
        return 1

    images = []
    for entry in args.entradas:
        try:
            found = ImageToPDFConverter.list_images_from_path(entry)
            images.extend(str(i) for i in found)
            if args.verbose:
                print(f"📂 {entry}: {len(found)} imagen(es)")
        except Exception as exc:
            print(f"⚠️ Omitido '{entry}': {exc}")

    if not images:
        print("❌ No hay imagenes validas")
        return 1

    result = ImageToPDFConverter.convert_images_to_pdf(
        image_paths=images,
        output_dir=args.output,
        output_name=args.name,
        range_str=args.range_str,
    )
    if result.get("success"):
        print(f"✅ {result['message']}")
        print(f"📁 Archivo: {result['output_path']}")
        return 0
    print(f"❌ Error: {result.get('error', 'desconocido')}")
    return 1


def run_imgconvert(args) -> int:
    try:
        from src.services.image_format_converter import ImageFormatConverter
    except ModuleNotFoundError as exc:
        print(f"❌ Dependencia faltante: {exc}")
        return 1

    images = []
    for entry in args.entradas:
        try:
            found = ImageFormatConverter.list_images_from_path(entry)
            images.extend(str(i) for i in found)
            if args.verbose:
                print(f"📂 {entry}: {len(found)} imagen(es)")
        except Exception as exc:
            print(f"⚠️ Omitido '{entry}': {exc}")

    if not images:
        print("❌ No hay imagenes validas")
        return 1

    result = ImageFormatConverter.convert_images(
        image_paths=images,
        output_dir=args.output,
        target_format=args.to,
        quality=args.quality,
    )
    if result.get("success"):
        print(f"✅ {result['message']}")
        print(f"📁 Salida: {result['output_directory']}")
        return 0

    print(f"❌ Error: {result.get('error', 'desconocido')}")
    return 1


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "extract":
        return run_extract(args)
    if args.command == "pdf2jpg":
        return run_pdf2jpg(args)
    if args.command == "img2pdf":
        return run_img2pdf(args)
    if args.command == "imgconvert":
        return run_imgconvert(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
