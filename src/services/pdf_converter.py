"""
Servicio de conversión de PDF a imágenes JPG
"""
from pathlib import Path
from typing import Dict, List, Optional
import fitz  # PyMuPDF
from PIL import Image

from src.services.pdf_extractor import PageParser


class PDFToImageConverter:
    """Servicio para convertir PDFs a imágenes JPG"""

    FORMAT_MAP = {
        "jpg": ("JPEG", ".jpg"),
        "jpeg": ("JPEG", ".jpg"),
        "png": ("PNG", ".png"),
    }

    @staticmethod
    def _next_available_dir(base_dir: Path) -> Path:
        """Evita reemplazo de carpetas de salida."""
        if not base_dir.exists():
            return base_dir

        index = 1
        while True:
            candidate = base_dir.parent / f"{base_dir.name}_{index:03d}"
            if not candidate.exists():
                return candidate
            index += 1
    
    @staticmethod
    def convert_pdf_to_jpg(
        pdf_path: str,
        output_dir: str,
        zoom: float = 2.0,
        quality: int = 95,
        output_format: str = "jpg",
        pages_range: Optional[str] = None,
        progress_callback=None,
    ) -> Dict:
        """
        Convierte un PDF a imágenes JPG
        
        Args:
            pdf_path: Ruta al archivo PDF
            output_dir: Directorio de salida
            zoom: Factor de zoom (1.0=72dpi, 2.0=144dpi, 3.0=216dpi, 4.0=288dpi)
            quality: Calidad JPG (1-100)
            
        Returns:
            Dict con resultado y metadata
        """
        try:
            pdf_path_obj = Path(pdf_path)
            output_dir_obj = Path(output_dir)
            
            # Validar entrada
            if not pdf_path_obj.exists():
                raise FileNotFoundError(f"Archivo PDF no encontrado: {pdf_path_obj}")
            
            if not (1.0 <= zoom <= 4.0):
                raise ValueError("Zoom debe estar entre 1.0 y 4.0")
            
            if not (1 <= quality <= 100):
                raise ValueError("Calidad debe estar entre 1 y 100")
            
            # Validar formato de salida
            format_key = output_format.strip().lower()
            if format_key not in PDFToImageConverter.FORMAT_MAP:
                raise ValueError("Formato no soportado. Usa: jpg o png")
            pillow_format, extension = PDFToImageConverter.FORMAT_MAP[format_key]

            # Crear directorio de salida
            output_dir_obj.mkdir(parents=True, exist_ok=True)
            
            # Abrir PDF
            doc = fitz.open(pdf_path_obj)
            total_pages = len(doc)
            
            if total_pages == 0:
                raise ValueError("El PDF no contiene páginas")

            if pages_range and pages_range.strip():
                pages_to_convert = PageParser.parse_pages(pages_range)
                invalid_pages = [p for p in pages_to_convert if p < 1 or p > total_pages]
                if invalid_pages:
                    raise ValueError(
                        f"Páginas fuera de rango: {invalid_pages}. El PDF tiene {total_pages} páginas"
                    )
            else:
                pages_to_convert = list(range(1, total_pages + 1))
            
            # Configurar matriz de transformación
            mat = fitz.Matrix(zoom, zoom)
            saved_pages = 0
            errors = []
            
            # Crear subcarpeta única para no sobrescribir
            work_output_dir = PDFToImageConverter._next_available_dir(output_dir_obj / pdf_path_obj.stem)
            work_output_dir.mkdir(parents=True, exist_ok=True)

            # Procesar cada página (1-indexado)
            total_selected = len(pages_to_convert)
            for idx, page_num in enumerate(pages_to_convert, start=1):
                try:
                    page = doc[page_num - 1]
                    # Renderizar a imagen
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    
                    # Convertir a PIL Image
                    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                    
                    # Generar nombre de archivo
                    output_name = f"pg_{page_num:03d}{extension}"
                    output_path = work_output_dir / output_name
                    
                    # Guardar imagen
                    save_kwargs = {"optimize": True}
                    if pillow_format == "JPEG":
                        save_kwargs["quality"] = quality
                    img.save(output_path, pillow_format, **save_kwargs)
                    saved_pages += 1
                    if progress_callback:
                        progress_callback(idx, total_selected, output_name)
                    
                except Exception as e:
                    errors.append(f"Página {page_num}: {str(e)}")
            
            doc.close()
            
            return {
                "success": True,
                "total_pages": total_pages,
                "selected_pages": total_selected,
                "saved_pages": saved_pages,
                "output_format": format_key,
                "output_directory": str(work_output_dir),
                "file_name": pdf_path_obj.name,
                "errors": errors if errors else None,
                "message": f"Conversión completada: {saved_pages}/{total_selected} páginas guardadas"
            }
            
        except FileNotFoundError as e:
            return {"success": False, "error": str(e)}
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Error inesperado: {str(e)}"}
    
    @staticmethod
    def convert_batch_pdfs(
        input_dir: str,
        output_dir: str,
        zoom: float = 2.0,
        quality: int = 95,
        output_format: str = "jpg",
    ) -> Dict:
        """
        Convierte todos los PDFs de una carpeta
        
        Args:
            input_dir: Directorio con PDFs
            output_dir: Directorio de salida
            zoom: Factor de zoom
            quality: Calidad JPG
            
        Returns:
            Dict con resultado agregado
        """
        try:
            input_dir_obj = Path(input_dir)
            output_dir_obj = Path(output_dir)
            
            # Validar entrada
            if not input_dir_obj.exists():
                raise FileNotFoundError(f"Directorio no encontrado: {input_dir_obj}")
            
            # Encontrar PDFs
            pdfs = list(input_dir_obj.glob("*.pdf"))
            
            if not pdfs:
                raise FileNotFoundError(f"No se encontraron PDFs en: {input_dir_obj}")
            
            # Procesar cada PDF
            results = []
            total_pages = 0
            total_saved = 0
            
            for pdf_path in pdfs:
                # Crear subcarpeta para cada PDF
                pdf_output_dir = PDFToImageConverter._next_available_dir(output_dir_obj / pdf_path.stem)
                result = PDFToImageConverter.convert_pdf_to_jpg(
                    str(pdf_path),
                    str(pdf_output_dir),
                    zoom,
                    quality,
                    output_format,
                )
                results.append(result)
                
                if result["success"]:
                    total_pages += result["total_pages"]
                    total_saved += result["saved_pages"]
            
            return {
                "success": True,
                "total_pdfs": len(pdfs),
                "successful_pdfs": sum(1 for r in results if r["success"]),
                "total_pages": total_pages,
                "total_saved": total_saved,
                "output_directory": str(output_dir_obj),
                "details": results,
                "message": f"Procesamiento lote completado: {len(pdfs)} archivos"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
