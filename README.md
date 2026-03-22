# PDF Extract Tool

Herramienta moderna y versátil para manipulación de archivos PDF con arquitectura de software escalable.

## Descripción General

PDF Extract Tool es una aplicación completa que proporciona múltiples interfaces (CLI y GUI) para:
- **Extracción de páginas**: Extrae rangos específicos o páginas individuales de PDFs
- **Conversión a imágenes**: Convierte páginas de PDF a JPG de alta calidad
- **Conversión de imágenes a PDF**: Une una o varias imágenes en PDF
- **Conversión de imágenes a otros formatos**: Convierte entre JPG, PNG, WEBP, AVIF, ICO, BMP, TIFF (según compatibilidad)
- **Procesamiento por lotes**: Procesa múltiples archivos simultáneamente

## Características Principales

✂️ **Extracción Flexible**
- Soporta rangos: `1-3`, `5`, `7-9`
- Combinación de rangos: `1-3,5,7-9`
- Validación automática de páginas

🖼️ **Conversión de Alta Calidad**
- Zoom configurable (72 DPI a 288 DPI)
- Calidad JPG ajustable (1-100)
- Rango de páginas (por defecto todas)
- Progreso visual de conversión

🧩 **Imágenes a PDF**
- Convierte una o varias imágenes a PDF
- Soporta rango de hojas (por defecto todo)
- Cola de conversiones múltiples
- Drag & drop de archivos y carpetas (si el entorno lo soporta)
- Evita reemplazos con nombres enumerados

🖌️ **Imágenes a Otros Formatos**
- Convierte imágenes sueltas o carpetas completas
- Soporta formatos comunes: `jpg`, `png`, `webp`, `avif`, `ico`, `bmp`, `tiff`
- Respeta compatibilidad real de Pillow y codecs instalados
- Muestra progreso y resumen de salida

🎯 **Múltiples Interfaces**
- **GUI**: Interfaz gráfica moderna con Tkinter
- **CLI**: Herramientas de línea de comandos para automatización

⚙️ **Arquitectura Profesional**
- Código modular y reutilizable
- Configuración centralizada
- Manejo robusto de errores
- Procesamiento asincrónico

## Estructura del Proyecto

```
pdfextract/
├── src/
│   ├── config/           # Configuración centralizada
│   │   ├── __init__.py
│   │   └── settings.py   # Variables de entorno y configuración
│   ├── services/         # Lógica de negocio reutilizable
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py   # Extracción de páginas
│   │   ├── pdf_converter.py   # Conversión PDF a JPG
│   │   ├── image_to_pdf_converter.py  # Conversión imágenes a PDF
│   │   └── image_format_converter.py  # Conversión entre formatos de imagen
│   ├── ui/              # Interfaces de usuario
│   │   ├── __init__.py
│   │   └── gui_main.py  # GUI principal con Tkinter
│   ├── utils/           # Utilidades (logging, validación, etc.)
│   └── models/          # Modelos de datos
├── data/                # Datos del proyecto
│   └── pdfs/            # PDFs de entrada
├── output/              # Archivos generados
│   ├── pdfs_extraidos/  # PDFs procesados
│   ├── imagenes_jpg/    # Imágenes convertidas
│   ├── pdf_generados_desde_imagenes/  # PDFs generados desde imágenes
│   └── imagenes_convertidas/  # Imágenes convertidas de formato
├── cli_extract.py       # Script CLI para extracción
├── cli_convert.py       # Script CLI para conversión
├── cli_images_to_pdf.py # Script CLI para imágenes a PDF
├── cli_image_convert.py # Script CLI para imagen -> formato
├── cli.py               # CLI unificada (extract/pdf2jpg/img2pdf/imgconvert)
├── gui_main.py          # Punto de entrada para GUI
└── README.md
```

## Requisitos

- Python 3.8+
- PyPDF2 (extracción de PDF)
- PyMuPDF/fitz (conversión a imagen)
- Pillow (procesamiento de imágenes)
- Tkinter (interfaz gráfica - incluida con Python)

> Nota: para algunos formatos (ej. AVIF) se requiere que Pillow esté compilado con soporte del codec correspondiente.

## Instalación

```bash
pip install PyPDF2 PyMuPDF Pillow
```

## Uso

### GUI (Interfaz Gráfica)

Interfaz moderna y fácil de usar con múltiples pestañas:

```bash
python gui_main.py
```

**Características:**
- ✂️ Extractor de páginas con vista previa de información
- 🖼️ Conversor de PDF a JPG con control de zoom/calidad, rango y progreso
- 🧩 Conversor de imágenes a PDF con cola y mensajes de salida
- 🖌️ Conversor de imágenes a otros formatos compatibles
- 📊 Status bar en tiempo real
- 🎨 Tema moderno y colores coherentes

### CLI - Extracción de Páginas

Extrae páginas específicas desde la terminal:

```bash
# Extrae páginas 1-3 y 5
python cli_extract.py input.pdf output.pdf "1-3,5"

# Con información detallada
python cli_extract.py input.pdf output.pdf "1-10" --verbose

# Ver ayuda
python cli_extract.py --help
```

### CLI - Conversión a JPG

Convierte PDFs a imágenes de alta calidad:

```bash
# Convierte un PDF
python cli_convert.py archivo.pdf

# Convierte todos los PDFs en una carpeta
python cli_convert.py ./pdfs --output ./imagenes --zoom 2.0 --quality 95

# Con información detallada
python cli_convert.py ./pdfs -v

# Ver ayuda
python cli_convert.py --help
```

### CLI - Imágenes a PDF

Convierte una o varias imágenes (o carpetas de imágenes) a un PDF:

```bash
# Convertir imágenes sueltas
python cli_images_to_pdf.py foto1.jpg foto2.png --name "album"

# Convertir desde carpeta
python cli_images_to_pdf.py ./imagenes --output ./output/pdfs

# Convertir con rango (si detectó 10 imágenes, usa solo 1-3 y 6)
python cli_images_to_pdf.py ./imagenes --range "1-3,6" --name "seleccion"

# Con detalle de progreso
python cli_images_to_pdf.py ./imagenes -v
```

### CLI Unificada

Una sola entrada para todos los flujos:

```bash
# Extraer páginas
python cli.py extract input.pdf output.pdf "1-3,5"

# PDF a JPG
python cli.py pdf2jpg input.pdf --range "1-4" --zoom 2.0 --quality 95

# Imágenes a PDF
python cli.py img2pdf ./imagenes --name "album" --range "1-10"

# Imágenes a otro formato
python cli.py imgconvert ./imagenes --to webp --quality 90
```

### CLI - Imágenes a Formato

Conversión directa de imágenes entre formatos:

```bash
# Carpeta completa a PNG
python cli_image_convert.py ./imagenes --to png

# Varios archivos a WEBP
python cli_image_convert.py foto1.jpg foto2.png --to webp --quality 90

# Crear iconos ICO
python cli_image_convert.py ./logos --to ico
```

**Opciones de zoom:**
- `1.0` = 72 DPI
- `2.0` = 144 DPI (predeterminado)
- `3.0` = 216 DPI
- `4.0` = 288 DPI

## Ejemplos

### Extracción

```python
from src.services.pdf_extractor import PDFExtractor

# Extraer páginas específicas
result = PDFExtractor.extract_pages(
    'input.pdf',
    'output.pdf',
    [1, 2, 3, 5, 7, 8, 9]
)

if result['success']:
    print(f"✅ {result['message']}")
else:
    print(f"❌ {result['error']}")
```

### Conversión

```python
from src.services.pdf_converter import PDFToImageConverter

# Convertir PDF a JPG
result = PDFToImageConverter.convert_pdf_to_jpg(
    'input.pdf',
    './output',
    zoom=2.0,
    quality=95
)

if result['success']:
    print(f"✅ {result['message']}")
    print(f"Imágenes guardadas en: {result['output_directory']}")
```

## Arquitectura de Software

El proyecto sigue una **arquitectura limpia** con separación clara de responsabilidades:

### Capas

1. **Config**: Configuración centralizada
   - Variables de entorno
   - Rutas de directorios
   - Configuración de aplicación

2. **Services**: Lógica de negocio
   - `PDFExtractor`: Extracción de páginas
   - `PDFToImageConverter`: Conversión a imágenes
   - `ImageToPDFConverter`: Conversión de imágenes a PDF
   - `PageParser`: Parsing de rangos de páginas

3. **UI**: Interfaces de usuario
   - `PDFExtractToolApp`: Aplicación GUI principal
   - Pestañas para diferentes funcionalidades
   - Estilos modernos y responsive

4. **Models**: Estructuras de datos (expandible)

5. **Utils**: Funciones auxiliares (expandible)

### Ventajas

- **Reutilización**: Los servicios pueden usarse desde cualquier interfaz
- **Escalabilidad**: Fácil agregar nuevas características
- **Testing**: Lógica separada de la UI, fácil de probar
- **Mantenimiento**: Código organizado y documentado

## Configuración

Edita `src/config/settings.py` para personalizar:

```python
# Resolución de conversión
ZOOM = 2.0  # Factor de zoom

# Calidad de salida
CALIDAD = 95  # Porcentaje (1-100)

# Directorios
PDF_INPUT_DIR = "data/pdfs"
IMAGE_OUTPUT_DIR = "output/imagenes_jpg"
PDF_OUTPUT_DIR = "output/pdfs_extraidos"
```

## Estructura de Datos de Respuesta

Los servicios devuelven diccionarios estandarizados:

```python
# Extracción exitosa
{
    "success": True,
    "output_path": "/path/to/output.pdf",
    "pages_extracted": 5,
    "total_pages": 50,
    "message": "Extracción completada: 5 páginas guardadas"
}

# Extracción fallida
{
    "success": False,
    "error": "Descripción del error"
}
```

## Extensiones Futuras

- [ ] Soporte para archivos ZIP
- [ ] Compresión de imágenes automática
- [ ] Extracción de texto OCR
- [ ] Marca de agua personalizada
- [ ] API REST completa
- [ ] Electron app multiplataforma
- [ ] Tests automatizados
- [ ] Docker support

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -m 'Agrega nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.

## Soporte

Para reportar bugs o solicitar características, abre un issue en el repositorio.
