"""Servicio para unir multiples PDFs en uno."""

from pathlib import Path
from typing import List

import PyPDF2


class PDFMergerService:
    """Une dos o mas archivos PDF en un unico resultado."""

    @staticmethod
    def _next_available_path(output_path: Path) -> Path:
        if not output_path.exists():
            return output_path
        index = 1
        while True:
            candidate = output_path.parent / f"{output_path.stem}_{index:03d}{output_path.suffix or '.pdf'}"
            if not candidate.exists():
                return candidate
            index += 1

    @staticmethod
    def merge_pdfs(input_paths: List[str], output_path: str) -> dict:
        try:
            if len(input_paths) < 2:
                raise ValueError("Debes seleccionar al menos 2 PDFs para unir")

            path_objs = [Path(p) for p in input_paths]
            missing = [str(p) for p in path_objs if not p.exists()]
            if missing:
                raise FileNotFoundError(f"Archivos no encontrados: {missing}")

            writer = PyPDF2.PdfWriter()
            total_pages = 0

            for pdf_path in path_objs:
                with open(pdf_path, "rb") as file_obj:
                    reader = PyPDF2.PdfReader(file_obj)
                    for page in reader.pages:
                        writer.add_page(page)
                    total_pages += len(reader.pages)

            out_path_obj = Path(output_path)
            out_path_obj.parent.mkdir(parents=True, exist_ok=True)
            out_path_obj = PDFMergerService._next_available_path(out_path_obj)

            with open(out_path_obj, "wb") as out_file:
                writer.write(out_file)

            return {
                "success": True,
                "output_path": str(out_path_obj),
                "files_merged": len(path_objs),
                "total_pages": total_pages,
                "message": f"Union completada: {len(path_objs)} PDFs en {out_path_obj.name}",
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}
