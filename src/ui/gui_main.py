"""Interfaz grafica principal del proyecto."""

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.settings import GUI_CONFIG, IMAGE_OUTPUT_DIR, IMAGE_TO_PDF_OUTPUT_DIR, PDF_OUTPUT_DIR
from src.services.image_to_pdf_converter import IMAGE_EXTENSIONS, ImageToPDFConverter
from src.services.pdf_converter import PDFToImageConverter
from src.services.pdf_extractor import PDFExtractor


class ModernStyle:
    """Gestion de estilos base para la GUI."""

    @staticmethod
    def configure_styles() -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Main.TFrame", background=GUI_CONFIG["theme_bg"])
        style.configure("Header.TFrame", background=GUI_CONFIG["theme_primary"])
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


class BaseTab(ttk.Frame):
    """Base comun para tabs con status y safe-ui-update."""

    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.status_var = tk.StringVar(value="Listo")

    def build_status_bar(self) -> None:
        status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken")
        status_bar.pack(side="bottom", fill="x", padx=10, pady=5)

    def on_ui(self, callback):
        self.after(0, callback)


class PDFExtractorTab(BaseTab):
    """Tab de extraccion de paginas."""

    def __init__(self, parent):
        super().__init__(parent)
        self.selected_file = None
        self.setup_ui()

    def setup_ui(self):
        main = ttk.Frame(self, style="Main.TFrame")
        main.pack(fill="both", expand=True, padx=16, pady=16)

        file_box = ttk.LabelFrame(main, text="PDF de entrada", padding=12)
        file_box.pack(fill="x", pady=8)
        self.file_label = ttk.Label(file_box, text="No seleccionado", foreground="gray")
        self.file_label.pack(anchor="w", pady=4)
        self.info_label = ttk.Label(file_box, text="", foreground="#555")
        self.info_label.pack(anchor="w", pady=2)
        ttk.Button(file_box, text="Seleccionar PDF", command=self.select_file).pack(anchor="w", pady=6)

        pages_box = ttk.LabelFrame(main, text="Rango de paginas", padding=12)
        pages_box.pack(fill="x", pady=8)
        ttk.Label(pages_box, text="Ejemplo: 1-3,5,7-9").pack(anchor="w")
        self.pages_var = tk.StringVar()
        ttk.Entry(pages_box, textvariable=self.pages_var).pack(fill="x", pady=6)

        action_box = ttk.Frame(main)
        action_box.pack(fill="x", pady=8)
        ttk.Button(action_box, text="Extraer", command=self.extract_pages).pack(side="left", padx=4)
        ttk.Button(action_box, text="Guardar como", command=self.save_as).pack(side="left", padx=4)

        self.build_status_bar()

    def select_file(self):
        path = filedialog.askopenfilename(title="Selecciona un PDF", filetypes=[("PDF", "*.pdf")])
        if not path:
            return
        self.selected_file = path
        info = PDFExtractor.get_pdf_info(path)
        self.file_label.config(text=Path(path).name, foreground="black")
        if info.get("success"):
            self.info_label.config(text=f"Paginas: {info['total_pages']} | Tamano: {info['file_size']} bytes")
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
        out = PDF_OUTPUT_DIR / f"{Path(self.selected_file).stem}_extraido.pdf"
        self.status_var.set("Extrayendo...")
        threading.Thread(target=self._run_extract, args=(str(out),), daemon=True).start()

    def save_as(self):
        if not self.selected_file:
            messagebox.showwarning("Aviso", "Selecciona un PDF primero")
            return
        out = filedialog.asksaveasfilename(
            initialdir=str(PDF_OUTPUT_DIR),
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if not out:
            return
        self.status_var.set("Extrayendo...")
        threading.Thread(target=self._run_extract, args=(out,), daemon=True).start()


class PDFToImageTab(BaseTab):
    """Tab de PDF a JPG con rango y progreso."""

    def __init__(self, parent):
        super().__init__(parent)
        self.selected_pdf = None
        self.setup_ui()

    def setup_ui(self):
        main = ttk.Frame(self, style="Main.TFrame")
        main.pack(fill="both", expand=True, padx=16, pady=16)

        top = ttk.LabelFrame(main, text="Entrada", padding=12)
        top.pack(fill="x", pady=8)
        self.file_label = ttk.Label(top, text="No seleccionado", foreground="gray")
        self.file_label.pack(anchor="w", pady=4)
        self.info_label = ttk.Label(top, text="", foreground="#555")
        self.info_label.pack(anchor="w", pady=2)
        ttk.Button(top, text="Seleccionar PDF", command=self.select_pdf).pack(anchor="w", pady=6)

        cfg = ttk.LabelFrame(main, text="Opciones", padding=12)
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

        ttk.Label(cfg, text="Calidad JPG:").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        self.quality_var = tk.IntVar(value=95)
        quality = ttk.Scale(cfg, from_=50, to=100, variable=self.quality_var, command=self._refresh_quality)
        quality.grid(row=2, column=1, sticky="ew", padx=4, pady=4)
        self.quality_label = ttk.Label(cfg, text="95%")
        self.quality_label.grid(row=2, column=2, sticky="w", padx=4)

        cfg.columnconfigure(1, weight=1)

        action = ttk.Frame(main)
        action.pack(fill="x", pady=8)
        ttk.Button(action, text="Convertir a JPG", command=self.convert).pack(side="left", padx=4)

        progress_box = ttk.LabelFrame(main, text="Progreso", padding=12)
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
            self.info_label.config(text=f"Paginas: {info['total_pages']} | Tamano: {info['file_size']} bytes")
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
            str(IMAGE_OUTPUT_DIR),
            zoom=float(self.zoom_var.get()),
            quality=int(float(self.quality_var.get())),
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
    """Tab de imagenes a PDF, con cola y drag&drop."""

    def __init__(self, parent):
        super().__init__(parent)
        self.image_paths = []
        self.queue_items = []
        self.setup_ui()

    def setup_ui(self):
        main = ttk.Frame(self, style="Main.TFrame")
        main.pack(fill="both", expand=True, padx=16, pady=16)

        # Entrada
        in_box = ttk.LabelFrame(main, text="Entrada de imagenes", padding=12)
        in_box.pack(fill="both", expand=True, pady=8)

        ctrl = ttk.Frame(in_box)
        ctrl.pack(fill="x", pady=4)
        ttk.Button(ctrl, text="Agregar imagenes", command=self.add_images).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Agregar carpeta", command=self.add_folder).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Limpiar", command=self.clear_images).pack(side="left", padx=4)

        self.drop_hint = ttk.Label(
            in_box,
            text="Arrastra y suelta archivos o directorios aqui",
            foreground="#555",
        )
        self.drop_hint.pack(anchor="w", padx=4, pady=4)

        self.listbox = tk.Listbox(in_box, height=8)
        self.listbox.pack(fill="both", expand=True, padx=4, pady=4)

        # Opciones
        opt = ttk.LabelFrame(main, text="Opciones", padding=12)
        opt.pack(fill="x", pady=8)
        ttk.Label(opt, text="Rango de hojas (vacio = todas):").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.range_var = tk.StringVar()
        ttk.Entry(opt, textvariable=self.range_var).grid(row=0, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(opt, text="Nombre base PDF:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.output_name_var = tk.StringVar(value="imagenes_convertidas")
        ttk.Entry(opt, textvariable=self.output_name_var).grid(row=1, column=1, sticky="ew", padx=4, pady=4)

        opt.columnconfigure(1, weight=1)

        action = ttk.Frame(main)
        action.pack(fill="x", pady=8)
        ttk.Button(action, text="Agregar a cola", command=self.enqueue_current).pack(side="left", padx=4)
        ttk.Button(action, text="Procesar cola", command=self.process_queue).pack(side="left", padx=4)

        queue_box = ttk.LabelFrame(main, text="Cola de conversion", padding=12)
        queue_box.pack(fill="both", expand=True, pady=8)
        self.queue_list = tk.Listbox(queue_box, height=6)
        self.queue_list.pack(fill="both", expand=True, padx=4, pady=4)

        progress_box = ttk.LabelFrame(main, text="Progreso", padding=12)
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

    def enqueue_current(self):
        if not self.image_paths:
            messagebox.showwarning("Aviso", "No hay imagenes para agregar")
            return
        item = {
            "images": list(self.image_paths),
            "range": self.range_var.get().strip() or None,
            "name": self.output_name_var.get().strip() or "imagenes_convertidas",
        }
        self.queue_items.append(item)
        self.queue_list.insert(tk.END, f"{item['name']} | imgs:{len(item['images'])} | rango:{item['range'] or 'todo'}")
        self.status_var.set(f"Elementos en cola: {len(self.queue_items)}")

    def _on_progress(self, current: int, total: int, filename: str):
        def _ui():
            self.progress.configure(maximum=max(total, 1), value=current)
            self.progress_label.config(text=f"{current}/{total} - {filename}")
        self.on_ui(_ui)

    def _process_worker(self):
        completed = 0
        outputs = []
        total_jobs = len(self.queue_items)
        for idx, job in enumerate(list(self.queue_items), start=1):
            self.on_ui(lambda i=idx, t=total_jobs: self.status_var.set(f"Procesando cola {i}/{t}"))
            result = ImageToPDFConverter.convert_images_to_pdf(
                image_paths=job["images"],
                output_dir=str(IMAGE_TO_PDF_OUTPUT_DIR),
                output_name=job["name"],
                range_str=job["range"],
                progress_callback=self._on_progress,
            )
            if result.get("success"):
                completed += 1
                outputs.append(result["output_path"])

        def _done():
            self.queue_items = []
            self.queue_list.delete(0, tk.END)
            self.progress_label.config(text="Proceso finalizado")
            self.status_var.set(f"Cola completada: {completed}/{total_jobs}")
            messagebox.showinfo(
                "Completado",
                f"PDFs generados: {completed}/{total_jobs}\n\nSalida: {IMAGE_TO_PDF_OUTPUT_DIR}\n\n" + "\n".join(outputs[:10]),
            )

        self.on_ui(_done)

    def process_queue(self):
        if not self.queue_items:
            messagebox.showwarning("Aviso", "La cola esta vacia")
            return
        self.progress.configure(value=0)
        self.progress_label.config(text="Iniciando...")
        threading.Thread(target=self._process_worker, daemon=True).start()


class PDFExtractToolApp(tk.Tk):
    """Aplicacion principal."""

    def __init__(self):
        super().__init__()
        self.title(GUI_CONFIG["title"])
        self.geometry(f"{GUI_CONFIG['window_width']}x{GUI_CONFIG['window_height']}")
        self.minsize(860, 620)
        ModernStyle.configure_styles()
        self.setup_ui()

    def setup_ui(self):
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        header = ttk.Frame(self, style="Header.TFrame", height=76)
        header.grid(row=0, column=0, sticky="nsew")
        header.grid_propagate(False)
        ttk.Label(header, text="PDF Extract Tool", style="Title.TLabel").pack(anchor="center", pady=(12, 2))
        ttk.Label(header, text="Extractor, PDF->JPG e Imagen->PDF", style="Header.TLabel").pack(anchor="center")

        container = ttk.Frame(self, style="Main.TFrame")
        container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        notebook = ttk.Notebook(container)
        notebook.grid(row=0, column=0, sticky="nsew")

        notebook.add(PDFExtractorTab(notebook), text="Extraer paginas")
        notebook.add(PDFToImageTab(notebook), text="PDF a JPG")
        notebook.add(ImageToPDFTab(notebook), text="Imagenes a PDF")

        footer = ttk.Frame(self)
        footer.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 8))
        ttk.Label(footer, text="v1.1", foreground="gray").pack(side="left")
        ttk.Button(footer, text="Acerca de", command=self.show_about).pack(side="right")

    def show_about(self):
        messagebox.showinfo(
            "Acerca de",
            "PDF Extract Tool v1.1\n\n"
            "- Extrae paginas de PDF\n"
            "- Convierte PDF a JPG con rango y progreso\n"
            "- Convierte imagenes a PDF (cola, drag&drop, rango, no sobrescribe)",
        )


def main():
    app = PDFExtractToolApp()
    app.mainloop()


if __name__ == "__main__":
    main()
