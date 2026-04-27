from securedal import TamperOperator

# Initialize the operator for PostgreSQL
op = TamperOperator(
    "postgresql",
    connection_string="postgresql://tamper_user:password@localhost:5432/tamper",
    table="sdk_store"
)
"""
OpenDAL treats relational DBs as KV stores. So we write/read value to/from a key(PRIMARY KEY), not supporting complex queries.
"""
print("Support for writes with if_match: ", op.capability().write_with_if_match)

# UNSUPPORTED
""" for key in op.list("/"):
    print(key) """

# UNSUPPORTED
""" op.remove_all("/") """

# Write data
op.write("test_pg1.txt", b"Hello World")

# Read data
content = op.read("test_pg1.txt")
print(content.decode())

# Get metadata
metadata = op.stat("test_pg1.txt")
print(f"Content length: {metadata}")