#!/usr/bin/env python3
"""
Interfaz de Línea de Comandos (CLI) para PDF Extract Tool
Script de entrada para modo CLI
"""
import argparse
import sys
from pathlib import Path

# Agregar raiz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def create_parser():
    """Crea el parser de argumentos"""
    parser = argparse.ArgumentParser(
        description='Extractor de páginas PDF - Herramienta CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python cli_extract.py input.pdf output.pdf "1-3,5,7-9"
  python cli_extract.py input.pdf output.pdf "1,2,3"
  python cli_extract.py input.pdf output.pdf "1-10"
        """
    )
    
    parser.add_argument('entrada', help='Ruta al archivo PDF de entrada')
    parser.add_argument('salida', help='Ruta al archivo PDF de salida')
    parser.add_argument('paginas', help='Páginas a extraer (ej: 1-3,5,7-9)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Mostrar información detallada')
    
    return parser


def main():
    """Función principal"""
    parser = create_parser()
    args = parser.parse_args()

    try:
        from src.services.pdf_extractor import PDFExtractor
    except ModuleNotFoundError as exc:
        print(f"❌ Dependencia faltante: {exc}. Instala los requisitos del proyecto.")
        sys.exit(1)
    
    # Validar archivos
    input_path = Path(args.entrada)
    if not input_path.exists():
        print(f"❌ Error: El archivo '{args.entrada}' no existe")
        sys.exit(1)
    
    if args.verbose:
        print(f"📄 Archivo de entrada: {args.entrada}")
        print(f"📤 Archivo de salida: {args.salida}")
        print(f"📋 Páginas: {args.paginas}")
        print()
    
    # Ejecutar extracción
    result = PDFExtractor.extract_from_string(args.entrada, args.salida, args.paginas)
    
    if result["success"]:
        print(f"✅ {result['message']}")
        if args.verbose:
            print(f"   Páginas extraídas: {result['pages_extracted']}")
            print(f"   Total de páginas en PDF: {result['total_pages']}")
        sys.exit(0)
    else:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
