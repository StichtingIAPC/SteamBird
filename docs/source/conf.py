# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import django

sys.path.insert(0, os.path.abspath('../..'))
sys.path.append(os.path.abspath("./_ext"))

# -- Activate Django ---------------------------------------------------------
os.environ['DJANGO_SETTINGS_MODULE'] = 'steambird.settings'
django.setup()

# -- Project information -----------------------------------------------------

project = 'Steambird'
copyright = '2019, Stichting IAPC & SteamBird contributors'
author = 'Stichting IAPC & SteamBird contributors'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.graphviz',
    'sphinx.ext.viewcode',
    'sphinxcontrib_django',
    'sphinx_autodoc_annotation',
    'm2r',
    'django_urls',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# Add any markup suffices that are used here.
source_suffix = ['.rst', '.md']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_show_sourcelink = True
html_copy_source = True

html_context = {
    'source_url_prefix': "https://git.iapc.utwente.nl/www/steambird/tree/master/docs/source/",
}

# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'http://docs.python.org/': None,
    'https://docs.djangoproject.com/en/stable': 'https://docs.djangoproject.com/en/stable/_objects',
}
