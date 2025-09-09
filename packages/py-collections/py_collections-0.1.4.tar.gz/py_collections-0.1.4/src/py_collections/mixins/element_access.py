"""Element access mixin for Collection class."""

from collections import Counter
from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar, Union

if TYPE_CHECKING:
    from ..collection import Collection

T = TypeVar("T")


class ItemNotFoundException(Exception):
    """Exception raised when an item is not found in the collection."""


class ElementAccessMixin[T]:
    """Mixin providing element access methods."""

    def first(self, predicate: Callable[[T], bool] | None = None) -> T | None:
        """
        Get the first element in the collection.

        Args:
            predicate: Optional callable that takes an item and returns a boolean.
                      If provided, returns the first element that satisfies the predicate.
                      If None, returns the first element in the collection.

        Returns:
            The first element that satisfies the predicate, or the first element if no predicate is provided.
            Returns None if the collection is empty or no element satisfies the predicate.
        """
        index = self._find_first_index(predicate)
        return self._items[index] if index is not None else None

    def exists(self, predicate: Callable[[T], bool] | None = None) -> bool:
        """
        Check if an element exists in the collection.

        Args:
            predicate: Optional callable that takes an item and returns a boolean.
                      If provided, checks if any element satisfies the predicate.
                      If None, checks if the collection is not empty.

        Returns:
            True if an element exists that satisfies the predicate (or if collection is not empty when no predicate),
            False otherwise.
        """
        return self._find_first_index(predicate) is not None

    def not_exists(self, predicate: Callable[[T], bool] | None = None) -> bool:
        """
        Check if no element exists in the collection that satisfies the predicate.

        Args:
            predicate: Optional callable that takes an item and returns a boolean.
                      If provided, checks if no element satisfies the predicate.
                      If None, checks if the collection is empty.

        Returns:
            True if no element exists that satisfies the predicate (or if collection is empty when no predicate),
            False otherwise.
        """
        return not self.exists(predicate)

    def find_duplicates(  # noqa: PLR0912
        self, key_or_callback: str | Callable[[T], any] | None = None
    ) -> "Collection[T]":
        """
        Find duplicate items in the collection.

        Args:
            key_or_callback: Optional key or callback function.
                - If None: compares objects directly to find duplicates
                - If str: extracts values from the specified key/attribute and finds duplicates based on those values
                - If callable: applies the callback to each item and finds duplicates based on the results

        Returns:
            A new Collection containing one instance of each duplicate item (items that appear more than once).

        Examples:
            >>> numbers = Collection([1, 2, 2, 3, 3, 3])
            >>> numbers.find_duplicates()
            Collection([2, 3])

            >>> items = Collection([{"id": 1}, {"id": 2}, {"id": 1}])
            >>> items.find_duplicates("id")
            Collection([{"id": 1}])

            >>> items.find_duplicates(lambda x: x["id"])
            Collection([{"id": 1}])
        """
        if not self._items:
            # Create Collection instance dynamically to avoid circular import
            from ..collection import Collection

            return Collection([])

        # Determine what to compare for duplicates
        if key_or_callback is None:
            # Compare objects directly
            values_to_compare = self._items
        elif isinstance(key_or_callback, str):
            # Extract values from the specified key/attribute
            values_to_compare = []
            for item in self._items:
                if isinstance(item, dict):
                    if key_or_callback not in item:
                        raise KeyError(
                            f"Key '{key_or_callback}' not found in item: {item}"
                        )
                    values_to_compare.append(item[key_or_callback])
                elif hasattr(item, key_or_callback):
                    values_to_compare.append(getattr(item, key_or_callback))
                else:
                    raise AttributeError(
                        f"Item {item} has no attribute '{key_or_callback}'"
                    )
        elif callable(key_or_callback):
            # Apply callback to each item
            values_to_compare = [key_or_callback(item) for item in self._items]
        else:
            raise TypeError("Argument must be None, a string key, or a callable")

        # Count occurrences of each value
        # Handle unhashable types by converting to tuples for counting
        try:
            value_counts = Counter(values_to_compare)
        except TypeError:
            # If values are unhashable, use a different approach
            value_counts = {}
            for value in values_to_compare:
                # Convert to string representation for unhashable types
                key = (
                    str(value)
                    if not isinstance(value, int | float | str | bool | type(None))
                    else value
                )
                value_counts[key] = value_counts.get(key, 0) + 1

        # Find items that appear more than once (only one instance of each duplicate)
        duplicate_items = []
        seen_duplicates = set()
        for i, value in enumerate(values_to_compare):
            # Use the same key strategy for checking counts
            key = (
                str(value)
                if not isinstance(value, int | float | str | bool | type(None))
                else value
            )
            if value_counts[key] > 1 and key not in seen_duplicates:
                duplicate_items.append(self._items[i])
                seen_duplicates.add(key)

        # Create Collection instance dynamically to avoid circular import
        from ..collection import Collection

        return Collection(duplicate_items)

    def find_uniques(  # noqa: PLR0912
        self, key_or_callback: str | Callable[[T], any] | None = None
    ) -> "Collection[T]":
        """
        Find unique items in the collection (items that appear exactly once).

        Args:
            key_or_callback: Optional key or callback function.
                - If None: compares objects directly to find unique items
                - If str: extracts values from the specified key/attribute and finds unique items based on those values
                - If callable: applies the callback to each item and finds unique items based on the results

        Returns:
            A new Collection containing only the unique items (items that appear exactly once).

        Examples:
            >>> numbers = Collection([1, 2, 2, 3, 3, 3, 4])
            >>> numbers.find_uniques()
            Collection([1, 4])

            >>> items = Collection([{"id": 1}, {"id": 2}, {"id": 1}, {"id": 3}])
            >>> items.find_uniques("id")
            Collection([{"id": 2}, {"id": 3}])

            >>> items.find_uniques(lambda x: x["id"])
            Collection([{"id": 2}, {"id": 3}])
        """
        if not self._items:
            # Create Collection instance dynamically to avoid circular import
            from ..collection import Collection

            return Collection([])

        # Determine what to compare for uniqueness
        if key_or_callback is None:
            # Compare objects directly
            values_to_compare = self._items
        elif isinstance(key_or_callback, str):
            # Extract values from the specified key/attribute
            values_to_compare = []
            for item in self._items:
                if isinstance(item, dict):
                    if key_or_callback not in item:
                        raise KeyError(
                            f"Key '{key_or_callback}' not found in item: {item}"
                        )
                    values_to_compare.append(item[key_or_callback])
                elif hasattr(item, key_or_callback):
                    values_to_compare.append(getattr(item, key_or_callback))
                else:
                    raise AttributeError(
                        f"Item {item} has no attribute '{key_or_callback}'"
                    )
        elif callable(key_or_callback):
            # Apply callback to each item
            values_to_compare = [key_or_callback(item) for item in self._items]
        else:
            raise TypeError("Argument must be None, a string key, or a callable")

        # Count occurrences of each value
        # Handle unhashable types by converting to tuples for counting
        try:
            value_counts = Counter(values_to_compare)
        except TypeError:
            # If values are unhashable, use a different approach
            value_counts = {}
            for value in values_to_compare:
                # Convert to string representation for unhashable types
                key = (
                    str(value)
                    if not isinstance(value, int | float | str | bool | type(None))
                    else value
                )
                value_counts[key] = value_counts.get(key, 0) + 1

        # Find items that appear exactly once
        unique_items = []
        for i, value in enumerate(values_to_compare):
            # Use the same key strategy for checking counts
            key = (
                str(value)
                if not isinstance(value, int | float | str | bool | type(None))
                else value
            )
            if value_counts[key] == 1:
                unique_items.append(self._items[i])

        # Create Collection instance dynamically to avoid circular import
        from ..collection import Collection

        return Collection(unique_items)

    def first_or_raise(self, predicate: Callable[[T], bool] | None = None) -> T:
        """
        Get the first element in the collection or raise ItemNotFoundException if not found.

        Args:
            predicate: Optional callable that takes an item and returns a boolean.
                      If provided, returns the first element that satisfies the predicate.
                      If None, returns the first element in the collection.

        Returns:
            The first element that satisfies the predicate, or the first element if no predicate is provided.

        Raises:
            ItemNotFoundException: If the collection is empty or no element satisfies the predicate.
        """
        index = self._find_first_index(predicate)
        if index is None:
            if not self._items:
                raise ItemNotFoundException(
                    "Cannot get first element from empty collection"
                )
            else:
                raise ItemNotFoundException("No element satisfies the predicate")
        return self._items[index]

    def last(self) -> T:
        """
        Get the last element in the collection.

        Returns:
            The last element in the collection.

        Raises:
            IndexError: If the collection is empty.
        """
        if not self._items:
            raise IndexError("Cannot get last element from empty collection")
        return self._items[-1]

    def _find_first_index(
        self, predicate: Callable[[T], bool] | None = None
    ) -> int | None:
        """
        Find the index of the first element that satisfies the predicate.

        Args:
            predicate: Optional callable that takes an item and returns a boolean.
                      If None, returns 0 (first element).

        Returns:
            Index of the first matching element, or None if not found.
        """
        if not self._items:
            return None

        if predicate is None:
            return 0

        for i, item in enumerate(self._items):
            if predicate(item):
                return i

        return None
