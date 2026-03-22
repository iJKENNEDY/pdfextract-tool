# REFERENCIA RÁPIDA - PDF Extract Tool

## Instalación

```bash
pip install PyPDF2 PyMuPDF Pillow
```

## Ejecución Rápida

| Tarea | Comando |
|-------|---------|
| Interfaz Gráfica | `python gui_main.py` |
| Extraer páginas | `python cli_extract.py in.pdf out.pdf "1-5"` |
| Convertir a JPG | `python cli_convert.py archivo.pdf` |
| Ayuda | `python cli_extract.py --help` |

## Formato de Páginas

| Formato | Resultado |
|---------|-----------|
| `"1"` | Página 1 |
| `"1-5"` | Páginas 1, 2, 3, 4, 5 |
| `"1,3,5"` | Páginas 1, 3, 5 |
| `"1-3,5,7-9"` | Páginas 1, 2, 3, 5, 7, 8, 9 |

## Opciones de Zoom

| Zoom | DPI | Uso |
|------|-----|-----|
| 1.0 | 72 | Baja resolución |
| 2.0 | 144 | Recomendado |
| 3.0 | 216 | Alta |
| 4.0 | 288 | Muy alta |

## Estructura del Código

```
src/
├── config/settings.py         # Configuración
├── services/
│   ├── pdf_extractor.py      # Extracción
│   └── pdf_converter.py      # Conversión
└── ui/gui_main.py            # GUI
```

## Uso en Python

```python
from src.services import PDFExtractor, PDFToImageConverter

# Extraer
r = PDFExtractor.extract_from_string('in.pdf', 'out.pdf', '1-5')

# Convertir
r = PDFToImageConverter.convert_pdf_to_jpg('in.pdf', 'out/', zoom=2.0)

# Info
info = PDFExtractor.get_pdf_info('file.pdf')
```

## Respuestas

```python
# Éxito
{
    "success": True,
    "message": "Operación completada",
    "pages_extracted": 5
}

# Error
{
    "success": False,
    "error": "Descripción del error"
}
```

## Directorios

```
data/pdfs/           → Entrada
output/pdfs_extraidos/    → PDFs procesados
output/imagenes_jpg/ → Imágenes generadas
```

## GUI Features

- Dos pestañas (Extractor, Conversor)
- Status bar en tiempo real
- Dialógos intuitivos
- Procesamiento asincrónico
- Tema moderno

## Documentación

- `README.md` - Documentación completa
- `INSTRUCCIONES.md` - Guía de uso
- `RESUMEN_RESTRUCTURACION.md` - Cambios realizados

## Troubleshooting

| Error | Solución |
|-------|----------|
| ModuleNotFoundError | `pip install [módulo]` |
| Archivo no encontrado | Verifica ruta |
| Páginas inválidas | Usa formato `"1-3,5"` |
| PDF corrupto | Archivo protegido |
