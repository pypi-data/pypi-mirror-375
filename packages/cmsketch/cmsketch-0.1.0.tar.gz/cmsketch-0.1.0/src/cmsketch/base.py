from typing import Protocol, Generic, TypeVar, Self
from abc import abstractmethod


T = TypeVar("T")


class BaseCountMinSketch(Generic[T], Protocol):

    @abstractmethod
    def get_width(self) -> int:
        """Get the width of the sketch."""

    @abstractmethod
    def get_depth(self) -> int:
        """Get the depth of the sketch."""

    @abstractmethod
    def insert(self, item: T) -> None:
        """Insert an item into the sketch."""

    @abstractmethod
    def count(self, item: T) -> int:
        """Get the estimated count of an item."""

    @abstractmethod
    def clear(self) -> None:
        """Reset the sketch to initial state."""

    @abstractmethod
    def merge(self, other: Self) -> None:
        """Merge another sketch into this one."""

    @abstractmethod
    def top_k(self, k: int, candidates: list[T]) -> list[tuple[T, int]]:
        """Get the top k items from candidates."""


class BaseCountMinSketchInt(BaseCountMinSketch[int]):
    """Base class for count-min sketch for integers."""


class BaseCountMinSketchStr(BaseCountMinSketch[str]):
    """Base class for count-min sketch for strings."""
