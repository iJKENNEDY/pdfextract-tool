# Changelog

All notable changes to this project are documented in this file.

## v1.1.0 - 2026-03-22

### Added
- Added a new image-to-PDF conversion workflow in `src/services/image_to_pdf_converter.py`.
- Added a dedicated CLI for image-to-PDF conversion: `cli_images_to_pdf.py`.
- Added a unified CLI entrypoint `cli.py` with subcommands:
  - `extract` (PDF page extraction)
  - `pdf2jpg` (PDF to JPG conversion)
  - `img2pdf` (images to PDF conversion)
- Added a new GUI tab for images-to-PDF in `src/ui/gui_main.py`.
- Added queue-based processing for multiple images-to-PDF jobs in GUI.
- Added progress feedback for long-running conversions in GUI.
- Added optional drag-and-drop support (with fallback) for files/directories in GUI.

### Changed
- Updated `src/services/pdf_converter.py`:
  - Added page-range support for PDF-to-JPG conversion.
  - Added progress callback support.
  - Updated output behavior to avoid overwriting existing folders.
- Updated `src/services/pdf_extractor.py` to avoid overwriting output PDF files by auto-enumerating names.
- Updated `src/config/settings.py`:
  - Fixed project root resolution.
  - Added `IMAGE_TO_PDF_OUTPUT_DIR`.
  - Improved compatibility with legacy root folders when present.
  - Adjusted default GUI window size.
- Updated `src/services/__init__.py` and `src/config/__init__.py` exports for new modules/constants.
- Updated `README.md` with new features and usage examples, including unified CLI.
- Updated `cli_extract.py` and `cli_convert.py` to use lazy imports for dependency-friendly `--help` behavior.

### Fixed
- Fixed output-collision issues by introducing automatic file/folder name enumeration.
- Fixed UX responsiveness by moving heavy tasks to background threads and updating status/progress in UI-safe callbacks.
- Fixed older path/config assumptions by normalizing project path handling.

## v1.2.0 - 2026-03-22

### Changed
- Bumped visible app version from `v1.1` to `v1.2` in GUI footer and About dialog (`src/ui/gui_main.py`).
- Updated `README.md` to display current version as `v1.2`.
