"""Configuracion centralizada del proyecto."""

from pathlib import Path

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"

# Compatibilidad con estructura previa (si existen carpetas raiz, se reutilizan)
LEGACY_PDF_DIR = PROJECT_ROOT / "pdfs"
LEGACY_IMG_DIR = PROJECT_ROOT / "imagenes_jpg"

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Directorios de entrada/salida
PDF_INPUT_DIR = LEGACY_PDF_DIR if LEGACY_PDF_DIR.exists() else DATA_DIR / "pdfs"
IMAGE_OUTPUT_DIR = LEGACY_IMG_DIR if LEGACY_IMG_DIR.exists() else OUTPUT_DIR / "imagenes_jpg"
PDF_OUTPUT_DIR = OUTPUT_DIR / "pdfs_extraidos"
IMAGE_TO_PDF_OUTPUT_DIR = OUTPUT_DIR / "pdf_generados_desde_imagenes"
IMAGE_CONVERT_OUTPUT_DIR = OUTPUT_DIR / "imagenes_convertidas"
PDF_MERGE_OUTPUT_DIR = OUTPUT_DIR / "pdf_unidos"

# Crear directorios si no existen
for directory in [
    DATA_DIR,
    PDF_INPUT_DIR,
    OUTPUT_DIR,
    IMAGE_OUTPUT_DIR,
    PDF_OUTPUT_DIR,
    IMAGE_TO_PDF_OUTPUT_DIR,
    IMAGE_CONVERT_OUTPUT_DIR,
    PDF_MERGE_OUTPUT_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuración de conversión PDF a JPG
PDF_TO_JPG_CONFIG = {
    "zoom": 2.0,              # Factor de zoom (1.0=72dpi, 2.0=144dpi, 3.0=216dpi)
    "quality": 95,            # Calidad del JPG (1-100)
    "format": "JPEG",         # Formato de salida
    "optimize": True,         # Optimizar imagen
}

# Configuración de GUI
GUI_CONFIG = {
    "title": "PDF Extract Tool",
    "window_width": 980,
    "window_height": 760,
    "theme_bg": "#f0f0f0",
    "theme_primary": "#2c3e50",
    "theme_secondary": "#3498db",
    "theme_success": "#27ae60",
    "theme_danger": "#e74c3c",
    "font_main": ("Segoe UI", 10),
    "font_title": ("Segoe UI", 14, "bold"),
    "font_button": ("Segoe UI", 10),
}

# Configuración de Flask
FLASK_CONFIG = {
    "debug": True,
    "host": "127.0.0.1",
    "port": 5000,
    "upload_folder": str(PDF_INPUT_DIR),
    "max_content_length": 50 * 1024 * 1024,  # 50MB máximo
}

# Mensajes de la aplicación
MESSAGES = {
    "select_pdf": "Selecciona un archivo PDF",
    "extract_success": "Extracción completada exitosamente",
    "extraction_error": "Error durante la extracción",
    "convert_success": "Conversión completada exitosamente",
    "conversion_error": "Error durante la conversión",
    "invalid_pages": "Formato de páginas inválido",
    "no_pages_selected": "Debes seleccionar al menos una página",
}
