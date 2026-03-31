"""Servicio de mejora tipo scanner para imagenes."""

from pathlib import Path
from typing import Dict, List

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


class ImageScannerService:
    """Mejora imagenes para estilo documento/certificado y exporta a PDF/JPG."""

    SUPPORTED_INPUTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

    @staticmethod
    def list_images_from_path(path_value: str) -> List[Path]:
        path_obj = Path(path_value)
        if not path_obj.exists():
            raise FileNotFoundError(f"Ruta no encontrada: {path_obj}")

        if path_obj.is_file():
            if path_obj.suffix.lower() not in ImageScannerService.SUPPORTED_INPUTS:
                raise ValueError(f"Formato no soportado: {path_obj.suffix}")
            return [path_obj]

        images = [
            p
            for p in sorted(path_obj.iterdir())
            if p.is_file() and p.suffix.lower() in ImageScannerService.SUPPORTED_INPUTS
        ]
        if not images:
            raise FileNotFoundError(f"No se encontraron imagenes en: {path_obj}")
        return images

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
    def _enhance_for_scan(img: Image.Image, contrast: float, sharpness: float) -> Image.Image:
        gray = img.convert("L")
        auto = ImageOps.autocontrast(gray)
        denoise = auto.filter(ImageFilter.MedianFilter(size=3))
        contrast_img = ImageEnhance.Contrast(denoise).enhance(contrast)
        sharp_img = ImageEnhance.Sharpness(contrast_img).enhance(sharpness)
        return sharp_img

    @staticmethod
    def scan_images(
        image_paths: List[str],
        output_dir: str,
        output_format: str = "pdf",
        output_name: str = "scan",
        quality: int = 95,
        contrast: float = 1.6,
        sharpness: float = 1.8,
        progress_callback=None,
    ) -> Dict:
        try:
            if not image_paths:
                raise ValueError("No hay imagenes para procesar")

            fmt = output_format.strip().lower()
            if fmt not in {"pdf", "jpg"}:
                raise ValueError("Formato de salida no soportado. Usa pdf o jpg")

            output_dir_obj = Path(output_dir)
            output_dir_obj.mkdir(parents=True, exist_ok=True)

            sources = [Path(p) for p in image_paths]
            total = len(sources)
            results = []

            processed_images: List[Image.Image] = []

            for idx, src in enumerate(sources, start=1):
                if not src.exists():
                    continue

                with Image.open(src) as raw:
                    scanned = ImageScannerService._enhance_for_scan(raw, contrast=contrast, sharpness=sharpness)

                    if fmt == "jpg":
                        out_file = ImageScannerService._next_available_file(output_dir_obj / f"scan_{src.stem}.jpg")
                        scanned.convert("RGB").save(out_file, "JPEG", quality=max(1, min(int(quality), 100)), optimize=True)
                        results.append(str(out_file))
                    else:
                        processed_images.append(scanned.convert("RGB"))

                if progress_callback:
                    progress_callback(idx, total, src.name)

            if fmt == "pdf":
                if not processed_images:
                    raise ValueError("No se pudo generar PDF, no hay imagenes procesadas")
                pdf_path = ImageScannerService._next_available_file(output_dir_obj / f"{output_name}.pdf")
                first = processed_images[0]
                rest = processed_images[1:]
                first.save(pdf_path, save_all=True, append_images=rest)
                for item in processed_images:
                    item.close()
                results = [str(pdf_path)]

            return {
                "success": True,
                "output_format": fmt,
                "output_directory": str(output_dir_obj),
                "outputs": results,
                "processed": len(results) if fmt == "jpg" else len(image_paths),
                "message": f"Escaneo completado en formato {fmt.upper()}",
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}
