# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


import pdflatex
from sphinx.application import Sphinx
import shutil
from pdflatex import PDFLaTeX
import subprocess
import os
project = 'BlogifiAR'
copyright = '2023, BlogifyAR'
author = 'R.S.'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.mathjax',
    'sphinx.ext.todo',
    'sphinx.ext.githubpages',
    'sphinx.ext.intersphinx',
    'sphinx.ext.ifconfig',
    'sphinx.ext.doctest',
    'sphinx.ext.imgconverter',
    'sphinx.ext.extlinks',
    'sphinx.ext.graphviz',
    'sphinx.ext.inheritance_diagram',

]

latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '11pt',
    'classoptions': ',openany,oneside',
    'babel': '\\usepackage[english]{babel}',
    'inputenc': '',
    'utf8extra': '',
    'preamble': r'''\usepackage{titlesec}
                    \titleformat{\section}[hang]{\normalfont\Large\bfseries}{\thesection}{1em}{}
                    \titlespacing*{\section}{0pt}{1.5ex plus 1ex minus .2ex}{1ex plus .2ex}
                    \titleformat{\subsection}[hang]{\normalfont\large\bfseries}{\thesubsection}{1em}{}
                    \titlespacing*{\subsection}{0pt}{1.5ex plus 1ex minus .2ex}{1ex plus .2ex}
                    \usepackage{fontspec}
                    \usepackage[titles]{tocloft}
                    \cftsetpnumwidth {1.25cm}\cftsetrmarg{1.5cm}
                    \setlength{\cftchapnumwidth}{0.75cm}
                    \setlength{\cftsecindent}{\cftchapnumwidth}
                    \setlength{\cftsecnumwidth}{1.25cm}    
                    ''',
    'fncychap': r'\usepackage[Bjornstrup]{fncychap}',
    'figure_align': 'htbp',
    'fontpkg': r'''\usepackage{lmodern}
                   \usepackage{amsmath,amsfonts,amssymb,amsthm}
                   \usepackage{graphicx}
                ''',
    'sphinxsetup': 'hmargin={1.25in,1in}, vmargin={1in,1in}, marginpar=1in',
    'extraclassoptions': 'openany',
    'printindex': "\\def\\twocolumn[#1]{#1}\\printindex",
}
latex_show_urls = 'footnote'
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
        'donate.html',
    ]
}

html_static_path = ['_static']
html_theme = 'alabaster'
html_theme_options = {
    'github_user': 'ramonserrano76',
    'github_repo': 'crashblog',
}
templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
latex_engine = 'xelatex'  # 'lualatex' # o

source_dir = 'source'
build_dir = 'build'
out_dir = 'build/latex'
latex_documents = [('index', 'Documentation.tex', 'All Documents', 'BlogifyAR Documentation 2023', 'manual', True, 'Documentation for all components of BlogifyAR', latex_elements),
                   ('privacy_policy', 'privacy_policy.tex', 'Privacy Policy', 'Privacy policy for BlogifyAR',
                    'manual', False, 'Privacy policy for BlogifyAR', latex_elements),
                   ('terms_and_conditions', 'terms_and_conditions.tex', 'Terms and Conditions', 'Terms and conditions for using BlogifyAR', 'manual', False, 'Terms and conditions for using BlogifyAR', latex_elements)]

source_suffix = '.rst'
