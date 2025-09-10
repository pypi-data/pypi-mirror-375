from .base import BaseCountMinSketchStr, BaseCountMinSketchInt

class CountMinSketchStr(BaseCountMinSketchStr):
    """Count-Min Sketch for string items."""

    def __init__(self, width: int, depth: int) -> None:
        """Create a Count-Min Sketch with specified dimensions."""
        ...

class CountMinSketchInt(BaseCountMinSketchInt):
    """Count-Min Sketch for integer items."""

    def __init__(self, width: int, depth: int) -> None:
        """Create a Count-Min Sketch for integers with specified dimensions."""
        ...
