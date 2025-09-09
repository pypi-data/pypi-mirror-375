"""
PyPulse: A library for pulse analysis.
"""

from .pypulse import *
from . import pulses
from . import aux_functions

# Optional: Define what is exposed when a user imports the package
__all__ = ["pypulse", "pulses", "aux_functions"]