"""
Count-Min Sketch Python bindings

A high-performance implementation of the Count-Min Sketch probabilistic data structure.
"""

from importlib.metadata import version

from cmsketch.base import (
    BaseCountMinSketch,
    BaseCountMinSketchStr,
    BaseCountMinSketchInt,
)
from cmsketch._core import (
    CountMinSketchStr,
    CountMinSketchInt,
)
from cmsketch.py.count_min_sketch import (
    PyCountMinSketchStr,
    PyCountMinSketchInt,
)


__version__ = version("cmsketch")

__all__ = [
    "BaseCountMinSketch",
    "BaseCountMinSketchStr",
    "BaseCountMinSketchInt",
    "CountMinSketchStr",
    "CountMinSketchInt",
    "PyCountMinSketchStr",
    "PyCountMinSketchInt",
]
