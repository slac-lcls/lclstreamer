# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "LCLStreamer"
copyright = "2024, SLAC National Accelerator Laboratory"
author = "SLAC LCLS"
version = "0.3.0"
release = "0.3.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_click",
    "sphinxcontrib.images",
    "sphinxcontrib.mermaid",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "site"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]

html_theme_options = {
    "github_url": "https://github.com/slac-lcls/lclstreamer",
    "navbar_end": ["navbar-icon-links"],
    "primary_sidebar_end": [],
    "show_nav_level": 2,
    "show_toc_level": 2,
}

html_title = "LCLStreamer: Data Retrieval and Streaming at LCLS"
html_baseurl = "https://slac-lcls.github.io/lclstreamer/"

# -- MyST configuration ------------------------------------------------------

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "substitution",
    "tasklist",
]

myst_heading_anchors = 3

# Enable mermaid diagrams - mermaid code blocks will be converted to mermaid directives
myst_fence_as_directive = ["mermaid"]

# Mermaid configuration
mermaid_output_format = "raw"
mermaid_init_js = "mermaid.initialize({startOnLoad:true});"

# -- Source suffix -----------------------------------------------------------

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
