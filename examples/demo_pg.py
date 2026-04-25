from securedal import TamperOperator

# Initialize the operator for PostgreSQL
op = TamperOperator(
    "postgresql",
    connection_string="postgresql://tamper_user:password@localhost:5432/tamper",
    table="opendal_storage"
)
"""
OpenDAL treats relational DBs as KV stores. So we write/read value to/from a key(PRIMARY KEY), not supporting complex queries.
"""
print("Support for writes with if_match: ", op.capability().write_with_if_match)

# Write data
op.write("test.txt", b"Hello World")

# Read data
content = op.read("test.txt")
print(content.decode())

# Get metadata
metadata = op.stat("test.txt")
print(f"Content length: {metadata}")