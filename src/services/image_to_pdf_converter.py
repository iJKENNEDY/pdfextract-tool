"""Servicio para convertir imagenes a PDF."""

from pathlib import Path
from typing import Callable, Dict, List, Optional

from PIL import Image


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


class ImageToPDFConverter:
    """Convierte una o varias imagenes a PDF con soporte de rango y progreso."""

    @staticmethod
    def list_images_from_path(path_value: str) -> List[Path]:
        """Obtiene imagenes desde archivo o directorio."""
        path_obj = Path(path_value)
        if not path_obj.exists():
            raise FileNotFoundError(f"Ruta no encontrada: {path_obj}")

        if path_obj.is_file():
            if path_obj.suffix.lower() not in IMAGE_EXTENSIONS:
                raise ValueError(f"Archivo no soportado: {path_obj.name}")
            return [path_obj]

        images = [p for p in sorted(path_obj.iterdir()) if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
        if not images:
            raise FileNotFoundError(f"No se encontraron imagenes en: {path_obj}")
        return images

    @staticmethod
    def parse_range(total: int, range_str: Optional[str]) -> List[int]:
        """Parsea rangos 1-indexados: '1-3,5' o todo si vacio."""
        if total <= 0:
            raise ValueError("No hay imagenes para convertir")

        if not range_str or not range_str.strip():
            return list(range(1, total + 1))

        selected = set()
        parts = range_str.split(",")
        for part in parts:
            token = part.strip()
            if not token:
                continue
            if "-" in token:
                start, end = map(int, token.split("-", 1))
                if start > end:
                    raise ValueError(f"Rango invalido: {token}")
                selected.update(range(start, end + 1))
            else:
                selected.add(int(token))

        filtered = sorted(i for i in selected if 1 <= i <= total)
        if not filtered:
            raise ValueError("El rango no selecciona imagenes validas")
        return filtered

    @staticmethod
    def _unique_output_path(output_dir: Path, base_name: str) -> Path:
        """Evita reemplazar archivos existentes enumerando sufijos."""
        candidate = output_dir / f"{base_name}.pdf"
        if not candidate.exists():
            return candidate

        index = 1
        while True:
            candidate = output_dir / f"{base_name}_{index:03d}.pdf"
            if not candidate.exists():
                return candidate
            index += 1

    @staticmethod
    def convert_images_to_pdf(
        image_paths: List[str],
        output_dir: str,
        output_name: str,
        range_str: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict:
        """Convierte imagenes a un solo PDF."""
        try:
            if not image_paths:
                raise ValueError("Debes enviar al menos una imagen")

            path_objs = [Path(p) for p in image_paths]
            for item in path_objs:
                if not item.exists():
                    raise FileNotFoundError(f"Imagen no encontrada: {item}")

            selected_indexes = ImageToPDFConverter.parse_range(len(path_objs), range_str)
            selected_images = [path_objs[i - 1] for i in selected_indexes]

            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)
            safe_base = output_name.strip() if output_name and output_name.strip() else "imagenes_convertidas"
            output_path = ImageToPDFConverter._unique_output_path(output_dir_path, safe_base)

            converted_images: List[Image.Image] = []
            total = len(selected_images)

            for idx, img_path in enumerate(selected_images, start=1):
                with Image.open(img_path) as img_raw:
                    rgb = img_raw.convert("RGB")
                    converted_images.append(rgb.copy())
                if progress_callback:
                    progress_callback(idx, total, img_path.name)

            first_image = converted_images[0]
            rest = converted_images[1:]
            first_image.save(output_path, save_all=True, append_images=rest)

            for img in converted_images:
                img.close()

            return {
                "success": True,
                "output_path": str(output_path),
                "output_directory": str(output_dir_path),
                "file_name": output_path.name,
                "selected_count": len(selected_images),
                "total_images": len(path_objs),
                "message": f"Conversion completada: {output_path.name} ({len(selected_images)} hojas)",
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}
