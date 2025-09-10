from typing import Self

from cmsketch.base import (
    BaseCountMinSketch,
    BaseCountMinSketchStr,
    BaseCountMinSketchInt,
)
from .hash_util import PyHashUtil


class BasePyCountMinSketch(BaseCountMinSketch):
    """Base class for Python Count-Min Sketch implementations."""

    def __init__(self, width: int, depth: int) -> None:
        """Initialize the Count-Min Sketch.

        Args:
            width: Number of buckets in each row
            depth: Number of hash functions (rows)

        Raises:
            ValueError: If width or depth is zero
        """
        if width == 0 or depth == 0:
            raise ValueError(
                f"Width and depth must be greater than zero; Got width: {width}, depth: {depth}"
            )

        self._width = width
        self._depth = depth

        # Initialize the sketch matrix as a 1D list (like C++ implementation)
        self._sketch_matrix = [0] * (width * depth)

        # Initialize hash functions
        self._hash_functions = []
        for i in range(depth):
            self._hash_functions.append(self._create_hash_function(i))

    def _create_hash_function(self, seed: int):
        """Create a hash function with the given seed.

        This method should be implemented by subclasses to handle
        different data types (str, int, etc.).

        Args:
            seed: The seed for the hash function

        Returns:
            A hash function that maps items to column indices
        """
        raise NotImplementedError("Subclasses must implement _create_hash_function")

    def get_width(self) -> int:
        """Get the width of the sketch."""
        return self._width

    def get_depth(self) -> int:
        """Get the depth of the sketch."""
        return self._depth

    def insert(self, item) -> None:
        """Insert an item into the sketch.

        Args:
            item: The item to insert
        """
        for i in range(self._depth):
            column_index = self._hash_functions[i](item)
            # Use 1D indexing like C++ implementation: i * width + column_index
            self._sketch_matrix[i * self._width + column_index] += 1

    def count(self, item) -> int:
        """Get the estimated count of an item.

        Args:
            item: The item to count

        Returns:
            The estimated count of the item
        """
        min_count = float("inf")

        for i in range(self._depth):
            column_index = self._hash_functions[i](item)
            # Use 1D indexing like C++ implementation: i * width + column_index
            count = self._sketch_matrix[i * self._width + column_index]
            min_count = min(min_count, count)

        return int(min_count)

    def clear(self) -> None:
        """Reset the sketch to initial state."""
        # Zero out the entire 1D matrix
        for i in range(len(self._sketch_matrix)):
            self._sketch_matrix[i] = 0

    def merge(self, other: Self) -> None:
        """Merge another sketch into this one.

        Args:
            other: Another BasePyCountMinSketch to merge with

        Raises:
            ValueError: If the sketches have incompatible dimensions
        """
        if self._width != other._width or self._depth != other._depth:
            raise ValueError("Incompatible CountMinSketch dimensions for merge")

        # Merge the 1D matrices element by element
        for i in range(len(self._sketch_matrix)):
            self._sketch_matrix[i] += other._sketch_matrix[i]

    def top_k(self, k: int, candidates: list) -> list[tuple]:
        """Get the top k items from candidates.

        Args:
            k: Number of top items to return
            candidates: List of candidate items to consider

        Returns:
            List of (item, count) tuples in descending count order
        """
        # Calculate counts for all candidates
        counts = [(item, self.count(item)) for item in candidates]

        # Sort by count in descending order
        counts.sort(key=lambda x: x[1], reverse=True)

        # Return top k items
        return counts[:k]


class PyCountMinSketchStr(BasePyCountMinSketch, BaseCountMinSketchStr):
    """Python implementation of the Count-Min Sketch for strings."""

    def _create_hash_function(self, seed: int):
        """Create a hash function with the given seed.

        Args:
            seed: The seed for the hash function

        Returns:
            A hash function that maps items to column indices
        """

        def hash_func(item: str) -> int:
            # Convert string to bytes for hashing
            item_bytes = item.encode("utf-8")
            h1 = PyHashUtil.hash_bytes(item_bytes)
            h2 = PyHashUtil.combine_hashes(seed, 15445)  # SEED_BASE from C++
            combined = PyHashUtil.combine_hashes(h1, h2)
            return combined % self._width

        return hash_func


class PyCountMinSketchInt(BasePyCountMinSketch, BaseCountMinSketchInt):
    """Python implementation of the Count-Min Sketch for integers."""

    def _create_hash_function(self, seed: int):
        """Create a hash function with the given seed.

        Args:
            seed: The seed for the hash function

        Returns:
            A hash function that maps items to column indices
        """

        def hash_func(item: int) -> int:
            # Use Python's built-in hash for integers
            h1 = hash(item)
            h2 = PyHashUtil.combine_hashes(seed, 15445)  # SEED_BASE from C++
            combined = PyHashUtil.combine_hashes(h1, h2)
            return combined % self._width

        return hash_func
