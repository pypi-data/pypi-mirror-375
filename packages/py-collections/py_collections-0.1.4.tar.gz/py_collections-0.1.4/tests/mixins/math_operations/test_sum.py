"""Tests for the sum method in MathOperationsMixin."""

import pytest

from py_collections import Collection


class TestSumMethod:
    """Test cases for the sum method."""

    def test_sum_without_arguments(self):
        """Test sum() with no arguments - sums all numeric values."""
        # Test with integers
        numbers = Collection([1, 2, 3, 4, 5])
        assert numbers.sum() == 15

        # Test with floats
        floats = Collection([1.5, 2.5, 3.5])
        assert floats.sum() == 7.5

        # Test with mixed integers and floats
        mixed = Collection([1, 2.5, 3, 4.5])
        assert mixed.sum() == 11.0

        # Test with non-numeric values (should be ignored)
        mixed_with_strings = Collection([1, 2, "hello", 3, "world", 4])
        assert mixed_with_strings.sum() == 10

    def test_sum_with_empty_collection(self):
        """Test sum() with empty collection raises ValueError."""
        empty = Collection([])
        with pytest.raises(
            ValueError, match="No numeric values found in collection to sum"
        ):
            empty.sum()

    def test_sum_with_no_numeric_values(self):
        """Test sum() with collection containing no numeric values raises ValueError."""
        strings = Collection(["hello", "world", "test"])
        with pytest.raises(
            ValueError, match="No numeric values found in collection to sum"
        ):
            strings.sum()

    def test_sum_with_key_string(self):
        """Test sum() with a string key - sums values of that key."""
        items = Collection(
            [
                {"price": 10, "name": "item1"},
                {"price": 20, "name": "item2"},
                {"price": 30, "name": "item3"},
            ]
        )
        assert items.sum("price") == 60

        # Test with floats
        items_float = Collection(
            [
                {"price": 10.5, "name": "item1"},
                {"price": 20.5, "name": "item2"},
            ]
        )
        assert items_float.sum("price") == 31.0

    def test_sum_with_key_attribute(self):
        """Test sum() with object attributes."""

        class Item:
            def __init__(self, price: float, name: str):
                self.price = price
                self.name = name

        items = Collection(
            [
                Item(10.5, "item1"),
                Item(20.5, "item2"),
                Item(30.0, "item3"),
            ]
        )
        assert items.sum("price") == 61.0

    def test_sum_with_key_missing_from_dict(self):
        """Test sum() with missing key in dictionary raises KeyError."""
        items = Collection(
            [
                {"price": 10, "name": "item1"},
                {"name": "item2"},  # Missing price key
            ]
        )
        with pytest.raises(KeyError, match="Key 'price' not found in item"):
            items.sum("price")

    def test_sum_with_key_missing_attribute(self):
        """Test sum() with missing attribute raises AttributeError."""

        class Item:
            def __init__(self, name: str):
                self.name = name

        items = Collection(
            [
                Item("item1"),
                Item("item2"),
            ]
        )
        with pytest.raises(AttributeError, match="Item .* has no attribute 'price'"):
            items.sum("price")

    def test_sum_with_key_non_numeric_value(self):
        """Test sum() with non-numeric value for key raises TypeError."""
        items = Collection(
            [
                {"price": 10, "name": "item1"},
                {"price": "twenty", "name": "item2"},  # Non-numeric price
            ]
        )
        with pytest.raises(TypeError, match="Value for key 'price' must be numeric"):
            items.sum("price")

    def test_sum_with_callback(self):
        """Test sum() with a callback function."""
        items = Collection(
            [
                {"price": 10, "tax_rate": 0.1},
                {"price": 20, "tax_rate": 0.15},
                {"price": 30, "tax_rate": 0.2},
            ]
        )

        # Sum prices with tax
        total_with_tax = items.sum(lambda item: item["price"] * (1 + item["tax_rate"]))
        expected = 10 * 1.1 + 20 * 1.15 + 30 * 1.2
        assert total_with_tax == expected

        # Sum just the prices
        total_prices = items.sum(lambda item: item["price"])
        assert total_prices == 60

    def test_sum_with_callback_returning_non_numeric(self):
        """Test sum() with callback returning non-numeric value raises TypeError."""
        items = Collection([{"name": "item1"}, {"name": "item2"}])
        with pytest.raises(TypeError, match="Callback must return a numeric value"):
            items.sum(lambda item: item["name"])  # Returns string

    def test_sum_with_invalid_argument_type(self):
        """Test sum() with invalid argument type raises TypeError."""
        items = Collection([1, 2, 3])
        with pytest.raises(
            TypeError, match="Argument must be None, a string key, or a callable"
        ):
            items.sum(123)  # Invalid type

    def test_sum_edge_cases(self):
        """Test sum() with edge cases."""
        # Test with zero values
        zeros = Collection([0, 0, 0])
        assert zeros.sum() == 0

        # Test with negative numbers
        negatives = Collection([-1, -2, -3])
        assert negatives.sum() == -6

        # Test with mixed positive and negative
        mixed_signs = Collection([1, -2, 3, -4])
        assert mixed_signs.sum() == -2

        # Test with very large numbers
        large_numbers = Collection([1e10, 2e10, 3e10])
        assert large_numbers.sum() == 6e10

    def test_sum_with_nested_dict_keys(self):
        """Test sum() with nested dictionary keys using dot notation."""
        items = Collection(
            [
                {"product": {"price": 10, "name": "item1"}},
                {"product": {"price": 20, "name": "item2"}},
                {"product": {"price": 30, "name": "item3"}},
            ]
        )

        # This should work with the current implementation
        # Note: The current implementation doesn't support dot notation,
        # but we can test the callback approach for nested access
        total = items.sum(lambda item: item["product"]["price"])
        assert total == 60

    def test_sum_with_complex_callback(self):
        """Test sum() with complex callback logic."""
        orders = Collection(
            [
                {"items": 3, "price_per_item": 10, "discount": 0.1},
                {"items": 2, "price_per_item": 15, "discount": 0.05},
                {"items": 1, "price_per_item": 25, "discount": 0.0},
            ]
        )

        # Calculate total after discount
        total_after_discount = orders.sum(
            lambda order: order["items"]
            * order["price_per_item"]
            * (1 - order["discount"])
        )
        expected = 3 * 10 * 0.9 + 2 * 15 * 0.95 + 1 * 25 * 1.0
        assert total_after_discount == expected

    def test_sum_preserves_type(self):
        """Test that sum() preserves the numeric type."""
        # All integers should return int
        integers = Collection([1, 2, 3])
        result = integers.sum()
        assert isinstance(result, int)
        assert result == 6

        # Mixed int and float should return float
        mixed = Collection([1, 2.0, 3])
        result = mixed.sum()
        assert isinstance(result, float)
        assert result == 6.0

        # All floats should return float
        floats = Collection([1.5, 2.5, 3.5])
        result = floats.sum()
        assert isinstance(result, float)
        assert result == 7.5
