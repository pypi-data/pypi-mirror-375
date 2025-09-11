"""
PyMethyl2Sam - A Python library for methylation data processing and BAM file generation.

Copyright (c) 2025
"""

from importlib.metadata import version

__version__ = version("pymethyl2sam")

# Import core components
from .core.genomics import *
from .core.sequencing import *
from .core.errors import *
from .simulator import MethylationSimulator

__all__ = ["MethylationSimulator"]
