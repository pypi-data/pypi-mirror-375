"""Main Collection class that combines all mixins."""

from typing import TypeVar

from .mixins import (
    BasicOperationsMixin,
    ElementAccessMixin,
    GroupingMixin,
    MathOperationsMixin,
    NavigationMixin,
    RemovalMixin,
    TransformationMixin,
    UtilityMixin,
)

T = TypeVar("T")


class Collection[T](
    BasicOperationsMixin[T],
    ElementAccessMixin[T],
    NavigationMixin[T],
    TransformationMixin[T],
    GroupingMixin[T],
    RemovalMixin[T],
    UtilityMixin[T],
    MathOperationsMixin[T],
):
    """
    A collection class that wraps a list and provides methods to manipulate it.

    This class combines functionality from multiple mixins:
    - BasicOperationsMixin: append, extend, all, len, iteration
    - ElementAccessMixin: first, last, exists, first_or_raise
    - NavigationMixin: after, before
    - TransformationMixin: map, pluck, filter, reverse, clone
    - GroupingMixin: group_by, chunk
    - RemovalMixin: remove, remove_one
    - UtilityMixin: take, dump_me, dump_me_and_die
    - MathOperationsMixin: sum

    Args:
        items: Optional list of items to initialize the collection with.
               If not provided, an empty list will be used.
    """

    def __init__(self, items: list[T] | None = None):
        """
        Initialize the collection with items.

        Args:
            items: Optional list of items to initialize the collection with.
                   If not provided, an empty list will be used.
        """
        self._items = items.copy() if items is not None else []

    def __str__(self) -> str:
        """Return a string representation of the collection."""
        return f"{self.__class__.__name__}({self._items})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the collection."""
        return f"{self.__class__.__name__}({self._items})"

    def __len__(self) -> int:
        """Return the number of items in the collection."""
        return len(self._items)

    def __iter__(self):
        """
        Return an iterator over the collection's items.

        Returns:
            An iterator that yields each item in the collection.
        """
        return iter(self._items)

    def __eq__(self, other) -> bool:
        """
        Check if two collections are equal.

        Args:
            other: Another collection or object to compare with.

        Returns:
            True if both collections contain the same items in the same order, False otherwise.
        """
        if not isinstance(other, Collection):
            return False
        return self._items == other._items

    def __getitem__(self, index):
        """
        Get an item from the collection by index.

        Args:
            index: The index of the item to retrieve.

        Returns:
            The item at the specified index.

        Raises:
            IndexError: If the index is out of range.
        """
        return self._items[index]

    def __add__(self, other):
        """
        Add two collections together.

        Args:
            other: Another collection to add to this one.

        Returns:
            A new Collection containing all items from both collections.
        """
        if not isinstance(other, Collection):
            raise TypeError(f"Can only add Collection to Collection, not {type(other)}")

        new_items = self._items + other._items
        return Collection(new_items)
