"""Tests for the find_uniques method in ElementAccessMixin."""

import pytest

from py_collections import Collection


class TestFindUniques:
    """Test cases for the find_uniques method."""

    def test_find_uniques_without_arguments(self):
        """Test find_uniques() with no arguments - compares objects directly."""
        # Test with integers
        numbers = Collection([1, 2, 2, 3, 3, 3, 4])
        uniques = numbers.find_uniques()
        assert uniques == Collection([1, 4])

        # Test with strings
        strings = Collection(["a", "b", "b", "c", "c", "c", "d"])
        uniques = strings.find_uniques()
        assert uniques == Collection(["a", "d"])

        # Test with mixed uniques
        mixed = Collection([1, "hello", 1, "world", "hello", 2])
        uniques = mixed.find_uniques()
        assert uniques == Collection(["world", 2])

    def test_find_uniques_with_empty_collection(self):
        """Test find_uniques() with empty collection returns empty collection."""
        empty = Collection([])
        uniques = empty.find_uniques()
        assert uniques == Collection([])

    def test_find_uniques_with_all_duplicates(self):
        """Test find_uniques() with collection containing only duplicates."""
        all_duplicates = Collection([1, 1, 2, 2, 3, 3])
        uniques = all_duplicates.find_uniques()
        assert uniques == Collection([])

    def test_find_uniques_with_all_unique(self):
        """Test find_uniques() with collection containing all unique items."""
        all_unique = Collection([1, 2, 3, 4, 5])
        uniques = all_unique.find_uniques()
        assert uniques == Collection([1, 2, 3, 4, 5])

    def test_find_uniques_with_key_string(self):
        """Test find_uniques() with a string key - finds unique items based on key values."""
        items = Collection(
            [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
                {"id": 1, "name": "Alice Duplicate"},
                {"id": 3, "name": "Charlie"},
                {"id": 2, "name": "Bob Duplicate"},
                {"id": 4, "name": "David"},
            ]
        )
        uniques = items.find_uniques("id")
        expected = Collection(
            [
                {"id": 3, "name": "Charlie"},
                {"id": 4, "name": "David"},
            ]
        )
        assert uniques == expected

    def test_find_uniques_with_key_attribute(self):
        """Test find_uniques() with object attributes."""

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
                Person("David", 28),  # Unique name
            ]
        )

        uniques = people.find_uniques("name")
        assert len(uniques) == 2  # Charlie and David
        assert uniques[0].name == "Charlie"
        assert uniques[1].name == "David"

    def test_find_uniques_with_key_missing_from_dict(self):
        """Test find_uniques() with missing key in dictionary raises KeyError."""
        items = Collection(
            [
                {"id": 1, "name": "Alice"},
                {"name": "Bob"},  # Missing id key
            ]
        )
        with pytest.raises(KeyError, match="Key 'id' not found in item"):
            items.find_uniques("id")

    def test_find_uniques_with_key_missing_attribute(self):
        """Test find_uniques() with missing attribute raises AttributeError."""

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
            people.find_uniques("age")

    def test_find_uniques_with_callback(self):
        """Test find_uniques() with a callback function."""
        items = Collection(
            [
                {"id": 1, "name": "Alice", "department": "Engineering"},
                {"id": 2, "name": "Bob", "department": "Sales"},
                {"id": 3, "name": "Charlie", "department": "Engineering"},
                {"id": 4, "name": "David", "department": "Sales"},
                {"id": 5, "name": "Eve", "department": "Marketing"},
            ]
        )

        # Find unique items based on department
        uniques = items.find_uniques(lambda x: x["department"])
        assert len(uniques) == 1  # Only Marketing is unique
        assert uniques[0]["department"] == "Marketing"

    def test_find_uniques_with_complex_callback(self):
        """Test find_uniques() with complex callback logic."""
        orders = Collection(
            [
                {"customer_id": 1, "amount": 100, "status": "completed"},
                {"customer_id": 2, "amount": 200, "status": "pending"},
                {"customer_id": 1, "amount": 150, "status": "completed"},
                {"customer_id": 3, "amount": 300, "status": "completed"},
                {"customer_id": 2, "amount": 250, "status": "completed"},
            ]
        )

        # Find unique items based on customer_id
        uniques = orders.find_uniques(lambda x: x["customer_id"])
        assert len(uniques) == 1  # Only customer 3 is unique

        customer_ids = [order["customer_id"] for order in uniques]
        assert customer_ids == [3]

    def test_find_uniques_with_invalid_argument_type(self):
        """Test find_uniques() with invalid argument type raises TypeError."""
        items = Collection([1, 2, 3])
        with pytest.raises(
            TypeError, match="Argument must be None, a string key, or a callable"
        ):
            items.find_uniques(123)  # Invalid type

    def test_find_uniques_edge_cases(self):
        """Test find_uniques() with edge cases."""
        # Single element (unique)
        single = Collection([42])
        assert single.find_uniques() == Collection([42])

        # All elements are the same (no uniques)
        all_same = Collection([1, 1, 1, 1])
        uniques = all_same.find_uniques()
        assert uniques == Collection([])

        # None values
        with_none = Collection([1, None, 2, None, 3])
        uniques = with_none.find_uniques()
        assert uniques == Collection([1, 2, 3])

        # Mixed types with uniques
        mixed_types = Collection([1, "hello", 1, "world", "hello", 2])
        uniques = mixed_types.find_uniques()
        assert uniques == Collection(["world", 2])

    def test_find_uniques_preserves_order(self):
        """Test that find_uniques() preserves the original order of items."""
        items = Collection([1, 2, 1, 3, 2, 4, 1])
        uniques = items.find_uniques()
        assert uniques == Collection([3, 4])

    def test_find_uniques_with_nested_dict_keys(self):
        """Test find_uniques() with nested dictionary keys using callback."""
        items = Collection(
            [
                {"user": {"id": 1, "name": "Alice"}},
                {"user": {"id": 2, "name": "Bob"}},
                {"user": {"id": 1, "name": "Alice Duplicate"}},
                {"user": {"id": 3, "name": "Charlie"}},
            ]
        )

        # Use callback to access nested key
        uniques = items.find_uniques(lambda x: x["user"]["id"])
        assert len(uniques) == 2
        assert uniques[0]["user"]["id"] == 2
        assert uniques[1]["user"]["id"] == 3

    def test_find_uniques_with_custom_objects_and_callback(self):
        """Test find_uniques() with custom objects and callback."""

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

        # Find unique items based on category
        uniques = products.find_uniques(lambda p: p.category)
        assert len(uniques) == 2  # Books and Office are unique
        categories = [p.category for p in uniques]
        assert "Books" in categories
        assert "Office" in categories

    def test_find_uniques_returns_new_collection(self):
        """Test that find_uniques() returns a new Collection instance."""
        original = Collection([1, 2, 1, 3])
        uniques = original.find_uniques()

        # Should be a new Collection instance
        assert uniques is not original
        assert isinstance(uniques, Collection)

        # Original should be unchanged
        assert original == Collection([1, 2, 1, 3])

    def test_find_uniques_with_hashable_and_unhashable_types(self):
        """Test find_uniques() with different types of values."""
        # Hashable types (should work fine)
        hashable_items = Collection([1, 2, 1, "hello", "world", "hello", 3])
        uniques = hashable_items.find_uniques()
        assert uniques == Collection([2, "world", 3])

        # Unhashable types (lists, dicts) - should work with direct comparison
        unhashable_items = Collection([[1, 2], [3, 4], [1, 2], [5, 6]])
        uniques = unhashable_items.find_uniques()
        assert uniques == Collection([[3, 4], [5, 6]])

    def test_find_uniques_performance_with_large_collection(self):
        """Test find_uniques() performance considerations."""
        # Create a large collection with some unique items
        large_data = [*list(range(1000)), 500, 501, 502]  # Add some duplicates
        collection = Collection(large_data)

        uniques = collection.find_uniques()
        # Should have 997 unique items (1000 original - 3 duplicates)
        assert len(uniques) == 997
        # The duplicates should not be in the uniques
        assert 500 not in uniques
        assert 501 not in uniques
        assert 502 not in uniques

    def test_find_uniques_vs_find_duplicates_complementary(self):
        """Test that find_uniques() and find_duplicates() identify different items."""
        items = Collection([1, 2, 2, 3, 3, 3, 4])

        uniques = items.find_uniques()
        duplicates = items.find_duplicates()

        # Check that we have the right counts
        assert len(uniques) == 2  # 1 and 4
        assert len(duplicates) == 2  # 2 and 3 (one instance of each duplicate)

        # Check that uniques and duplicates don't overlap
        unique_values = set(uniques)
        duplicate_values = set(duplicates)
        assert unique_values.isdisjoint(duplicate_values)

        # Check specific values
        assert 1 in uniques
        assert 4 in uniques
        assert 2 in duplicates
        assert 3 in duplicates

    def test_find_uniques_with_single_occurrence_items(self):
        """Test find_uniques() specifically with items that appear exactly once."""
        items = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        uniques = items.find_uniques()

        # All items should be unique
        assert uniques == items
        assert len(uniques) == 10

    def test_find_uniques_with_mixed_frequency_items(self):
        """Test find_uniques() with items that appear different numbers of times."""
        items = Collection([1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5])
        uniques = items.find_uniques()

        # Only items 1 and 5 appear exactly once
        assert uniques == Collection([1, 5])
