#!/usr/bin/env python3
"""
Example demonstrating the sum method in py-collections.

This example shows how to use the sum method with different arguments,
inspired by Laravel's collection sum method.
"""

from py_collections import Collection


def main():
    """Demonstrate various uses of the sum method."""
    print("=== py-collections sum() Method Examples ===\n")

    # Example 1: Sum without arguments - sums all numeric values
    print("1. Sum without arguments (sums all numeric values):")
    numbers = Collection([1, 2, 3, 4, 5])
    print(f"   Collection: {numbers}")
    print(f"   Sum: {numbers.sum()}")

    # With mixed types (non-numeric values are ignored)
    mixed = Collection([1, 2, "hello", 3, "world", 4.5])
    print(f"   Mixed collection: {mixed}")
    print(f"   Sum (ignoring non-numeric): {mixed.sum()}")
    print()

    # Example 2: Sum with a key - sums values of that key
    print("2. Sum with a key (sums values of that key):")
    products = Collection(
        [
            {"name": "Laptop", "price": 999.99, "category": "Electronics"},
            {"name": "Mouse", "price": 29.99, "category": "Electronics"},
            {"name": "Keyboard", "price": 79.99, "category": "Electronics"},
            {"name": "Book", "price": 19.99, "category": "Books"},
        ]
    )
    print(f"   Products: {products}")
    print(f"   Sum of prices: {products.sum('price')}")
    print()

    # Example 3: Sum with object attributes
    print("3. Sum with object attributes:")

    class Product:
        def __init__(self, name: str, price: float, quantity: int):
            self.name = name
            self.price = price
            self.quantity = quantity

        def __repr__(self):
            return f"Product(name='{self.name}', price={self.price}, quantity={self.quantity})"

    product_objects = Collection(
        [
            Product("Widget A", 10.50, 5),
            Product("Widget B", 15.75, 3),
            Product("Widget C", 8.25, 8),
        ]
    )
    print(f"   Product objects: {product_objects}")
    print(f"   Sum of prices: {product_objects.sum('price')}")
    print(f"   Sum of quantities: {product_objects.sum('quantity')}")
    print()

    # Example 4: Sum with a callback function
    print("4. Sum with a callback function:")

    # Calculate total value (price * quantity)
    total_value = product_objects.sum(lambda p: p.price * p.quantity)
    print(f"   Total value (price * quantity): {total_value}")

    # Calculate total with tax
    orders = Collection(
        [
            {"subtotal": 100, "tax_rate": 0.08},
            {"subtotal": 200, "tax_rate": 0.10},
            {"subtotal": 150, "tax_rate": 0.09},
        ]
    )
    print(f"   Orders: {orders}")
    total_with_tax = orders.sum(
        lambda order: order["subtotal"] * (1 + order["tax_rate"])
    )
    print(f"   Total with tax: {total_with_tax}")
    print()

    # Example 5: Complex business logic
    print("5. Complex business logic example:")

    sales_data = Collection(
        [
            {
                "product": "Laptop",
                "units_sold": 10,
                "unit_price": 999.99,
                "commission_rate": 0.05,
            },
            {
                "product": "Mouse",
                "units_sold": 50,
                "unit_price": 29.99,
                "commission_rate": 0.03,
            },
            {
                "product": "Keyboard",
                "units_sold": 25,
                "unit_price": 79.99,
                "commission_rate": 0.04,
            },
        ]
    )

    # Calculate total revenue
    total_revenue = sales_data.sum(lambda sale: sale["units_sold"] * sale["unit_price"])
    print(f"   Sales data: {sales_data}")
    print(f"   Total revenue: ${total_revenue:.2f}")

    # Calculate total commission
    total_commission = sales_data.sum(
        lambda sale: sale["units_sold"] * sale["unit_price"] * sale["commission_rate"]
    )
    print(f"   Total commission: ${total_commission:.2f}")
    print()

    # Example 6: Error handling
    print("6. Error handling examples:")

    # Empty collection
    empty = Collection([])
    try:
        empty.sum()
    except ValueError as e:
        print(f"   Empty collection sum(): {e}")

    # Collection with no numeric values
    strings_only = Collection(["hello", "world", "test"])
    try:
        strings_only.sum()
    except ValueError as e:
        print(f"   Non-numeric collection sum(): {e}")

    # Missing key
    try:
        products.sum("missing_key")
    except KeyError as e:
        print(f"   Missing key sum(): {e}")

    # Non-numeric value for key
    bad_data = Collection([{"price": 10}, {"price": "invalid"}])
    try:
        bad_data.sum("price")
    except TypeError as e:
        print(f"   Non-numeric key value sum(): {e}")
    print()

    # Example 7: Performance and edge cases
    print("7. Edge cases:")

    # Large numbers
    large_numbers = Collection([1e6, 2e6, 3e6])
    print(f"   Large numbers sum: {large_numbers.sum()}")

    # Negative numbers
    negatives = Collection([-10, -20, -30])
    print(f"   Negative numbers sum: {negatives.sum()}")

    # Mixed positive and negative
    mixed_signs = Collection([10, -5, 20, -15])
    print(f"   Mixed signs sum: {mixed_signs.sum()}")

    # Zero values
    zeros = Collection([0, 0, 0])
    print(f"   Zero values sum: {zeros.sum()}")
    print()

    print("=== End of Examples ===")


if __name__ == "__main__":
    main()
