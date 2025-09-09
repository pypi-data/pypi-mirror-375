from . import _core as _core
from .utils import greet
from .ops import add         

# Re-export everything from the compiled extension
from ._core import *           

# Public API
__all__ = list(globals().keys())