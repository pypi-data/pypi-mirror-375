#!/usr/bin/env python3
"""
Example demonstrating the find_duplicates method.

This example shows how find_duplicates returns only one instance of each duplicate item.
"""

from py_collections import Collection


def main():
    print("=== find_duplicates Example ===\n")

    # Example 1: Basic duplicates with integers
    print("1. Basic duplicates with integers:")
    numbers = Collection([1, 2, 2, 3, 3, 3, 4])
    duplicates = numbers.find_duplicates()
    print(f"   Original: {numbers}")
    print(f"   Duplicates: {duplicates}")
    print("   Expected: Collection([2, 3]) - only one instance of each duplicate")
    print()

    # Example 2: Duplicates with string key
    print("2. Duplicates with string key:")
    users = Collection(
        [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 1, "name": "Alice Duplicate"},
            {"id": 3, "name": "Charlie"},
            {"id": 2, "name": "Bob Duplicate"},
        ]
    )
    duplicate_users = users.find_duplicates("id")
    print(f"   Original: {users}")
    print(f"   Duplicates by ID: {duplicate_users}")
    print(
        '   Expected: Collection([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])'
    )
    print()

    # Example 3: Duplicates with callback function
    print("3. Duplicates with callback function:")
    products = Collection(
        [
            {"name": "Laptop", "category": "Electronics"},
            {"name": "Mouse", "category": "Electronics"},
            {"name": "Book", "category": "Books"},
            {"name": "Keyboard", "category": "Electronics"},
            {"name": "Pen", "category": "Office"},
        ]
    )
    duplicate_categories = products.find_duplicates(lambda p: p["category"])
    print(f"   Original: {products}")
    print(f"   Duplicates by category: {duplicate_categories}")
    print('   Expected: Collection([{"name": "Laptop", "category": "Electronics"}])')
    print()

    # Example 4: Edge cases
    print("4. Edge cases:")

    # Empty collection
    empty = Collection([])
    empty_duplicates = empty.find_duplicates()
    print(f"   Empty collection: {empty_duplicates}")

    # No duplicates
    unique = Collection([1, 2, 3, 4, 5])
    unique_duplicates = unique.find_duplicates()
    print(f"   No duplicates: {unique_duplicates}")

    # All same elements
    all_same = Collection([1, 1, 1, 1])
    all_same_duplicates = all_same.find_duplicates()
    print(f"   All same elements: {all_same_duplicates}")
    print()

    # Example 5: Mixed types
    print("5. Mixed types:")
    mixed = Collection([1, "hello", 1, "world", "hello", 2])
    mixed_duplicates = mixed.find_duplicates()
    print(f"   Mixed types: {mixed}")
    print(f"   Duplicates: {mixed_duplicates}")
    print('   Expected: Collection([1, "hello"])')
    print()

    print("=== Summary ===")
    print(
        "The find_duplicates method now returns only one instance of each duplicate item."
    )
    print("This makes it easier to identify which items are duplicated without getting")
    print("multiple copies of the same duplicate item.")


if __name__ == "__main__":
    main()
