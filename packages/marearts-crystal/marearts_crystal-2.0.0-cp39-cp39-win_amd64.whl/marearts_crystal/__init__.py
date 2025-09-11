__version__ = "2.0.0"

from .ma_crystal import ma_crystal

# Control what's exposed with 'from marearts_crystal import *'
__all__ = ['ma_crystal']

# This ensures only the ma_crystal class is exposed
# Internal implementation details remain hidden
