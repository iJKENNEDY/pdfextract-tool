#!/usr/bin/env python3
"""
Interfaz Gráfica para PDF Extract Tool
Script de entrada para GUI
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.gui_main import PDFExtractToolApp


def main():
    """Función principal"""
    app = PDFExtractToolApp()
    app.mainloop()


if __name__ == "__main__":
    main()
