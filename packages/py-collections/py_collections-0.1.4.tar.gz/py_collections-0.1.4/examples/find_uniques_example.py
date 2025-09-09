#!/usr/bin/env python3
"""
Example demonstrating the find_uniques method in py-collections.

This example shows how to use the find_uniques method to identify
unique items in a collection using different comparison strategies.
"""

from py_collections import Collection


def main():
    """Demonstrate various uses of the find_uniques method."""
    print("=== py-collections find_uniques() Method Examples ===\n")

    # Example 1: Basic usage without arguments
    print("1. Basic usage without arguments (direct object comparison):")
    numbers = Collection([1, 2, 2, 3, 3, 3, 4])
    print(f"   Original: {numbers}")
    uniques = numbers.find_uniques()
    print(f"   Unique items: {uniques}")

    # With strings
    words = Collection(
        ["hello", "world", "hello", "python", "world", "collections", "unique"]
    )
    print(f"   Words: {words}")
    uniques = words.find_uniques()
    print(f"   Unique words: {uniques}")
    print()

    # Example 2: Using with string key
    print("2. Using with string key (finds unique items based on key values):")
    users = Collection(
        [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
            {
                "id": 1,
                "name": "Alice Smith",
                "email": "alice.smith@example.com",
            },  # Duplicate ID
            {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
            {
                "id": 2,
                "name": "Bob Johnson",
                "email": "bob.johnson@example.com",
            },  # Duplicate ID
            {"id": 4, "name": "David", "email": "david@example.com"},  # Unique ID
        ]
    )

    print(f"   Users: {users}")

    # Find unique items based on ID
    unique_ids = users.find_uniques("id")
    print(f"   Unique IDs: {unique_ids}")

    # Find unique items based on email domain
    unique_emails = users.find_uniques("email")
    print(f"   Unique emails: {unique_emails}")
    print()

    # Example 3: Using with object attributes
    print("3. Using with object attributes:")

    class Product:
        def __init__(self, name: str, sku: str, price: float):
            self.name = name
            self.sku = sku
            self.price = price

        def __repr__(self):
            return f"Product(name='{self.name}', sku='{self.sku}', price={self.price})"

    products = Collection(
        [
            Product("Laptop", "LAP001", 999.99),
            Product("Mouse", "MOU001", 29.99),
            Product("Laptop Pro", "LAP001", 1299.99),  # Duplicate SKU
            Product("Keyboard", "KEY001", 79.99),
            Product("Mouse Wireless", "MOU001", 39.99),  # Duplicate SKU
            Product("Monitor", "MON001", 299.99),  # Unique SKU
        ]
    )

    print(f"   Products: {products}")

    # Find unique items based on SKU
    unique_skus = products.find_uniques("sku")
    print(f"   Unique SKUs: {unique_skus}")
    print()

    # Example 4: Using with callback function
    print("4. Using with callback function:")

    orders = Collection(
        [
            {
                "order_id": "ORD001",
                "customer_id": 100,
                "amount": 150.0,
                "status": "completed",
            },
            {
                "order_id": "ORD002",
                "customer_id": 101,
                "amount": 200.0,
                "status": "pending",
            },
            {
                "order_id": "ORD003",
                "customer_id": 100,
                "amount": 75.0,
                "status": "completed",
            },
            {
                "order_id": "ORD004",
                "customer_id": 102,
                "amount": 300.0,
                "status": "completed",
            },
            {
                "order_id": "ORD005",
                "customer_id": 101,
                "amount": 125.0,
                "status": "completed",
            },
            {
                "order_id": "ORD006",
                "customer_id": 103,
                "amount": 400.0,
                "status": "pending",
            },  # Unique customer
        ]
    )

    print(f"   Orders: {orders}")

    # Find unique items based on customer_id
    unique_customers = orders.find_uniques(lambda order: order["customer_id"])
    print(f"   Unique customers: {unique_customers}")

    # Find unique items based on status
    unique_statuses = orders.find_uniques(lambda order: order["status"])
    print(f"   Unique statuses: {unique_statuses}")
    print()

    # Example 5: Complex business logic
    print("5. Complex business logic:")

    employees = Collection(
        [
            {
                "emp_id": 1,
                "name": "Alice",
                "department": "Engineering",
                "manager_id": 10,
            },
            {"emp_id": 2, "name": "Bob", "department": "Sales", "manager_id": 11},
            {
                "emp_id": 3,
                "name": "Charlie",
                "department": "Engineering",
                "manager_id": 10,
            },
            {"emp_id": 4, "name": "David", "department": "Marketing", "manager_id": 12},
            {"emp_id": 5, "name": "Eve", "department": "Engineering", "manager_id": 10},
            {"emp_id": 6, "name": "Frank", "department": "Sales", "manager_id": 11},
            {
                "emp_id": 7,
                "name": "Grace",
                "department": "HR",
                "manager_id": 13,
            },  # Unique department
        ]
    )

    print(f"   Employees: {employees}")

    # Find employees in unique departments
    unique_departments = employees.find_uniques(lambda emp: emp["department"])
    print(f"   Unique department employees: {unique_departments}")

    # Find employees with unique managers
    unique_managers = employees.find_uniques(lambda emp: emp["manager_id"])
    print(f"   Unique manager employees: {unique_managers}")
    print()

    # Example 6: Data validation scenarios
    print("6. Data validation scenarios:")

    # Check for unique email addresses
    user_data = Collection(
        [
            {"user_id": 1, "email": "alice@company.com", "username": "alice"},
            {"user_id": 2, "email": "bob@company.com", "username": "bob"},
            {
                "user_id": 3,
                "email": "alice@company.com",
                "username": "alice_smith",
            },  # Duplicate email
            {"user_id": 4, "email": "charlie@company.com", "username": "charlie"},
            {
                "user_id": 5,
                "email": "bob@company.com",
                "username": "bob_johnson",
            },  # Duplicate email
            {
                "user_id": 6,
                "email": "david@company.com",
                "username": "david",
            },  # Unique email
        ]
    )

    print(f"   User data: {user_data}")

    # Find unique emails
    unique_emails = user_data.find_uniques("email")
    print(f"   Unique emails: {unique_emails}")

    # Find unique usernames
    unique_usernames = user_data.find_uniques("username")
    print(f"   Unique usernames: {unique_usernames}")
    print()

    # Example 7: Edge cases
    print("7. Edge cases:")

    # Empty collection
    empty = Collection([])
    print(f"   Empty collection uniques: {empty.find_uniques()}")

    # All unique
    all_unique = Collection([1, 2, 3, 4, 5])
    print(f"   All unique collection: {all_unique.find_uniques()}")

    # All duplicates
    all_duplicates = Collection([1, 1, 1, 1])
    print(f"   All duplicates collection: {all_duplicates.find_uniques()}")

    # Single element
    single = Collection([42])
    print(f"   Single element collection: {single.find_uniques()}")

    # None values
    with_none = Collection([1, None, 2, None, 3])
    print(f"   Collection with None uniques: {with_none.find_uniques()}")
    print()

    # Example 8: Performance with larger datasets
    print("8. Performance with larger datasets:")

    # Create a larger dataset with some unique items
    large_data = [*list(range(100)), 50, 51, 52, 53, 54]  # Add some duplicates
    large_collection = Collection(large_data)

    print(f"   Large collection size: {len(large_collection)}")
    uniques = large_collection.find_uniques()
    print(f"   Found {len(uniques)} unique items")
    print(f"   First few unique items: {uniques.take(10)}")
    print()

    # Example 9: Working with nested data
    print("9. Working with nested data:")

    nested_data = Collection(
        [
            {"user": {"id": 1, "profile": {"email": "alice@example.com"}}},
            {"user": {"id": 2, "profile": {"email": "bob@example.com"}}},
            {
                "user": {"id": 1, "profile": {"email": "alice.smith@example.com"}}
            },  # Duplicate user ID
            {"user": {"id": 3, "profile": {"email": "charlie@example.com"}}},
            {
                "user": {"id": 4, "profile": {"email": "david@example.com"}}
            },  # Unique user ID
        ]
    )

    print(f"   Nested data: {nested_data}")

    # Find unique items based on nested user ID
    unique_user_ids = nested_data.find_uniques(lambda x: x["user"]["id"])
    print(f"   Unique user IDs: {unique_user_ids}")

    # Find unique items based on email domain
    unique_domains = nested_data.find_uniques(
        lambda x: x["user"]["profile"]["email"].split("@")[1]
    )
    print(f"   Unique email domains: {unique_domains}")
    print()

    # Example 10: Comparison with find_duplicates
    print("10. Comparison with find_duplicates:")

    test_data = Collection([1, 2, 2, 3, 3, 3, 4, 5])
    print(f"   Test data: {test_data}")

    uniques = test_data.find_uniques()
    duplicates = test_data.find_duplicates()

    print(f"   Unique items: {uniques}")
    print(f"   Duplicate items: {duplicates}")

    # Show that uniques + duplicates = original (in terms of counts)
    print(f"   Unique count: {len(uniques)}")
    print(f"   Duplicate count: {len(duplicates)}")
    print(f"   Total unique + duplicate items: {len(uniques) + len(duplicates)}")
    print(f"   Original count: {len(test_data)}")
    print()

    # Example 11: Error handling
    print("11. Error handling:")

    # Missing key
    try:
        users.find_uniques("missing_key")
    except KeyError as e:
        print(f"   Missing key error: {e}")

    # Missing attribute
    try:
        products.find_uniques("missing_attribute")
    except AttributeError as e:
        print(f"   Missing attribute error: {e}")

    # Invalid argument type
    try:
        numbers.find_uniques(123)
    except TypeError as e:
        print(f"   Invalid argument type error: {e}")
    print()

    print("=== End of Examples ===")


if __name__ == "__main__":
    main()
