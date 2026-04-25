from securedal import TamperOperator

# Initialize the operator for the local S3 (Minio)
op = TamperOperator(
    scheme="s3",
    bucket="test-bucket",
    endpoint="http://localhost:9000",
    access_key_id="minioadmin",
    secret_access_key="minioadmin",
    region="us-east-1",
)
print("Support for writes with append: ", op.capability().write_can_append)

""" for object in op.list("/"):
    print(object) """

# Write data to an object
op.write("test_s3_1.txt", b"Hello World!")

# Read data from the object
content = op.read("test_s3_1.txt")
print(content.decode())

# Get metadata
metadata = op.stat("test_s3_1.txt")
print(f"Content length: {metadata}")
