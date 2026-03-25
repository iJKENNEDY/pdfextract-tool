#!/usr/bin/env python3
"""
Convertidor de PDF a JPG
Script de entrada para conversión batch
"""
import argparse
import sys
from pathlib import Path

# Agregar raiz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def create_parser():
    """Crea el parser de argumentos"""
    try:
        from src.config.settings import IMAGE_OUTPUT_DIR, PDF_TO_JPG_CONFIG
    except ModuleNotFoundError:
        IMAGE_OUTPUT_DIR = Path("output") / "imagenes_jpg"
        PDF_TO_JPG_CONFIG = {"zoom": 2.0, "quality": 95}

    parser = argparse.ArgumentParser(
        description='Convertidor de PDF a JPG'
    )
    
    parser.add_argument('entrada', nargs='?', default=str(Path(__file__).resolve().parent.parent / 'data' / 'pdfs'),
                       help='Ruta al archivo PDF o carpeta con PDFs')
    parser.add_argument('--output', '-o', default=str(IMAGE_OUTPUT_DIR),
                       help='Directorio de salida para las imágenes')
    parser.add_argument('--zoom', '-z', type=float, default=PDF_TO_JPG_CONFIG['zoom'],
                       help='Factor de zoom (1.0=72dpi, 2.0=144dpi, 3.0=216dpi)')
    parser.add_argument('--quality', '-q', type=int, default=PDF_TO_JPG_CONFIG['quality'],
                       help='Calidad JPG (1-100)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Mostrar información detallada')
    
    return parser


def main():
    """Función principal"""
    parser = create_parser()
    args = parser.parse_args()

    try:
        from src.services.pdf_converter import PDFToImageConverter
    except ModuleNotFoundError as exc:
        print(f"❌ Dependencia faltante: {exc}. Instala los requisitos del proyecto.")
        sys.exit(1)
    
    input_path = Path(args.entrada)
    
    # Validar entrada
    if not input_path.exists():
        print(f"❌ Error: La ruta '{args.entrada}' no existe")
        sys.exit(1)
    
    if args.verbose:
        print(f"📁 Entrada: {args.entrada}")
        print(f"📁 Salida: {args.output}")
        print(f"🎨 Zoom: {args.zoom}x | Calidad: {args.quality}%")
        print()
    
    # Decidir si es archivo o carpeta
    if input_path.is_file():
        # Procesar un archivo
        result = PDFToImageConverter.convert_pdf_to_jpg(
            str(input_path),
            args.output,
            zoom=args.zoom,
            quality=args.quality
        )
        
        if result["success"]:
            print(f"✅ {result['message']}")
            if args.verbose:
                print(f"   Páginas guardadas: {result['saved_pages']}/{result['total_pages']}")
                print(f"   Directorio: {result['output_directory']}")
        else:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
    
    else:
        # Procesar carpeta
        result = PDFToImageConverter.convert_batch_pdfs(
            str(input_path),
            args.output,
            zoom=args.zoom,
            quality=args.quality
        )
        
        if result["success"]:
            print(f"✅ {result['message']}")
            if args.verbose:
                print(f"   PDFs procesados: {result['successful_pdfs']}/{result['total_pdfs']}")
                print(f"   Total de páginas: {result['total_pages']}")
                print(f"   Páginas guardadas: {result['total_saved']}")
                print(f"   Directorio: {result['output_directory']}")
        else:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()
