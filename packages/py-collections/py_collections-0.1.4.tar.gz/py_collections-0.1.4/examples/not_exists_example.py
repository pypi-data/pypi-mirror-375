#!/usr/bin/env python3
"""
Example demonstrating the not_exists method in py-collections.

This example shows how to use the not_exists method to check if no elements
satisfy a given condition, which is the logical opposite of the exists method.
"""

from py_collections import Collection


def main():
    """Demonstrate various uses of the not_exists method."""
    print("=== py-collections not_exists() Method Examples ===\n")

    # Example 1: Basic usage without predicate
    print("1. Basic usage without predicate:")
    empty_collection = Collection([])
    non_empty_collection = Collection([1, 2, 3])

    print(f"   Empty collection: {empty_collection}")
    print(f"   not_exists(): {empty_collection.not_exists()}")

    print(f"   Non-empty collection: {non_empty_collection}")
    print(f"   not_exists(): {non_empty_collection.not_exists()}")
    print()

    # Example 2: Using with predicates
    print("2. Using with predicates:")
    numbers = Collection([1, 2, 3, 4, 5])
    print(f"   Numbers: {numbers}")

    # Check if no numbers are greater than 3
    no_large_numbers = numbers.not_exists(lambda x: x > 3)
    print(f"   No numbers > 3: {no_large_numbers}")

    # Check if no numbers are greater than 10
    no_very_large_numbers = numbers.not_exists(lambda x: x > 10)
    print(f"   No numbers > 10: {no_very_large_numbers}")
    print()

    # Example 3: Working with strings
    print("3. Working with strings:")
    words = Collection(["hello", "world", "python", "collections"])
    print(f"   Words: {words}")

    # Check if no words start with 'a'
    no_a_words = words.not_exists(lambda x: x.startswith("a"))
    print(f"   No words start with 'a': {no_a_words}")

    # Check if no words start with 'z'
    no_z_words = words.not_exists(lambda x: x.startswith("z"))
    print(f"   No words start with 'z': {no_z_words}")
    print()

    # Example 4: Working with objects
    print("4. Working with objects:")

    class Product:
        def __init__(self, name: str, price: float, in_stock: bool):
            self.name = name
            self.price = price
            self.in_stock = in_stock

        def __repr__(self):
            return f"Product(name='{self.name}', price={self.price}, in_stock={self.in_stock})"

    products = Collection(
        [
            Product("Laptop", 999.99, True),
            Product("Mouse", 29.99, False),
            Product("Keyboard", 79.99, True),
            Product("Monitor", 299.99, False),
        ]
    )

    print(f"   Products: {products}")

    # Check if no products are out of stock
    all_in_stock = products.not_exists(lambda p: not p.in_stock)
    print(f"   All products in stock: {all_in_stock}")

    # Check if no products are expensive (> $500)
    no_expensive_products = products.not_exists(lambda p: p.price > 500)
    print(f"   No expensive products (> $500): {no_expensive_products}")

    # Check if no products are cheap (< $20)
    no_cheap_products = products.not_exists(lambda p: p.price < 20)
    print(f"   No cheap products (< $20): {no_cheap_products}")
    print()

    # Example 5: Data validation scenarios
    print("5. Data validation scenarios:")

    # User data validation
    users = Collection(
        [
            {"name": "Alice", "email": "alice@example.com", "age": 25},
            {"name": "Bob", "email": "bob@example.com", "age": 30},
            {"name": "Charlie", "email": "charlie@example.com", "age": 35},
        ]
    )

    print(f"   Users: {users}")

    # Check if no users are under 18
    no_minors = users.not_exists(lambda u: u["age"] < 18)
    print(f"   No minors (age < 18): {no_minors}")

    # Check if no users have invalid emails
    no_invalid_emails = users.not_exists(lambda u: "@" not in u["email"])
    print(f"   No invalid emails: {no_invalid_emails}")

    # Check if no users have empty names
    no_empty_names = users.not_exists(lambda u: not u["name"].strip())
    print(f"   No empty names: {no_empty_names}")
    print()

    # Example 6: Comparison with exists method
    print("6. Comparison with exists method:")

    test_data = Collection([1, 2, 3, 4, 5])

    def predicate(x):
        return x > 3

    exists_result = test_data.exists(predicate)
    not_exists_result = test_data.not_exists(predicate)

    print(f"   Data: {test_data}")
    print("   Predicate: x > 3")
    print(f"   exists(): {exists_result}")
    print(f"   not_exists(): {not_exists_result}")
    print(f"   They are opposites: {exists_result == (not not_exists_result)}")
    print()

    # Example 7: Complex business logic
    print("7. Complex business logic:")

    orders = Collection(
        [
            {"id": 1, "status": "pending", "amount": 100.0, "customer_type": "premium"},
            {"id": 2, "status": "shipped", "amount": 250.0, "customer_type": "regular"},
            {
                "id": 3,
                "status": "delivered",
                "amount": 75.0,
                "customer_type": "premium",
            },
            {
                "id": 4,
                "status": "cancelled",
                "amount": 300.0,
                "customer_type": "regular",
            },
        ]
    )

    print(f"   Orders: {orders}")

    # Check if no orders are stuck in pending status for premium customers
    no_stuck_premium_orders = orders.not_exists(
        lambda o: o["status"] == "pending" and o["customer_type"] == "premium"
    )
    print(f"   No stuck premium orders: {no_stuck_premium_orders}")

    # Check if no high-value orders are cancelled
    no_cancelled_high_value = orders.not_exists(
        lambda o: o["status"] == "cancelled" and o["amount"] > 200
    )
    print(f"   No cancelled high-value orders (> $200): {no_cancelled_high_value}")

    # Check if no orders are in invalid states
    valid_statuses = {"pending", "shipped", "delivered", "cancelled"}
    no_invalid_statuses = orders.not_exists(lambda o: o["status"] not in valid_statuses)
    print(f"   No invalid order statuses: {no_invalid_statuses}")
    print()

    # Example 8: Edge cases
    print("8. Edge cases:")

    # Empty collection
    empty = Collection([])
    print(f"   Empty collection not_exists(): {empty.not_exists()}")
    print(
        f"   Empty collection not_exists(predicate): {empty.not_exists(lambda x: x > 0)}"
    )

    # Single element
    single = Collection([42])
    print(f"   Single element not_exists(): {single.not_exists()}")
    print(
        f"   Single element not_exists(lambda x: x == 42): {single.not_exists(lambda x: x == 42)}"
    )

    # Collection with None values
    with_none = Collection([1, None, 3, None])
    print(f"   Collection with None not_exists(): {with_none.not_exists()}")
    print(
        f"   Collection with None not_exists(lambda x: x is None): {with_none.not_exists(lambda x: x is None)}"
    )

    # Collection with duplicates
    duplicates = Collection([1, 1, 1, 1])
    print(
        f"   Collection with duplicates not_exists(lambda x: x == 1): {duplicates.not_exists(lambda x: x == 1)}"
    )
    print(
        f"   Collection with duplicates not_exists(lambda x: x == 2): {duplicates.not_exists(lambda x: x == 2)}"
    )
    print()

    print("=== End of Examples ===")


if __name__ == "__main__":
    main()
