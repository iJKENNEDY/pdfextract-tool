# INSTRUCCIONES DE USO - PDF Extract Tool

## Instalación Rápida

```bash
# Instalar dependencias obligatorias
pip install PyPDF2 PyMuPDF Pillow

# Opcional: para aplicación web
pip install Flask
```

## Ejecución

### Opción 1: GUI (Recomendado para usuarios finales)

```bash
python gui_main.py
```

La GUI abre una ventana con dos pestañas:
- **Extractor de Páginas**: Extrae páginas específicas
- **Conversor a JPG**: Convierte PDFs a imágenes

### Opción 2: CLI - Extracción de Páginas

```bash
# Uso básico
python cli_extract.py entrada.pdf salida.pdf "1-3,5,7-9"

# Con información detallada
python cli_extract.py entrada.pdf salida.pdf "1-10" --verbose

# Ver ayuda
python cli_extract.py --help
```

**Ejemplos de formato de páginas:**
- `"1"` → Solo página 1
- `"1-5"` → Páginas 1 a 5
- `"1,3,5"` → Páginas 1, 3, 5
- `"1-3,5,7-9"` → Páginas 1, 2, 3, 5, 7, 8, 9

### Opción 3: CLI - Conversión a JPG

```bash
# Convertir un PDF
python cli_convert.py archivo.pdf

# Convertir todos los PDFs en una carpeta
python cli_convert.py ./pdfs --output ./imagenes

# Controlar calidad y resolución
python cli_convert.py ./pdfs --zoom 2.0 --quality 95 --verbose

# Ver ayuda
python cli_convert.py --help
```

**Opciones de zoom:**
- `1.0` = 72 DPI (baja resolución)
- `2.0` = 144 DPI (recomendado)
- `3.0` = 216 DPI (alta)
- `4.0` = 288 DPI (muy alta)

## Uso Desde Python

```python
from src.services import PDFExtractor, PDFToImageConverter

# EXTRACCIÓN
result = PDFExtractor.extract_from_string(
    'entrada.pdf',
    'salida.pdf',
    '1-5,10'
)

if result['success']:
    print(f"✓ {result['message']}")
else:
    print(f"✗ {result['error']}")

# CONVERSIÓN
result = PDFToImageConverter.convert_pdf_to_jpg(
    'documento.pdf',
    './salida',
    zoom=2.0,
    quality=95
)

if result['success']:
    print(f"✓ {result['message']}")
    print(f"Directorio: {result['output_directory']}")
else:
    print(f"✗ {result['error']}")

# INFORMACIÓN DEL PDF
info = PDFExtractor.get_pdf_info('documento.pdf')
print(f"Total de páginas: {info['total_pages']}")
print(f"Tamaño: {info['file_size']} bytes")
```

## Personalización

Edita `src/config/settings.py` para:

```python
# Cambiar resolución predeterminada
PDF_TO_JPG_CONFIG = {
    "zoom": 3.0,  # Más alto = más detalles
    "quality": 95,  # Más alto = mejor calidad
}

# Cambiar colores de la GUI
GUI_CONFIG = {
    "theme_primary": "#2c3e50",
    "theme_secondary": "#3498db",
    "theme_success": "#27ae60",
    "theme_danger": "#e74c3c",
}

# Cambiar directorios
PDF_INPUT_DIR = Path("data/pdfs")
IMAGE_OUTPUT_DIR = Path("output/imagenes_jpg")
PDF_OUTPUT_DIR = Path("output/pdfs_extraidos")
```

## Estructura del Proyecto

```
pdfextract/
├── gui_main.py                 ← Ejecuta la GUI
├── cli_extract.py              ← CLI para extracción
├── cli_convert.py              ← CLI para conversión
│
├── src/
│   ├── config/settings.py      ← Configuración centralizada
│   ├── services/
│   │   ├── pdf_extractor.py    ← Lógica de extracción
│   │   └── pdf_converter.py    ← Lógica de conversión
│   └── ui/gui_main.py          ← Interfaz gráfica
│
├── data/pdfs/                  ← Tus PDFs aquí
├── output/
│   ├── pdfs_extraidos/         ← PDFs procesados
│   └── imagenes_jpg/           ← Imágenes generadas
│
└── README.md                   ← Documentación principal
```

## Solución de Problemas

| Problema | Solución |
|----------|----------|
| ModuleNotFoundError: PyPDF2 | `pip install PyPDF2` |
| ModuleNotFoundError: fitz | `pip install PyMuPDF` |
| ModuleNotFoundError: tkinter | Viene con Python, en Linux: `apt install python3-tk` |
| Archivo no encontrado | Verifica la ruta completa o relativa del PDF |
| Páginas inválidas | Formato debe ser `"1-3,5"` sin espacios |
| PDF corrupto | El archivo puede estar protegido o dañado |

## Ejemplos Prácticos

### Ejemplo 1: Extraer primeras 5 páginas

```bash
python cli_extract.py documento.pdf primeras5.pdf "1-5"
```

### Ejemplo 2: Extraer específicas

```bash
python cli_extract.py documento.pdf especiales.pdf "1,5,10,15-20"
```

### Ejemplo 3: Convertir a alta resolución

```bash
python cli_convert.py documento.pdf --zoom 4.0 --quality 100
```

### Ejemplo 4: Procesar lote de PDFs

```bash
python cli_convert.py ./carpeta_pdfs --zoom 2.0
```

## Características Principales

✓ **Extracción flexible** - Rangos individuales o combinados
✓ **Conversión de calidad** - Control total de resolución y compresión
✓ **Interfaz moderna** - GUI atractiva y fácil de usar
✓ **CLI potente** - Automatización desde terminal
✓ **Arquitectura limpia** - Código modular y reutilizable
✓ **Sin dependencias pesadas** - Librerías ligeras
✓ **Multiplataforma** - Windows, Linux, macOS

## Contacto y Soporte

Para reportar bugs o solicitar características, consulta el README.md
