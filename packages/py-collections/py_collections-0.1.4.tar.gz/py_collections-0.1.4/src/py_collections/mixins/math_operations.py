"""Math operations mixin for Collection class."""

from typing import TYPE_CHECKING, Any, Callable, TypeVar, Union

if TYPE_CHECKING:
    from ..collection import Collection

T = TypeVar("T")


class MathOperationsMixin[T]:
    """Mixin providing mathematical operations for collections."""

    def sum(  # noqa: PLR0912
        self, key_or_callback: str | Callable[[T], int | float] | None = None
    ) -> int | float:
        """
        Calculate the sum of items in the collection.

        Args:
            key_or_callback: Optional key or callback function.
                - If None: sums all numeric values in the collection
                - If str: sums the values of the specified key/attribute from each item
                - If callable: sums the results returned by the callback for each item

        Returns:
            The sum of the values.

        Raises:
            ValueError: If no numeric values are found when summing without arguments.
            AttributeError: If the specified key doesn't exist on items.
            TypeError: If the callback doesn't return a numeric value.

        Examples:
            >>> numbers = Collection([1, 2, 3, 4, 5])
            >>> numbers.sum()
            15

            >>> items = Collection([{"price": 10}, {"price": 20}, {"price": 30}])
            >>> items.sum("price")
            60

            >>> items.sum(lambda x: x["price"] * 1.1)  # With 10% tax
            66.0
        """
        if key_or_callback is None:
            # Sum all numeric values in the collection
            numeric_items = [
                item for item in self._items if isinstance(item, int | float)
            ]
            if not numeric_items:
                raise ValueError("No numeric values found in collection to sum")
            return sum(numeric_items)

        elif isinstance(key_or_callback, str):
            # Sum the values of a specific key/attribute from each item
            total = 0
            for item in self._items:
                if isinstance(item, dict):
                    if key_or_callback not in item:
                        raise KeyError(
                            f"Key '{key_or_callback}' not found in item: {item}"
                        )
                    value = item[key_or_callback]
                elif hasattr(item, key_or_callback):
                    value = getattr(item, key_or_callback)
                else:
                    raise AttributeError(
                        f"Item {item} has no attribute '{key_or_callback}'"
                    )

                if not isinstance(value, int | float):
                    raise TypeError(
                        f"Value for key '{key_or_callback}' must be numeric, got {type(value).__name__}"
                    )

                total += value
            return total

        elif callable(key_or_callback):
            # Sum the results returned by the callback for each item
            total = 0
            for item in self._items:
                result = key_or_callback(item)
                if not isinstance(result, int | float):
                    raise TypeError(
                        f"Callback must return a numeric value, got {type(result).__name__}"
                    )
                total += result
            return total

        else:
            raise TypeError("Argument must be None, a string key, or a callable")
