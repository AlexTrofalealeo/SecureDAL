from securedal import TamperOperator

# Initialize the operator for Redis
op = TamperOperator(
    scheme="redis",
    endpoint="redis://localhost:6379",
    db="1",
)
print("Support for writes with append: ", op.capability().write_can_append)

# UNSUPPORTED
""" for key in op.list("/"):
    print(key) """

# UNSUPPORTED
""" op.remove_all("/") """


# Write data to a key
op.write("test_redis_4.txt", b"0"*16_777_216)

# Read data from the key
content = op.read("test_redis_4.txt")
print(content.decode()[:16])

# Get metadata
metadata = op.stat("test_redis_4.txt")
print(f"Content length: {metadata}")
