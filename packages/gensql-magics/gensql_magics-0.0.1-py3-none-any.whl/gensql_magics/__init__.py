from .magic import GenSQLMagics

__version__ = "0.0.1"

# Load the magic
def load_ipython_extension(ipython):
    ipython.register_magics(GenSQLMagics)