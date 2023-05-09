# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'OpenAstronomy GitHub Actions Workflows'
copyright = '2023, OpenAstronomy developers'
author = 'OpenAstronomy developers'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_theme_options = {
    'logo': {
        'image_light': 'https://openastronomy.org/img/logo/logoOA_svg.png',
        'image_dark': 'https://openastronomy.org/img/logo/logoOA_white_svg.png',
        'text': 'GitHub Actions Workflows',
        'alt_text': 'OpenAstronomy',
    },
    'icon_links': [
        {
            'name': 'GitHub',
            'url': 'https://github.com/OpenAstronomy/github-actions-workflows',
            'icon': 'fa-brands fa-square-github',
            'type': 'fontawesome',
        },
    ],
}

# Set the master doc to the index file
master_doc = 'index'
