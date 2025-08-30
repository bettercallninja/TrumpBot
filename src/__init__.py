# src/__init__.py
__all__ = ["main", "__version__"]
__version__ = "0.1.0"

# فقط re-export: بیرون بتواند بنویسد `from src import main`
from .app import main
