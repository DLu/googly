# -- Project information -----------------------------------------------------
project = 'googly'
copyright = '2024, David V. Lu!!'
author = 'David V. Lu!!'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'myst_parser',
]
source_suffix = ['.md']

# -- Options for HTML output -------------------------------------------------
autoclass_content = 'both'
html_static_path = ['_static']
