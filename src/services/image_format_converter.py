"""Servicio para convertir imagenes entre formatos compatibles."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image


SUPPORTED_TARGETS = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "bmp": "BMP",
    "tiff": "TIFF",
    "ico": "ICO",
    "avif": "AVIF",
}

SOURCE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".ico", ".avif"}


class ImageFormatConverter:
    """Convierte una o varias imagenes a otro formato."""

    @staticmethod
    def list_supported_targets() -> List[str]:
        return sorted(set(SUPPORTED_TARGETS.keys()))

    @staticmethod
    def list_images_from_path(path_value: str) -> List[Path]:
        path_obj = Path(path_value)
        if not path_obj.exists():
            raise FileNotFoundError(f"Ruta no encontrada: {path_obj}")

        if path_obj.is_file():
            if path_obj.suffix.lower() not in SOURCE_EXTENSIONS:
                raise ValueError(f"Formato de entrada no soportado: {path_obj.suffix}")
            return [path_obj]

        images = [
            p
            for p in sorted(path_obj.iterdir())
            if p.is_file() and p.suffix.lower() in SOURCE_EXTENSIONS
        ]
        if not images:
            raise FileNotFoundError(f"No se encontraron imagenes compatibles en: {path_obj}")
        return images

    @staticmethod
    def _safe_target(format_value: str) -> Tuple[str, str]:
        key = format_value.strip().lower().replace(".", "")
        if key not in SUPPORTED_TARGETS:
            raise ValueError(f"Formato destino no soportado: {format_value}")
        return key, SUPPORTED_TARGETS[key]

    @staticmethod
    def _next_available_file(path_obj: Path) -> Path:
        if not path_obj.exists():
            return path_obj
        index = 1
        while True:
            candidate = path_obj.parent / f"{path_obj.stem}_{index:03d}{path_obj.suffix}"
            if not candidate.exists():
                return candidate
            index += 1

    @staticmethod
    def _prepare_image_for_target(img: Image.Image, target_format: str) -> Image.Image:
        if target_format in {"JPEG", "BMP"}:
            return img.convert("RGB")
        if target_format == "ICO":
            return img.convert("RGBA")
        return img.copy()

    @staticmethod
    def convert_images(
        image_paths: List[str],
        output_dir: str,
        target_format: str,
        quality: int = 95,
        progress_callback=None,
    ) -> Dict:
        try:
            if not image_paths:
                raise ValueError("No hay imagenes para convertir")

            target_ext, target_pillow = ImageFormatConverter._safe_target(target_format)
            output_dir_obj = Path(output_dir)
            output_dir_obj.mkdir(parents=True, exist_ok=True)

            converted = 0
            errors: List[str] = []
            outputs: List[str] = []
            total = len(image_paths)

            for idx, item in enumerate(image_paths, start=1):
                src = Path(item)
                if not src.exists():
                    errors.append(f"No existe: {src}")
                    continue

                try:
                    out_name = f"{src.stem}.{target_ext}"
                    out_path = ImageFormatConverter._next_available_file(output_dir_obj / out_name)

                    with Image.open(src) as im:
                        prepared = ImageFormatConverter._prepare_image_for_target(im, target_pillow)
                        save_kwargs = {}
                        if target_pillow in {"JPEG", "WEBP", "AVIF"}:
                            save_kwargs["quality"] = max(1, min(int(quality), 100))
                        if target_pillow == "ICO":
                            save_kwargs["sizes"] = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

                        prepared.save(out_path, target_pillow, **save_kwargs)
                        prepared.close()

                    outputs.append(str(out_path))
                    converted += 1
                    if progress_callback:
                        progress_callback(idx, total, out_path.name)
                except Exception as exc:
                    errors.append(f"{src.name}: {exc}")

            return {
                "success": converted > 0,
                "converted": converted,
                "total": total,
                "target_format": target_ext,
                "output_directory": str(output_dir_obj),
                "outputs": outputs,
                "errors": errors,
                "message": f"Conversion completada: {converted}/{total} imagen(es) a {target_ext.upper()}",
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}
