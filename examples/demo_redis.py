from src.tamper_operator import TamperOperator

# Initialize the operator for Redis
op = TamperOperator(
    scheme="redis",
    endpoint="redis://localhost:6379",
    db="1",
)
print("Support for writes with append: ", op.capability().write_can_append)

""" for key in op.list("/"):
    print(key) """

# Write data to a key
op.write("test_redis_1.txt", b"Hello World!")

# Read data from the key
content = op.read("test_redis_1.txt")
print(content.decode())

# Get metadata
metadata = op.stat("test_redis_1.txt")
print(f"Content length: {metadata}")
