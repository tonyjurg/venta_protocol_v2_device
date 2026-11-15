"""Sphinx configuration for the Venta Protocol V2 API reference."""

from pathlib import Path
import json
import os
import sys


PROJECT_ROOT = Path(os.environ.get("VENTA_DOCS_SOURCE", Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(PROJECT_ROOT))

project = "Venta Protocol V2"
copyright = "2026, Tony Jurg"
author = "Tony Jurg"
docs_version = os.environ.get("VENTA_DOCS_VERSION", "Current (main)")

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_title = f"Venta Protocol V2 API — {docs_version}"
html_static_path = ["_static"]
html_css_files = ["api.css"]
html_context = {
    "docs_version": docs_version,
    "docs_versions": json.loads(os.environ.get("VENTA_DOCS_VERSIONS", "[]")),
}
rst_prolog = f".. |docs_version| replace:: {docs_version}\n"

autodoc_typehints = "description"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}
napoleon_google_docstring = True
napoleon_numpy_docstring = True
