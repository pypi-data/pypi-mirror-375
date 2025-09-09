# __all__ ajuda IDEs/autocomplete
__all__ = ["hello", "__version__"]

# versão “fonte única”: hatch vai ler daqui (ver pyproject)
__version__ = "0.1.0"

from .core import hello
