"""Interfaz grafica principal del proyecto."""

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.settings import (
    DEFAULT_OUTPUT_BASE_DIR,
    GUI_CONFIG,
)
from src.services.image_format_converter import SOURCE_EXTENSIONS, ImageFormatConverter
from src.services.image_scanner import ImageScannerService
from src.services.image_to_pdf_converter import IMAGE_EXTENSIONS, ImageToPDFConverter
from src.services.pdf_converter import PDFToImageConverter
from src.services.pdf_extractor import PDFExtractor
from src.services.pdf_merger import PDFMergerService


class ModernStyle:
    """Gestion de estilos base para la GUI."""

    @staticmethod
    def configure_styles() -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Main.TFrame", background=GUI_CONFIG["theme_bg"])
        style.configure("Header.TFrame", background=GUI_CONFIG["theme_primary"])
        style.configure("Card.TFrame", background="white")
        style.configure(
            "Title.TLabel",
            font=GUI_CONFIG["font_title"],
            background=GUI_CONFIG["theme_primary"],
            foreground="white",
        )
        style.configure(
            "Header.TLabel",
            font=("Segoe UI", 10, "bold"),
            background=GUI_CONFIG["theme_primary"],
            foreground="white",
        )
        style.configure("Normal.TLabel", font=GUI_CONFIG["font_main"], background=GUI_CONFIG["theme_bg"])

        # Secciones por color (combinaciones suaves)
        section_styles = {
            "Extract": ("#E8F1FF", "#2E4F7A"),
            "PdfImg": ("#EAFBF3", "#2C6B4F"),
            "ImgPdf": ("#FFF4E8", "#8A4F20"),
            "ImgFmt": ("#F3ECFF", "#5A3E8E"),
            "Scan": ("#FFF8E7", "#7A5B1D"),
        }
        for prefix, (bg, fg) in section_styles.items():
            style.configure(f"{prefix}.TLabelframe", background=bg, borderwidth=1)
            style.configure(f"{prefix}.TLabelframe.Label", background=bg, foreground=fg, font=("Segoe UI", 10, "bold"))
            style.configure(f"{prefix}.TFrame", background=bg)
            style.configure(f"{prefix}.TLabel", background=bg, foreground=fg)


class BaseTab(ttk.Frame):
    """Base comun para tabs con status y safe-ui-update."""

    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.status_var = tk.StringVar(value="Listo")
        self.output_dir_var = tk.StringVar(value=str(DEFAULT_OUTPUT_BASE_DIR))

    def build_status_bar(self) -> None:
        status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken")
        status_bar.pack(side="bottom", fill="x", padx=10, pady=5)

    def on_ui(self, callback):
        self.after(0, callback)

    @staticmethod
    def bytes_to_mb(size_bytes: int) -> float:
        return float(size_bytes) / (1024.0 * 1024.0)

    def open_output_dir(self, path_value: str):
        try:
            path_obj = Path(path_value)
            if path_obj.is_file():
                path_obj = path_obj.parent
            path_obj.mkdir(parents=True, exist_ok=True)
            if sys.platform.startswith("win"):
                import os

                os.startfile(str(path_obj))
            elif sys.platform == "darwin":
                import subprocess

                subprocess.Popen(["open", str(path_obj)])
            else:
                import subprocess

                subprocess.Popen(["xdg-open", str(path_obj)])
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo abrir el directorio:\n{exc}")

    def get_output_subdir(self, subfolder: str) -> Path:
        base = Path(self.output_dir_var.get()) if self.output_dir_var.get() else DEFAULT_OUTPUT_BASE_DIR
        target = base / subfolder
        target.mkdir(parents=True, exist_ok=True)
        return target

    def choose_output_base_dir(self):
        selected = filedialog.askdirectory(
            title="Selecciona directorio base de salida",
            initialdir=self.output_dir_var.get() or str(DEFAULT_OUTPUT_BASE_DIR),
        )
        if selected:
            self.output_dir_var.set(selected)
            self.status_var.set(f"Output base: {selected}")


class PDFExtractorTab(BaseTab):
    """Tab de extraccion de paginas."""

    def __init__(self, parent):
        super().__init__(parent)
        self.selected_file = None
        self.setup_ui()

    def setup_ui(self):
        main = ttk.Frame(self, style="Extract.TFrame")
        main.pack(fill="both", expand=True, padx=16, pady=16)

        file_box = ttk.LabelFrame(main, text="📄 PDF de entrada", padding=12, style="Extract.TLabelframe")
        file_box.pack(fill="x", pady=8)
        self.file_label = ttk.Label(file_box, text="No seleccionado", foreground="gray", style="Extract.TLabel")
        self.file_label.pack(anchor="w", pady=4)
        self.info_label = ttk.Label(file_box, text="", foreground="#555", style="Extract.TLabel")
        self.info_label.pack(anchor="w", pady=2)
        ttk.Button(file_box, text="📁 Seleccionar PDF", command=self.select_file).pack(anchor="w", pady=6)

        pages_box = ttk.LabelFrame(main, text="🔢 Rango de paginas", padding=12, style="Extract.TLabelframe")
        pages_box.pack(fill="x", pady=8)
        ttk.Label(pages_box, text="Ejemplo: 1-3,5,7-9", style="Extract.TLabel").pack(anchor="w")
        self.pages_var = tk.StringVar()
        ttk.Entry(pages_box, textvariable=self.pages_var).pack(fill="x", pady=6)

        action_box = ttk.Frame(main)
        action_box.pack(fill="x", pady=8)
        ttk.Button(action_box, text="✂️ Extraer", command=self.extract_pages).pack(side="left", padx=4)
        ttk.Button(action_box, text="💾 Guardar como", command=self.save_as).pack(side="left", padx=4)
        ttk.Button(action_box, text="📂 Abrir output", command=lambda: self.open_output_dir(str(self.get_output_subdir("pdfs_extraidos")))).pack(side="left", padx=4)
        ttk.Button(action_box, text="🗂️ Cambiar output", command=self.choose_output_base_dir).pack(side="left", padx=4)

        self.build_status_bar()

    def select_file(self):
        path = filedialog.askopenfilename(title="Selecciona un PDF", filetypes=[("PDF", "*.pdf")])
        if not path:
            return
        self.selected_file = path
        info = PDFExtractor.get_pdf_info(path)
        self.file_label.config(text=Path(path).name, foreground="black")
        if info.get("success"):
            size_mb = self.bytes_to_mb(info["file_size"])
            self.info_label.config(text=f"Paginas: {info['total_pages']} | Tamano: {size_mb:.2f} MB")
            self.status_var.set("PDF cargado")

    def _run_extract(self, output_file: str):
        pages = self.pages_var.get().strip()
        if not self.selected_file:
            self.on_ui(lambda: messagebox.showwarning("Aviso", "Selecciona un PDF primero"))
            return
        if not pages:
            self.on_ui(lambda: messagebox.showwarning("Aviso", "Ingresa un rango de paginas"))
            return

        result = PDFExtractor.extract_from_string(self.selected_file, output_file, pages)
        if result.get("success"):
            def _ok():
                self.status_var.set(result["message"])
                messagebox.showinfo("Completado", f"{result['message']}\n\nArchivo:\n{result['output_path']}")
            self.on_ui(_ok)
        else:
            self.on_ui(lambda: messagebox.showerror("Error", result.get("error", "Error desconocido")))

    def extract_pages(self):
        if not self.selected_file:
            messagebox.showwarning("Aviso", "Selecciona un PDF primero")
            return
        out = self.get_output_subdir("pdfs_extraidos") / "extract.pdf"
        self.status_var.set("Extrayendo...")
        threading.Thread(target=self._run_extract, args=(str(out),), daemon=True).start()

    def save_as(self):
        if not self.selected_file:
            messagebox.showwarning("Aviso", "Selecciona un PDF primero")
            return
        out = filedialog.asksaveasfilename(
            initialdir=str(self.get_output_subdir("pdfs_extraidos")),
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if not out:
            return
        self.status_var.set("Extrayendo...")
        threading.Thread(target=self._run_extract, args=(out,), daemon=True).start()


class PDFMergeTab(BaseTab):
    """Tab para unir multiples PDFs."""

    def __init__(self, parent):
        super().__init__(parent)
        self.pdf_paths = []
        self.setup_ui()

    def setup_ui(self):
        main = ttk.Frame(self, style="Extract.TFrame")
        main.pack(fill="both", expand=True, padx=16, pady=16)

        in_box = ttk.LabelFrame(main, text="📚 PDFs a unir", padding=12, style="Extract.TLabelframe")
        in_box.pack(fill="both", expand=True, pady=8)

        ctrl = ttk.Frame(in_box)
        ctrl.pack(fill="x", pady=4)
        ttk.Button(ctrl, text="➕ Agregar PDFs", command=self.add_pdfs).pack(side="left", padx=4)
        ttk.Button(ctrl, text="⬆️ Subir", command=self.move_up).pack(side="left", padx=4)
        ttk.Button(ctrl, text="⬇️ Bajar", command=self.move_down).pack(side="left", padx=4)
        ttk.Button(ctrl, text="❌ Quitar", command=self.remove_selected).pack(side="left", padx=4)
        ttk.Button(ctrl, text="🧹 Limpiar", command=self.clear_list).pack(side="left", padx=4)

        ttk.Label(
            in_box,
            text="Se uniran respetando el orden de la lista (arriba a abajo)",
            style="Extract.TLabel",
        ).pack(anchor="w", padx=4, pady=(2, 6))

        self.listbox = tk.Listbox(in_box, height=10)
        self.listbox.pack(fill="both", expand=True, padx=4, pady=4)

        out_box = ttk.LabelFrame(main, text="💾 Salida", padding=12, style="Extract.TLabelframe")
        out_box.pack(fill="x", pady=8)
        self.output_var = tk.StringVar(value=str(self.get_output_subdir("pdf_unidos") / "merge.pdf"))
        ttk.Entry(out_box, textvariable=self.output_var).pack(fill="x", pady=4)
        ttk.Button(out_box, text="📁 Elegir ruta", command=self.pick_output).pack(anchor="w", pady=4)

        action = ttk.Frame(main)
        action.pack(fill="x", pady=8)
        ttk.Button(action, text="🔗 Unir PDFs", command=self.merge).pack(side="left", padx=4)
        ttk.Button(action, text="📂 Abrir output", command=lambda: self.open_output_dir(str(self.get_output_subdir("pdf_unidos")))).pack(side="left", padx=4)
        ttk.Button(action, text="🗂️ Cambiar output", command=self.choose_output_base_dir).pack(side="left", padx=4)

        self.build_status_bar()

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for idx, item in enumerate(self.pdf_paths, start=1):
            self.listbox.insert(tk.END, f"{idx:03d}. {Path(item).name}")
        self.status_var.set(f"PDFs cargados: {len(self.pdf_paths)}")

    def add_pdfs(self):
        paths = filedialog.askopenfilenames(title="Selecciona PDFs", filetypes=[("PDF", "*.pdf")])
        for p in paths:
            if p not in self.pdf_paths:
                self.pdf_paths.append(p)
        self._refresh_list()

    def clear_list(self):
        self.pdf_paths = []
        self._refresh_list()

    def remove_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        index = sel[0]
        self.pdf_paths.pop(index)
        self._refresh_list()
        if index > 0:
            self.listbox.selection_set(index - 1)
        elif self.pdf_paths:
            self.listbox.selection_set(0)

    def move_up(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        index = sel[0]
        if index == 0:
            return
        self.pdf_paths[index - 1], self.pdf_paths[index] = self.pdf_paths[index], self.pdf_paths[index - 1]
        self._refresh_list()
        self.listbox.selection_set(index - 1)

    def move_down(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        index = sel[0]
        if index >= len(self.pdf_paths) - 1:
            return
        self.pdf_paths[index + 1], self.pdf_paths[index] = self.pdf_paths[index], self.pdf_paths[index + 1]
        self._refresh_list()
        self.listbox.selection_set(index + 1)

    def pick_output(self):
        out = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialdir=str(self.get_output_subdir("pdf_unidos")),
            filetypes=[("PDF", "*.pdf")],
        )
        if out:
            self.output_var.set(out)

    def _worker(self):
        result = PDFMergerService.merge_pdfs(self.pdf_paths, self.output_var.get())
        if result.get("success"):
            def _ok():
                self.status_var.set(result["message"])
                messagebox.showinfo(
                    "Completado",
                    f"{result['message']}\n\nPDFs unidos: {result['files_merged']}\nPaginas totales: {result['total_pages']}\nArchivo: {result['output_path']}",
                )
            self.on_ui(_ok)
        else:
            self.on_ui(lambda: messagebox.showerror("Error", result.get("error", "Error desconocido")))

    def merge(self):
        if len(self.pdf_paths) < 2:
            messagebox.showwarning("Aviso", "Debes seleccionar al menos 2 PDFs")
            return
        self.status_var.set("Uniendo PDFs...")
        threading.Thread(target=self._worker, daemon=True).start()


class PDFToImageTab(BaseTab):
    """Tab de PDF a JPG con rango y progreso."""

    def __init__(self, parent):
        super().__init__(parent)
        self.selected_pdf = None
        self.setup_ui()

    def setup_ui(self):
        main = ttk.Frame(self, style="PdfImg.TFrame")
        main.pack(fill="both", expand=True, padx=16, pady=16)

        top = ttk.LabelFrame(main, text="📄 Entrada", padding=12, style="PdfImg.TLabelframe")
        top.pack(fill="x", pady=8)
        self.file_label = ttk.Label(top, text="No seleccionado", foreground="gray", style="PdfImg.TLabel")
        self.file_label.pack(anchor="w", pady=4)
        self.info_label = ttk.Label(top, text="", foreground="#555", style="PdfImg.TLabel")
        self.info_label.pack(anchor="w", pady=2)
        ttk.Button(top, text="📁 Seleccionar PDF", command=self.select_pdf).pack(anchor="w", pady=6)

        cfg = ttk.LabelFrame(main, text="⚙️ Opciones", padding=12, style="PdfImg.TLabelframe")
        cfg.pack(fill="x", pady=8)

        ttk.Label(cfg, text="Rango de paginas (vacio = todo):").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.pages_var = tk.StringVar()
        ttk.Entry(cfg, textvariable=self.pages_var).grid(row=0, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(cfg, text="Zoom:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.zoom_var = tk.DoubleVar(value=2.0)
        zoom = ttk.Scale(cfg, from_=1.0, to=4.0, variable=self.zoom_var, command=self._refresh_zoom)
        zoom.grid(row=1, column=1, sticky="ew", padx=4, pady=4)
        self.zoom_label = ttk.Label(cfg, text="2.0x (144 DPI)")
        self.zoom_label.grid(row=1, column=2, sticky="w", padx=4)

        ttk.Label(cfg, text="Formato salida:").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        self.output_format_var = tk.StringVar(value="jpg")
        ttk.Combobox(
            cfg,
            textvariable=self.output_format_var,
            state="readonly",
            values=["jpg", "png"],
            width=12,
        ).grid(row=2, column=1, sticky="w", padx=4, pady=4)

        ttk.Label(cfg, text="Calidad JPG:").grid(row=3, column=0, sticky="w", padx=4, pady=4)
        self.quality_var = tk.IntVar(value=95)
        quality = ttk.Scale(cfg, from_=50, to=100, variable=self.quality_var, command=self._refresh_quality)
        quality.grid(row=3, column=1, sticky="ew", padx=4, pady=4)
        self.quality_label = ttk.Label(cfg, text="95%")
        self.quality_label.grid(row=3, column=2, sticky="w", padx=4)

        cfg.columnconfigure(1, weight=1)

        action = ttk.Frame(main)
        action.pack(fill="x", pady=8)
        ttk.Button(action, text="🖼️ Convertir a JPG", command=self.convert).pack(side="left", padx=4)
        ttk.Button(action, text="📂 Abrir output", command=lambda: self.open_output_dir(str(self.get_output_subdir("imagenes")))).pack(side="left", padx=4)
        ttk.Button(action, text="🗂️ Cambiar output", command=self.choose_output_base_dir).pack(side="left", padx=4)

        progress_box = ttk.LabelFrame(main, text="📊 Progreso", padding=12, style="PdfImg.TLabelframe")
        progress_box.pack(fill="x", pady=8)
        self.progress = ttk.Progressbar(progress_box, mode="determinate")
        self.progress.pack(fill="x", padx=4, pady=4)
        self.progress_label = ttk.Label(progress_box, text="Sin proceso")
        self.progress_label.pack(anchor="w", padx=4)

        self.build_status_bar()

    def _refresh_zoom(self, _value=None):
        zoom = float(self.zoom_var.get())
        self.zoom_label.config(text=f"{zoom:.1f}x ({int(72 * zoom)} DPI)")

    def _refresh_quality(self, _value=None):
        self.quality_label.config(text=f"{int(float(self.quality_var.get()))}%")

    def select_pdf(self):
        path = filedialog.askopenfilename(title="Selecciona un PDF", filetypes=[("PDF", "*.pdf")])
        if not path:
            return
        self.selected_pdf = path
        self.file_label.config(text=Path(path).name, foreground="black")
        info = PDFExtractor.get_pdf_info(path)
        if info.get("success"):
            size_mb = self.bytes_to_mb(info["file_size"])
            self.info_label.config(text=f"Paginas: {info['total_pages']} | Tamano: {size_mb:.2f} MB")
        self.status_var.set("PDF listo para convertir")

    def _on_progress(self, current: int, total: int, filename: str):
        def _ui():
            self.progress.configure(maximum=max(total, 1), value=current)
            self.progress_label.config(text=f"{current}/{total} - {filename}")
            self.status_var.set(f"Convirtiendo... {current}/{total}")
        self.on_ui(_ui)

    def _worker(self):
        pdf_file = self.selected_pdf
        if not pdf_file:
            self.on_ui(lambda: messagebox.showwarning("Aviso", "Selecciona un PDF primero"))
            return

        result = PDFToImageConverter.convert_pdf_to_jpg(
            pdf_file,
            str(self.get_output_subdir("imagenes")),
            zoom=float(self.zoom_var.get()),
            quality=int(float(self.quality_var.get())),
            output_format=self.output_format_var.get(),
            pages_range=self.pages_var.get().strip() or None,
            progress_callback=self._on_progress,
        )

        if result.get("success"):
            def _ok():
                self.status_var.set(result["message"])
                self.progress_label.config(text="Proceso finalizado")
                messagebox.showinfo(
                    "Completado",
                    f"{result['message']}\n\nPDF: {result['file_name']}\nHojas procesadas: {result['saved_pages']}\nSalida: {result['output_directory']}",
                )
            self.on_ui(_ok)
        else:
            self.on_ui(lambda: messagebox.showerror("Error", result.get("error", "Error desconocido")))

    def convert(self):
        if not self.selected_pdf:
            messagebox.showwarning("Aviso", "Selecciona un PDF primero")
            return
        self.progress.configure(value=0)
        self.progress_label.config(text="Iniciando...")
        self.status_var.set("Convirtiendo PDF a JPG...")
        threading.Thread(target=self._worker, daemon=True).start()


class ImageToPDFTab(BaseTab):
    """Tab de imagenes a PDF (modo todo/individual y drag&drop)."""

    def __init__(self, parent):
        super().__init__(parent)
        self.image_paths = []
        self.setup_ui()

    def setup_ui(self):
        main = ttk.Frame(self, style="ImgPdf.TFrame")
        main.pack(fill="both", expand=True, padx=16, pady=16)

        # Entrada
        in_box = ttk.LabelFrame(main, text="🖼️ Entrada de imagenes", padding=12, style="ImgPdf.TLabelframe")
        in_box.pack(fill="both", expand=True, pady=8)

        ctrl = ttk.Frame(in_box)
        ctrl.pack(fill="x", pady=4)
        ttk.Button(ctrl, text="➕ Agregar imagenes", command=self.add_images).pack(side="left", padx=4)
        ttk.Button(ctrl, text="📂 Agregar carpeta", command=self.add_folder).pack(side="left", padx=4)
        ttk.Button(ctrl, text="🧹 Limpiar", command=self.clear_images).pack(side="left", padx=4)

        self.drop_hint = ttk.Label(
            in_box,
            text="Arrastra y suelta archivos o directorios aqui",
            foreground="#555",
            style="ImgPdf.TLabel",
        )
        self.drop_hint.pack(anchor="w", padx=4, pady=4)

        self.listbox = tk.Listbox(in_box, height=8)
        self.listbox.pack(fill="both", expand=True, padx=4, pady=4)

        # Opciones
        opt = ttk.LabelFrame(main, text="⚙️ Opciones", padding=12, style="ImgPdf.TLabelframe")
        opt.pack(fill="x", pady=8)
        ttk.Label(opt, text="Rango de hojas (vacio = todas):").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.range_var = tk.StringVar(value="1")
        ttk.Entry(opt, textvariable=self.range_var).grid(row=0, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(opt, text="Nombre base PDF:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.output_name_var = tk.StringVar(value="img2pdf")
        ttk.Entry(opt, textvariable=self.output_name_var).grid(row=1, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(opt, text="Modo de conversion:").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        self.mode_var = tk.StringVar(value="todo")
        ttk.Combobox(
            opt,
            textvariable=self.mode_var,
            state="readonly",
            values=["todo", "individual"],
        ).grid(row=2, column=1, sticky="ew", padx=4, pady=4)

        opt.columnconfigure(1, weight=1)

        action = ttk.Frame(main)
        action.pack(fill="x", pady=8)
        ttk.Button(action, text="🚀 Convertir", command=self.process_conversion).pack(side="left", padx=4)
        ttk.Button(action, text="📂 Abrir output", command=lambda: self.open_output_dir(str(self.get_output_subdir("img2pdf")))).pack(side="left", padx=4)
        ttk.Button(action, text="🗂️ Cambiar output", command=self.choose_output_base_dir).pack(side="left", padx=4)

        progress_box = ttk.LabelFrame(main, text="📊 Progreso", padding=12, style="ImgPdf.TLabelframe")
        progress_box.pack(fill="x", pady=8)
        self.progress = ttk.Progressbar(progress_box, mode="determinate")
        self.progress.pack(fill="x", padx=4, pady=4)
        self.progress_label = ttk.Label(progress_box, text="Sin proceso")
        self.progress_label.pack(anchor="w", padx=4)

        self.build_status_bar()

        self._enable_dnd()

    def _enable_dnd(self):
        try:
            drop_register = getattr(self, "drop_target_register", None)
            drop_bind = getattr(self, "dnd_bind", None)
            if callable(drop_register) and callable(drop_bind):
                drop_register("DND_Files")
                drop_bind("<<Drop>>", self._on_drop)
            else:
                self.drop_hint.config(text="Drag&Drop no disponible en este entorno")
        except Exception:
            self.drop_hint.config(text="Drag&Drop no disponible en este entorno")

    def _on_drop(self, event):
        raw = event.data.strip()
        parts = self.tk.splitlist(raw)
        for item in parts:
            p = Path(item)
            if p.is_dir():
                self._add_from_folder(p)
            elif p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS:
                self._add_single_image(p)
        self._refresh_list()

    def _add_single_image(self, image_path: Path):
        value = str(image_path)
        if value not in self.image_paths:
            self.image_paths.append(value)

    def _add_from_folder(self, folder_path: Path):
        for child in sorted(folder_path.iterdir()):
            if child.is_file() and child.suffix.lower() in IMAGE_EXTENSIONS:
                self._add_single_image(child)

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for idx, item in enumerate(self.image_paths, start=1):
            self.listbox.insert(tk.END, f"{idx:03d}. {Path(item).name}")
        self.status_var.set(f"Imagenes cargadas: {len(self.image_paths)}")

    def add_images(self):
        paths = filedialog.askopenfilenames(
            title="Selecciona imagenes",
            filetypes=[("Imagenes", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.webp")],
        )
        for p in paths:
            self._add_single_image(Path(p))
        self._refresh_list()

    def add_folder(self):
        folder = filedialog.askdirectory(title="Selecciona carpeta con imagenes")
        if not folder:
            return
        self._add_from_folder(Path(folder))
        self._refresh_list()

    def clear_images(self):
        self.image_paths = []
        self._refresh_list()

    def _on_progress(self, current: int, total: int, filename: str):
        def _ui():
            self.progress.configure(maximum=max(total, 1), value=current)
            self.progress_label.config(text=f"{current}/{total} - {filename}")
        self.on_ui(_ui)

    def _process_all_images(self):
        result = ImageToPDFConverter.convert_images_to_pdf(
            image_paths=list(self.image_paths),
            output_dir=str(self.get_output_subdir("img2pdf")),
            output_name=self.output_name_var.get().strip() or "img2pdf",
            range_str=self.range_var.get().strip() or None,
            progress_callback=self._on_progress,
        )

        def _done():
            if result.get("success"):
                self.progress_label.config(text="Proceso finalizado")
                self.status_var.set(result["message"])
                messagebox.showinfo(
                    "Completado",
                    f"{result['message']}\n\nSalida: {result['output_directory']}\nArchivo: {result['output_path']}",
                )
            else:
                self.status_var.set("Error en conversion")
                messagebox.showerror("Error", result.get("error", "Error desconocido"))

        self.on_ui(_done)

    def _process_individual_images(self):
        outputs = []
        total = len(self.image_paths)
        success_count = 0
        base_name = self.output_name_var.get().strip() or "imagen"

        for idx, image_path in enumerate(self.image_paths, start=1):
            file_stem = Path(image_path).stem
            output_name = f"{base_name}_{file_stem}"

            result = ImageToPDFConverter.convert_images_to_pdf(
                image_paths=[image_path],
                output_dir=str(self.get_output_subdir("img2pdf")),
                output_name=output_name,
                range_str="1",
            )

            if result.get("success"):
                success_count += 1
                outputs.append(result["output_path"])

            self.on_ui(lambda i=idx, t=total, n=file_stem: self._on_progress(i, t, n))

        def _done():
            self.progress_label.config(text="Proceso finalizado")
            self.status_var.set(f"Conversion individual completada: {success_count}/{total}")
            messagebox.showinfo(
                "Completado",
                f"PDFs generados: {success_count}/{total}\n\nSalida: {self.get_output_subdir('img2pdf')}\n\n" + "\n".join(outputs[:10]),
            )

        self.on_ui(_done)

    def process_conversion(self):
        if not self.image_paths:
            messagebox.showwarning("Aviso", "No hay imagenes seleccionadas")
            return

        mode = self.mode_var.get().strip().lower()
        self.progress.configure(value=0)
        self.progress_label.config(text="Iniciando...")
        self.status_var.set(f"Convirtiendo en modo: {mode}")

        if mode == "individual":
            threading.Thread(target=self._process_individual_images, daemon=True).start()
        else:
            threading.Thread(target=self._process_all_images, daemon=True).start()

class ImageFormatConvertTab(BaseTab):
    """Tab para convertir imagenes a otros formatos compatibles."""

    def __init__(self, parent):
        super().__init__(parent)
        self.image_paths = []
        self.setup_ui()

    def setup_ui(self):
        main = ttk.Frame(self, style="ImgFmt.TFrame")
        main.pack(fill="both", expand=True, padx=16, pady=16)

        in_box = ttk.LabelFrame(main, text="🖼️ Entrada", padding=12, style="ImgFmt.TLabelframe")
        in_box.pack(fill="both", expand=True, pady=8)

        ctrl = ttk.Frame(in_box)
        ctrl.pack(fill="x", pady=4)
        ttk.Button(ctrl, text="➕ Agregar imagenes", command=self.add_images).pack(side="left", padx=4)
        ttk.Button(ctrl, text="📂 Agregar carpeta", command=self.add_folder).pack(side="left", padx=4)
        ttk.Button(ctrl, text="🧹 Limpiar", command=self.clear_images).pack(side="left", padx=4)

        self.drop_hint = ttk.Label(
            in_box,
            text="Arrastra y suelta archivos o carpetas aqui",
            foreground="#555",
            style="ImgFmt.TLabel",
        )
        self.drop_hint.pack(anchor="w", padx=4, pady=4)

        self.listbox = tk.Listbox(in_box, height=9)
        self.listbox.pack(fill="both", expand=True, padx=4, pady=4)

        opt = ttk.LabelFrame(main, text="⚙️ Opciones", padding=12, style="ImgFmt.TLabelframe")
        opt.pack(fill="x", pady=8)

        ttk.Label(opt, text="Formato destino:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.target_var = tk.StringVar(value="png")
        formats = ImageFormatConverter.list_supported_targets()
        self.target_combo = ttk.Combobox(opt, textvariable=self.target_var, values=formats, state="readonly")
        self.target_combo.grid(row=0, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(opt, text="Calidad (JPG/WEBP/AVIF):").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.quality_var = tk.IntVar(value=95)
        quality = ttk.Scale(opt, from_=1, to=100, variable=self.quality_var, command=self._refresh_quality)
        quality.grid(row=1, column=1, sticky="ew", padx=4, pady=4)
        self.quality_label = ttk.Label(opt, text="95%")
        self.quality_label.grid(row=1, column=2, sticky="w", padx=4)
        opt.columnconfigure(1, weight=1)

        action = ttk.Frame(main)
        action.pack(fill="x", pady=8)
        ttk.Button(action, text="🎨 Convertir imagenes", command=self.convert).pack(side="left", padx=4)
        ttk.Button(action, text="📂 Abrir output", command=lambda: self.open_output_dir(str(self.get_output_subdir("imgfmt")))).pack(side="left", padx=4)
        ttk.Button(action, text="🗂️ Cambiar output", command=self.choose_output_base_dir).pack(side="left", padx=4)

        progress_box = ttk.LabelFrame(main, text="📊 Progreso", padding=12, style="ImgFmt.TLabelframe")
        progress_box.pack(fill="x", pady=8)
        self.progress = ttk.Progressbar(progress_box, mode="determinate")
        self.progress.pack(fill="x", padx=4, pady=4)
        self.progress_label = ttk.Label(progress_box, text="Sin proceso")
        self.progress_label.pack(anchor="w", padx=4)

        self.build_status_bar()
        self._enable_dnd()

    def _enable_dnd(self):
        try:
            drop_register = getattr(self, "drop_target_register", None)
            drop_bind = getattr(self, "dnd_bind", None)
            if callable(drop_register) and callable(drop_bind):
                drop_register("DND_Files")
                drop_bind("<<Drop>>", self._on_drop)
            else:
                self.drop_hint.config(text="Drag&Drop no disponible en este entorno")
        except Exception:
            self.drop_hint.config(text="Drag&Drop no disponible en este entorno")

    def _on_drop(self, event):
        raw = event.data.strip()
        for item in self.tk.splitlist(raw):
            p = Path(item)
            if p.is_dir():
                try:
                    found = ImageFormatConverter.list_images_from_path(str(p))
                    for path_obj in found:
                        value = str(path_obj)
                        if value not in self.image_paths:
                            self.image_paths.append(value)
                except Exception:
                    continue
            elif p.is_file() and p.suffix.lower() in SOURCE_EXTENSIONS:
                value = str(p)
                if value not in self.image_paths:
                    self.image_paths.append(value)
        self._refresh_list()

    def _refresh_quality(self, _value=None):
        self.quality_label.config(text=f"{int(float(self.quality_var.get()))}%")

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for idx, item in enumerate(self.image_paths, start=1):
            self.listbox.insert(tk.END, f"{idx:03d}. {Path(item).name}")
        self.status_var.set(f"Imagenes cargadas: {len(self.image_paths)}")

    def add_images(self):
        paths = filedialog.askopenfilenames(
            title="Selecciona imagenes",
            filetypes=[("Imagenes", "*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff *.ico *.avif")],
        )
        for p in paths:
            if p not in self.image_paths:
                self.image_paths.append(p)
        self._refresh_list()

    def add_folder(self):
        folder = filedialog.askdirectory(title="Selecciona carpeta con imagenes")
        if not folder:
            return
        try:
            found = ImageFormatConverter.list_images_from_path(folder)
            for path_obj in found:
                item = str(path_obj)
                if item not in self.image_paths:
                    self.image_paths.append(item)
            self._refresh_list()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def clear_images(self):
        self.image_paths = []
        self._refresh_list()

    def _on_progress(self, current: int, total: int, filename: str):
        def _ui():
            self.progress.configure(maximum=max(total, 1), value=current)
            self.progress_label.config(text=f"{current}/{total} - {filename}")
            self.status_var.set(f"Convirtiendo... {current}/{total}")
        self.on_ui(_ui)

    def _worker(self):
        result = ImageFormatConverter.convert_images(
            image_paths=self.image_paths,
            output_dir=str(self.get_output_subdir("imgfmt")),
            target_format=self.target_var.get(),
            quality=int(float(self.quality_var.get())),
            progress_callback=self._on_progress,
        )

        if result.get("success"):
            def _ok():
                self.status_var.set(result["message"])
                self.progress_label.config(text="Proceso finalizado")
                messagebox.showinfo(
                    "Completado",
                    f"{result['message']}\n\nSalida: {result['output_directory']}\nFormato: {result['target_format'].upper()}",
                )
            self.on_ui(_ok)
        else:
            self.on_ui(lambda: messagebox.showerror("Error", result.get("error", "Error desconocido")))

    def convert(self):
        if not self.image_paths:
            messagebox.showwarning("Aviso", "No hay imagenes para convertir")
            return
        self.progress.configure(value=0)
        self.progress_label.config(text="Iniciando...")
        self.status_var.set("Convirtiendo imagenes...")
        threading.Thread(target=self._worker, daemon=True).start()


class ScanTab(BaseTab):
    """Tab para escanear/mejorar imagenes de certificados/documentos."""

    def __init__(self, parent):
        super().__init__(parent)
        self.image_paths = []
        self.setup_ui()

    def setup_ui(self):
        main = ttk.Frame(self, style="Scan.TFrame")
        main.pack(fill="both", expand=True, padx=16, pady=16)

        in_box = ttk.LabelFrame(main, text="📄 Entrada (certificados / documentos)", padding=12, style="Scan.TLabelframe")
        in_box.pack(fill="both", expand=True, pady=8)

        ctrl = ttk.Frame(in_box)
        ctrl.pack(fill="x", pady=4)
        ttk.Button(ctrl, text="➕ Agregar imagenes", command=self.add_images).pack(side="left", padx=4)
        ttk.Button(ctrl, text="📂 Agregar carpeta", command=self.add_folder).pack(side="left", padx=4)
        ttk.Button(ctrl, text="🧹 Limpiar", command=self.clear_images).pack(side="left", padx=4)

        self.listbox = tk.Listbox(in_box, height=8)
        self.listbox.pack(fill="both", expand=True, padx=4, pady=4)

        opt = ttk.LabelFrame(main, text="⚙️ Escaneo", padding=12, style="Scan.TLabelframe")
        opt.pack(fill="x", pady=8)

        ttk.Label(opt, text="Salida:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.scan_format_var = tk.StringVar(value="pdf")
        ttk.Combobox(opt, textvariable=self.scan_format_var, state="readonly", values=["pdf", "jpg"], width=10).grid(
            row=0, column=1, sticky="w", padx=4, pady=4
        )

        ttk.Label(opt, text="Nombre base:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.scan_name_var = tk.StringVar(value="scan")
        ttk.Entry(opt, textvariable=self.scan_name_var).grid(row=1, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(opt, text="Calidad JPG:").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        self.scan_quality_var = tk.IntVar(value=95)
        ttk.Scale(opt, from_=1, to=100, variable=self.scan_quality_var).grid(row=2, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(opt, text="Contraste:").grid(row=3, column=0, sticky="w", padx=4, pady=4)
        self.scan_contrast_var = tk.DoubleVar(value=1.6)
        ttk.Scale(opt, from_=1.0, to=3.0, variable=self.scan_contrast_var).grid(row=3, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(opt, text="Nitidez:").grid(row=4, column=0, sticky="w", padx=4, pady=4)
        self.scan_sharpness_var = tk.DoubleVar(value=1.8)
        ttk.Scale(opt, from_=1.0, to=3.0, variable=self.scan_sharpness_var).grid(row=4, column=1, sticky="ew", padx=4, pady=4)

        opt.columnconfigure(1, weight=1)

        action = ttk.Frame(main)
        action.pack(fill="x", pady=8)
        ttk.Button(action, text="🧾 Escanear", command=self.scan).pack(side="left", padx=4)
        ttk.Button(action, text="📂 Abrir output", command=lambda: self.open_output_dir(str(self.get_output_subdir("scanner")))).pack(side="left", padx=4)
        ttk.Button(action, text="🗂️ Cambiar output", command=self.choose_output_base_dir).pack(side="left", padx=4)

        progress_box = ttk.LabelFrame(main, text="📊 Progreso", padding=12, style="Scan.TLabelframe")
        progress_box.pack(fill="x", pady=8)
        self.progress = ttk.Progressbar(progress_box, mode="determinate")
        self.progress.pack(fill="x", padx=4, pady=4)
        self.progress_label = ttk.Label(progress_box, text="Sin proceso")
        self.progress_label.pack(anchor="w", padx=4)

        self.build_status_bar()

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for idx, item in enumerate(self.image_paths, start=1):
            self.listbox.insert(tk.END, f"{idx:03d}. {Path(item).name}")
        self.status_var.set(f"Imagenes cargadas: {len(self.image_paths)}")

    def add_images(self):
        paths = filedialog.askopenfilenames(
            title="Selecciona imagenes",
            filetypes=[("Imagenes", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.webp")],
        )
        for p in paths:
            if p not in self.image_paths:
                self.image_paths.append(p)
        self._refresh_list()

    def add_folder(self):
        folder = filedialog.askdirectory(title="Selecciona carpeta con imagenes")
        if not folder:
            return
        try:
            found = ImageScannerService.list_images_from_path(folder)
            for path_obj in found:
                p = str(path_obj)
                if p not in self.image_paths:
                    self.image_paths.append(p)
            self._refresh_list()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def clear_images(self):
        self.image_paths = []
        self._refresh_list()

    def _on_progress(self, current: int, total: int, filename: str):
        def _ui():
            self.progress.configure(maximum=max(total, 1), value=current)
            self.progress_label.config(text=f"{current}/{total} - {filename}")
            self.status_var.set(f"Escaneando... {current}/{total}")

        self.on_ui(_ui)

    def _worker(self):
        result = ImageScannerService.scan_images(
            image_paths=self.image_paths,
            output_dir=str(self.get_output_subdir("scanner")),
            output_format=self.scan_format_var.get(),
            output_name=self.scan_name_var.get().strip() or "scan",
            quality=int(float(self.scan_quality_var.get())),
            contrast=float(self.scan_contrast_var.get()),
            sharpness=float(self.scan_sharpness_var.get()),
            progress_callback=self._on_progress,
        )

        if result.get("success"):
            def _ok():
                self.status_var.set(result["message"])
                self.progress_label.config(text="Proceso finalizado")
                out_preview = "\n".join(result.get("outputs", [])[:8])
                messagebox.showinfo(
                    "Completado",
                    f"{result['message']}\n\nSalida: {result['output_directory']}\n\n{out_preview}",
                )

            self.on_ui(_ok)
        else:
            self.on_ui(lambda: messagebox.showerror("Error", result.get("error", "Error desconocido")))

    def scan(self):
        if not self.image_paths:
            messagebox.showwarning("Aviso", "No hay imagenes para escanear")
            return
        self.progress.configure(value=0)
        self.progress_label.config(text="Iniciando...")
        threading.Thread(target=self._worker, daemon=True).start()


class PDFExtractToolApp(tk.Tk):
    """Aplicacion principal."""

    def __init__(self):
        super().__init__()
        self.title(GUI_CONFIG["title"])
        self.geometry(f"{GUI_CONFIG['window_width']}x{GUI_CONFIG['window_height']}")
        self.minsize(860, 620)
        self._setup_window_icon()
        self._show_loading_screen()
        self.after(700, self._finish_startup)

    def _show_loading_screen(self):
        """Pantalla inicial de carga."""
        loading_frame = ttk.Frame(self, padding=24)
        loading_frame.pack(fill="both", expand=True)

        ttk.Label(
            loading_frame,
            text="⏳ Cargando PDF Extract Tool...",
            font=("Segoe UI", 13, "bold"),
        ).pack(pady=(30, 12))

        progress = ttk.Progressbar(loading_frame, mode="indeterminate", length=320)
        progress.pack(pady=10)
        progress.start(12)

        ttk.Label(
            loading_frame,
            text="Inicializando modulos y recursos...",
            foreground="#666",
        ).pack(pady=(8, 0))

        self.update_idletasks()

    def _finish_startup(self):
        """Finaliza inicializacion y monta la UI principal."""
        for child in self.winfo_children():
            child.destroy()
        ModernStyle.configure_styles()
        self.setup_ui()

    def _setup_window_icon(self):
        """Carga icono .ico de la aplicacion si existe."""
        try:
            root_path = Path(__file__).resolve().parent.parent.parent
            candidates = [root_path / "logo.ico", root_path / "logo123.ico"]
            for icon_path in candidates:
                if icon_path.exists():
                    self.iconbitmap(str(icon_path))
                    break
        except Exception:
            pass

    def setup_ui(self):
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        header = ttk.Frame(self, style="Header.TFrame", height=76)
        header.grid(row=0, column=0, sticky="nsew")
        header.grid_propagate(False)
        ttk.Label(header, text="📚 PDF Extract Tool", style="Title.TLabel").pack(anchor="center", pady=(12, 2))
        ttk.Label(header, text="✂️ Extraer | 🔗 Unir PDFs | 🖼️ PDF->JPG | 🧩 Imagen->PDF | 🎨 Imagen->Imagen | 🧾 Scan", style="Header.TLabel").pack(anchor="center")

        container = ttk.Frame(self, style="Main.TFrame")
        container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        notebook = ttk.Notebook(container)
        notebook.grid(row=0, column=0, sticky="nsew")

        notebook.add(PDFExtractorTab(notebook), text="✂️ Extraer paginas")
        notebook.add(PDFMergeTab(notebook), text="🔗 Unir PDFs")
        notebook.add(PDFToImageTab(notebook), text="🖼️ PDF a JPG")
        notebook.add(ImageToPDFTab(notebook), text="🧩 Imagenes a PDF")
        notebook.add(ImageFormatConvertTab(notebook), text="🎨 Imagen a formato")
        notebook.add(ScanTab(notebook), text="🧾 Scanner")

        footer = ttk.Frame(self)
        footer.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 8))
        ttk.Label(footer, text="v1.2", foreground="gray").pack(side="left")
        ttk.Button(footer, text="🚪 Salir", command=self.destroy).pack(side="right", padx=(0, 6))
        ttk.Button(footer, text="ℹ️ Acerca de", command=self.show_about).pack(side="right")

    def show_about(self):
        messagebox.showinfo(
            "Acerca de",
            "PDF Extract Tool v1.2\n\n"
            "- Extrae paginas de PDF\n"
            "- Une multiples PDFs en un solo archivo\n"
            "- Convierte PDF a JPG con rango y progreso\n"
            "- Convierte imagenes a PDF (modo todo/individual, drag&drop, rango, no sobrescribe)\n"
            "- Convierte imagenes entre formatos (jpg/png/webp/avif/ico/etc)\n"
            "- Escanea imagenes/certificados en grises y exporta a PDF o JPG",
        )


def main():
    app = PDFExtractToolApp()
    app.mainloop()


if __name__ == "__main__":
    main()
