# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path("..", "..", "src").resolve()))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project: str = "LCLStreamer"
copyright: str = "2026, SLAC National Accelerator Laboratory"
author: str = "LCLStreamer Development Team"
release: str = "0.3.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: list[str] = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "sphinxcontrib.images",
    "sphinxcontrib.mermaid",
]

templates_path: list[str] = ["_templates"]
exclude_patterns: list[str] = []

add_module_names: bool = False

autodoc_typehints: str = "description"

autodoc_mock_imports: list[str] = [
    "psana",
]

autodoc_default_options: dict[str, Any] = {
    "members": True,
    "member-order": "bysource",
    "exclude-members": "__new__",
    "undoc-members": False,
}

autoclass_content: str = "init"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme: str = "pydata_sphinx_theme"

html_static_path: list[str] = ["_static/css"]
html_css_files: list[str] = ["custom.css"]

html_show_sourcelink = False

html_sidebars: dict[str, list[str]] = {"**": []}

html_theme_options: dict[str, Any] = {
    "show_prev_next": False,
    "logo": {
        "text": "LCLStreamer",
    },
}

html_context = {
    "github_url": "https://github.com/",
    "github_user": "slac-lcls",
    "github_repo": "om",
}

html_title = "LCLStreamer: Data Retrieval and Streaming at LCLS"
html_baseurl = "https://slac-lcls.github.io/lclstreamer/"
