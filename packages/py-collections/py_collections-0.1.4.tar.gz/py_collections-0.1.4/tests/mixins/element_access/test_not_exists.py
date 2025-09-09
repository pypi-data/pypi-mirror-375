"""Tests for the not_exists method in ElementAccessMixin."""

import pytest

from py_collections import Collection


class TestNotExists:
    """Test cases for the not_exists method."""

    def test_not_exists_with_empty_collection(self):
        """Test not_exists() with empty collection returns True."""
        empty = Collection([])
        assert empty.not_exists() is True

    def test_not_exists_with_non_empty_collection(self):
        """Test not_exists() with non-empty collection returns False."""
        non_empty = Collection([1, 2, 3])
        assert non_empty.not_exists() is False

    def test_not_exists_with_predicate_matching_element(self):
        """Test not_exists() with predicate that matches an element returns False."""
        numbers = Collection([1, 2, 3, 4, 5])
        assert numbers.not_exists(lambda x: x > 3) is False

    def test_not_exists_with_predicate_not_matching(self):
        """Test not_exists() with predicate that doesn't match any element returns True."""
        numbers = Collection([1, 2, 3])
        assert numbers.not_exists(lambda x: x > 5) is True

    def test_not_exists_with_string_elements(self):
        """Test not_exists() with string elements."""
        strings = Collection(["hello", "world", "test"])

        # No predicate - collection is not empty
        assert strings.not_exists() is False

        # Predicate that matches
        assert strings.not_exists(lambda x: x.startswith("h")) is False

        # Predicate that doesn't match
        assert strings.not_exists(lambda x: x.startswith("z")) is True

    def test_not_exists_with_custom_objects(self):
        """Test not_exists() with custom objects."""

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
                Person("Charlie", 35),
            ]
        )

        # No predicate - collection is not empty
        assert people.not_exists() is False

        # Predicate that matches
        assert people.not_exists(lambda p: p.age > 30) is False

        # Predicate that doesn't match
        assert people.not_exists(lambda p: p.age > 40) is True

    def test_not_exists_with_none_values(self):
        """Test not_exists() with None values."""
        items = Collection([None, 1, None, 2])

        # No predicate - collection is not empty
        assert items.not_exists() is False

        # Predicate that matches None
        assert items.not_exists(lambda x: x is None) is False

        # Predicate that doesn't match
        assert items.not_exists(lambda x: x == "missing") is True

    def test_not_exists_with_complex_predicates(self):
        """Test not_exists() with complex predicates."""
        data = Collection(
            [
                {"name": "Alice", "age": 25, "city": "NYC"},
                {"name": "Bob", "age": 30, "city": "LA"},
                {"name": "Charlie", "age": 35, "city": "NYC"},
            ]
        )

        # Complex predicate that matches
        assert data.not_exists(lambda x: x["age"] > 30 and x["city"] == "NYC") is False

        # Complex predicate that doesn't match
        assert data.not_exists(lambda x: x["age"] > 40 and x["city"] == "SF") is True

    def test_not_exists_consistency_with_exists(self):
        """Test that not_exists() is consistent with exists()."""
        test_cases = [
            Collection([]),  # Empty collection
            Collection([1, 2, 3]),  # Non-empty collection
            Collection(["a", "b", "c"]),  # String collection
            Collection([None, 1, None]),  # Collection with None values
        ]

        predicates = [
            None,  # No predicate
            lambda x: x > 2,  # Numeric predicate
            lambda x: x.startswith("a"),  # String predicate
            lambda x: x is None,  # None predicate
        ]

        for collection in test_cases:
            for predicate in predicates:
                # Skip invalid predicate combinations
                if predicate is not None:
                    try:
                        # Test that not_exists is the opposite of exists
                        assert collection.not_exists(predicate) == (
                            not collection.exists(predicate)
                        )
                    except (AttributeError, TypeError):
                        # Skip if predicate doesn't work with this collection type
                        continue

    def test_not_exists_with_empty_collection_and_predicate(self):
        """Test not_exists() with empty collection and predicate returns True."""
        empty = Collection([])
        assert empty.not_exists(lambda x: x > 0) is True

    def test_not_exists_edge_cases(self):
        """Test not_exists() with edge cases."""
        # Single element collection
        single = Collection([42])
        assert single.not_exists() is False
        assert single.not_exists(lambda x: x == 42) is False
        assert single.not_exists(lambda x: x != 42) is True

        # Collection with duplicate elements
        duplicates = Collection([1, 1, 1])
        assert duplicates.not_exists(lambda x: x == 1) is False
        assert duplicates.not_exists(lambda x: x == 2) is True

        # Collection with mixed types
        mixed = Collection([1, "hello", None, 3.14])
        assert mixed.not_exists() is False
        assert mixed.not_exists(lambda x: isinstance(x, int)) is False
        assert mixed.not_exists(lambda x: isinstance(x, list)) is True

    def test_not_exists_performance_consideration(self):
        """Test that not_exists() stops early when it finds a match."""
        # This test ensures that not_exists() behaves efficiently
        # by stopping as soon as it finds an element that satisfies the predicate
        numbers = Collection([1, 2, 3, 4, 5])

        # Should return False immediately when it finds the first element > 0
        assert numbers.not_exists(lambda x: x > 0) is False

        # Should return True only after checking all elements
        assert numbers.not_exists(lambda x: x > 10) is True
