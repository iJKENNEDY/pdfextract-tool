"""
Servicio de extracción de páginas PDF
Lógica central reutilizable para todas las interfaces
"""
from pathlib import Path
from typing import List
import PyPDF2


class PageParser:
    """Parser para convertir strings de páginas en listas de números"""
    
    @staticmethod
    def parse_pages(pages_str: str) -> List[int]:
        """
        Convierte string como '1-3,5,7-9' en [1,2,3,5,7,8,9]
        
        Args:
            pages_str: String de páginas (ej: '1-3,5,7-9')
            
        Returns:
            Lista ordenada de números de página
            
        Raises:
            ValueError: Si el formato no es válido
        """
        try:
            pages = set()
            parts = pages_str.split(',')
            
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                    
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    if start > end:
                        raise ValueError(f"Rango inválido: {start}-{end}")
                    pages.update(range(start, end + 1))
                else:
                    pages.add(int(part))
            
            if not pages:
                raise ValueError("No se especificaron páginas")
                
            return sorted(pages)
        except ValueError as e:
            raise ValueError(f"Formato de páginas inválido: {str(e)}")


class PDFExtractor:
    """Servicio para extracción de páginas de PDF"""

    @staticmethod
    def _next_available_path(output_path: Path) -> Path:
        """Evita reemplazo de archivos enumerando sufijos."""
        if not output_path.exists():
            return output_path

        stem = output_path.stem
        suffix = output_path.suffix or ".pdf"
        parent = output_path.parent
        index = 1
        while True:
            candidate = parent / f"{stem}_{index:03d}{suffix}"
            if not candidate.exists():
                return candidate
            index += 1
    
    @staticmethod
    def extract_pages(input_path: str, output_path: str, pages: List[int]) -> dict:
        """
        Extrae páginas específicas de un PDF
        
        Args:
            input_path: Ruta al PDF de entrada
            output_path: Ruta al PDF de salida
            pages: Lista de números de página a extraer (1-indexado)
            
        Returns:
            Dict con resultado y metadata
        """
        try:
            # Validar entrada
            input_path_obj = Path(input_path)
            if not input_path_obj.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {input_path_obj}")
            
            # Leer PDF
            with open(input_path_obj, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
                
                # Validar páginas
                invalid_pages = [p for p in pages if p < 1 or p > total_pages]
                if invalid_pages:
                    raise ValueError(
                        f"Páginas fuera de rango: {invalid_pages}. "
                        f"El PDF tiene {total_pages} páginas"
                    )
                
                # Extraer páginas
                writer = PyPDF2.PdfWriter()
                for page_num in pages:
                    writer.add_page(reader.pages[page_num - 1])
                
                # Crear directorio de salida si no existe
                output_path_obj = Path(output_path)
                output_path_obj.parent.mkdir(parents=True, exist_ok=True)
                output_path_obj = PDFExtractor._next_available_path(output_path_obj)
                
                # Guardar
                with open(output_path_obj, 'wb') as out_f:
                    writer.write(out_f)
                
                return {
                    "success": True,
                    "output_path": str(output_path_obj),
                    "pages_extracted": len(pages),
                    "total_pages": total_pages,
                    "message": f"Extracción completada: {len(pages)} páginas guardadas"
                }
                
        except FileNotFoundError as e:
            return {"success": False, "error": str(e)}
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Error inesperado: {str(e)}"}
    
    @staticmethod
    def extract_from_string(input_path: str, output_path: str, pages_str: str) -> dict:
        """
        Extrae páginas especificadas como string
        
        Args:
            input_path: Ruta al PDF de entrada
            output_path: Ruta al PDF de salida
            pages_str: String de páginas (ej: '1-3,5,7-9')
            
        Returns:
            Dict con resultado y metadata
        """
        try:
            pages = PageParser.parse_pages(pages_str)
            return PDFExtractor.extract_pages(input_path, output_path, pages)
        except ValueError as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_pdf_info(pdf_path: str) -> dict:
        """
        Obtiene información del PDF (número de páginas)
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Dict con información del PDF
        """
        try:
            pdf_path_obj = Path(pdf_path)
            if not pdf_path_obj.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {pdf_path_obj}")
            
            with open(pdf_path_obj, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return {
                    "success": True,
                    "total_pages": len(reader.pages),
                    "file_name": pdf_path_obj.name,
                    "file_size": pdf_path_obj.stat().st_size
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
