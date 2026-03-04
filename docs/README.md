# LCLStreamer Documentation

This directory contains the Sphinx documentation for LCLStreamer.

## Building the Documentation

The documentation is built using [Sphinx](https://www.sphinx-doc.org/) with the [MyST parser](https://myst-parser.readthedocs.io/) for Markdown support.

### Prerequisites

All required packages are already specified in the `pyproject.toml` file:
- sphinx
- myst-parser
- pydata-sphinx-theme
- sphinx-click
- sphinxcontrib-images
- sphinxcontrib-mermaid

### Building HTML Documentation

To build the HTML documentation, run:

```bash
make html
```

Or on Windows:

```bash
make.bat html
```

The generated documentation will be in the `_build/html` directory. Open `_build/html/index.html` in your browser to view it.

### Other Build Targets

- `make clean` - Remove built documentation
- `make html` - Build HTML documentation
- `make dirhtml` - Build HTML pages as directories
- `make singlehtml` - Build a single HTML page
- `make help` - Show all available build targets

## Documentation Structure

- `conf.py` - Sphinx configuration file
- `index.rst` - Main documentation entry point (reStructuredText)
- `docs/` - Markdown documentation files
  - `index.md` - Introduction
  - `lclstreamer_data_workflow.md` - Data workflow description
  - `installation_running.md` - Installation and running instructions
  - `configuration_*.md` - Configuration documentation files
- `_static/` - Static files (CSS, images, etc.)
- `_build/` - Generated documentation (not in version control)

## Theme

The documentation uses the [PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/), which provides a clean, modern look and is commonly used in the scientific Python community.