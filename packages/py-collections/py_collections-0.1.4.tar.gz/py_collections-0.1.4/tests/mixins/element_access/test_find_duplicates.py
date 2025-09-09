"""Tests for the find_duplicates method in ElementAccessMixin."""

import pytest

from py_collections import Collection


class TestFindDuplicates:
    """Test cases for the find_duplicates method."""

    def test_find_duplicates_without_arguments(self):
        """Test find_duplicates() with no arguments - compares objects directly."""
        # Test with integers
        numbers = Collection([1, 2, 2, 3, 3, 3])
        duplicates = numbers.find_duplicates()
        assert duplicates == Collection([2, 3])

        # Test with strings
        strings = Collection(["a", "b", "b", "c", "c", "c"])
        duplicates = strings.find_duplicates()
        assert duplicates == Collection(["b", "c"])

        # Test with mixed duplicates
        mixed = Collection([1, "hello", 1, "world", "hello", 2])
        duplicates = mixed.find_duplicates()
        assert duplicates == Collection([1, "hello"])

    def test_find_duplicates_with_empty_collection(self):
        """Test find_duplicates() with empty collection returns empty collection."""
        empty = Collection([])
        duplicates = empty.find_duplicates()
        assert duplicates == Collection([])

    def test_find_duplicates_with_no_duplicates(self):
        """Test find_duplicates() with collection containing no duplicates."""
        unique = Collection([1, 2, 3, 4, 5])
        duplicates = unique.find_duplicates()
        assert duplicates == Collection([])

    def test_find_duplicates_with_key_string(self):
        """Test find_duplicates() with a string key - finds duplicates based on key values."""
        items = Collection(
            [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
                {"id": 1, "name": "Alice Duplicate"},
                {"id": 3, "name": "Charlie"},
                {"id": 2, "name": "Bob Duplicate"},
            ]
        )
        duplicates = items.find_duplicates("id")
        expected = Collection(
            [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ]
        )
        assert duplicates == expected

    def test_find_duplicates_with_key_attribute(self):
        """Test find_duplicates() with object attributes."""

        class Person:
            def __init__(self, name: str, age: int):
                self.name = name
                self.age = age

            def __repr__(self):
                return f"Person(name='{self.name}', age={self.age})"

        people = Collection(
            [
                Person("Alice", 25),
                Person("Bob", 30),
                Person("Alice", 35),  # Same name, different age
                Person("Charlie", 25),
                Person("Bob", 40),  # Same name, different age
            ]
        )

        duplicates = people.find_duplicates("name")
        assert len(duplicates) == 2  # One Alice and one Bob
        assert duplicates[0].name == "Alice"
        assert duplicates[1].name == "Bob"

    def test_find_duplicates_with_key_missing_from_dict(self):
        """Test find_duplicates() with missing key in dictionary raises KeyError."""
        items = Collection(
            [
                {"id": 1, "name": "Alice"},
                {"name": "Bob"},  # Missing id key
            ]
        )
        with pytest.raises(KeyError, match="Key 'id' not found in item"):
            items.find_duplicates("id")

    def test_find_duplicates_with_key_missing_attribute(self):
        """Test find_duplicates() with missing attribute raises AttributeError."""

        class Person:
            def __init__(self, name: str):
                self.name = name

        people = Collection(
            [
                Person("Alice"),
                Person("Bob"),
            ]
        )
        with pytest.raises(AttributeError, match="Item .* has no attribute 'age'"):
            people.find_duplicates("age")

    def test_find_duplicates_with_callback(self):
        """Test find_duplicates() with a callback function."""
        items = Collection(
            [
                {"id": 1, "name": "Alice", "department": "Engineering"},
                {"id": 2, "name": "Bob", "department": "Sales"},
                {"id": 3, "name": "Charlie", "department": "Engineering"},
                {"id": 4, "name": "David", "department": "Sales"},
                {"id": 5, "name": "Eve", "department": "Marketing"},
            ]
        )

        # Find duplicates based on department
        duplicates = items.find_duplicates(lambda x: x["department"])
        assert len(duplicates) == 2  # One Engineering, one Sales
        departments = [item["department"] for item in duplicates]
        assert departments.count("Engineering") == 1
        assert departments.count("Sales") == 1

    def test_find_duplicates_with_complex_callback(self):
        """Test find_duplicates() with complex callback logic."""
        orders = Collection(
            [
                {"customer_id": 1, "amount": 100, "status": "completed"},
                {"customer_id": 2, "amount": 200, "status": "pending"},
                {"customer_id": 1, "amount": 150, "status": "completed"},
                {"customer_id": 3, "amount": 300, "status": "completed"},
                {"customer_id": 2, "amount": 250, "status": "completed"},
            ]
        )

        # Find duplicates based on customer_id
        duplicates = orders.find_duplicates(lambda x: x["customer_id"])
        assert len(duplicates) == 2  # One order for customer 1, one for customer 2

        customer_ids = [order["customer_id"] for order in duplicates]
        assert customer_ids.count(1) == 1
        assert customer_ids.count(2) == 1

    def test_find_duplicates_with_invalid_argument_type(self):
        """Test find_duplicates() with invalid argument type raises TypeError."""
        items = Collection([1, 2, 3])
        with pytest.raises(
            TypeError, match="Argument must be None, a string key, or a callable"
        ):
            items.find_duplicates(123)  # Invalid type

    def test_find_duplicates_edge_cases(self):
        """Test find_duplicates() with edge cases."""
        # Single element (no duplicates)
        single = Collection([42])
        assert single.find_duplicates() == Collection([])

        # All elements are the same
        all_same = Collection([1, 1, 1, 1])
        duplicates = all_same.find_duplicates()
        assert duplicates == Collection([1])

        # None values
        with_none = Collection([1, None, 2, None, 3])
        duplicates = with_none.find_duplicates()
        assert duplicates == Collection([None])

        # Mixed types with duplicates
        mixed_types = Collection([1, "hello", 1, "world", "hello"])
        duplicates = mixed_types.find_duplicates()
        assert duplicates == Collection([1, "hello"])

    def test_find_duplicates_preserves_order(self):
        """Test that find_duplicates() preserves the original order of items."""
        items = Collection([1, 2, 1, 3, 2, 4, 1])
        duplicates = items.find_duplicates()
        assert duplicates == Collection([1, 2])

    def test_find_duplicates_with_nested_dict_keys(self):
        """Test find_duplicates() with nested dictionary keys using callback."""
        items = Collection(
            [
                {"user": {"id": 1, "name": "Alice"}},
                {"user": {"id": 2, "name": "Bob"}},
                {"user": {"id": 1, "name": "Alice Duplicate"}},
            ]
        )

        # Use callback to access nested key
        duplicates = items.find_duplicates(lambda x: x["user"]["id"])
        assert len(duplicates) == 1
        assert duplicates[0]["user"]["id"] == 1

    def test_find_duplicates_with_custom_objects_and_callback(self):
        """Test find_duplicates() with custom objects and callback."""

        class Product:
            def __init__(self, name: str, category: str, price: float):
                self.name = name
                self.category = category
                self.price = price

            def __repr__(self):
                return f"Product(name='{self.name}', category='{self.category}', price={self.price})"

        products = Collection(
            [
                Product("Laptop", "Electronics", 999.99),
                Product("Mouse", "Electronics", 29.99),
                Product("Book", "Books", 19.99),
                Product("Keyboard", "Electronics", 79.99),
                Product("Pen", "Office", 2.99),
            ]
        )

        # Find duplicates based on category
        duplicates = products.find_duplicates(lambda p: p.category)
        assert len(duplicates) == 1  # One Electronics item
        categories = [p.category for p in duplicates]
        assert categories.count("Electronics") == 1

    def test_find_duplicates_returns_new_collection(self):
        """Test that find_duplicates() returns a new Collection instance."""
        original = Collection([1, 2, 1, 3])
        duplicates = original.find_duplicates()

        # Should be a new Collection instance
        assert duplicates is not original
        assert isinstance(duplicates, Collection)

        # Original should be unchanged
        assert original == Collection([1, 2, 1, 3])

    def test_find_duplicates_with_hashable_and_unhashable_types(self):
        """Test find_duplicates() with different types of values."""
        # Hashable types (should work fine)
        hashable_items = Collection([1, 2, 1, "hello", "world", "hello"])
        duplicates = hashable_items.find_duplicates()
        assert duplicates == Collection([1, "hello"])

        # Unhashable types (lists, dicts) - should work with direct comparison
        unhashable_items = Collection([[1, 2], [3, 4], [1, 2]])
        duplicates = unhashable_items.find_duplicates()
        assert duplicates == Collection([[1, 2]])

    def test_find_duplicates_performance_with_large_collection(self):
        """Test find_duplicates() performance considerations."""
        # Create a large collection with some duplicates
        large_data = [*list(range(1000)), 500, 501, 502]  # Add some duplicates
        collection = Collection(large_data)

        duplicates = collection.find_duplicates()
        assert len(duplicates) == 3  # Three duplicate items (one instance of each)
        assert duplicates == Collection([500, 501, 502])
