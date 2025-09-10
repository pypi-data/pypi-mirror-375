# conf.py
def set_path(source = "cdxcore"):
    import os, sys
    root_path = os.path.split(
                os.path.split(  
                  os.path.split( __file__ )[0] # 'source
                  )[0] # 'docs'
                )[0] # 'packag
    assert root_path[-len(source):] == source, f"Conf.py '{__file__}': invalid source path '{root_path}'. Call 'make html' from the docs directory"
    sys.path.insert(0, root_path)  # so your package is importable
    

project = "cdxcore"
author = "Hans Buehler"
release = "0.1.0"

set_path(project)

extensions = [
    "sphinx.ext.autodoc",           # core: import & docstrings
    "sphinx.ext.autosummary",       # summary tables with links
    "sphinx.ext.napoleon",          # Google/NumPy style docstrings
    "sphinx_autodoc_typehints",     # nicer type hints formatting
    "sphinx.ext.mathjax",           # math rendering
]

autosummary_generate = True         # make _autosummary files
autodoc_typehints = "description"   # show types in doc body instead of signature
autodoc_member_order = "bysource"   # preserve order in source file
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_use_param = True
napoleon_use_rtype = False
autoclass_content = "both"

