from securedal import TamperOperator
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize the operator for the S3 (Wasabi)
op = TamperOperator(
    scheme="s3",
    bucket="bench-storage",
    endpoint="https://s3.eu-west-1.wasabisys.com",
    access_key_id=os.getenv('ACCESS_KEY'),
    secret_access_key=os.getenv('SECRET_KEY'),
    region="eu-west-1",
)
print("Support for writes with append: ", op.capability().write_can_append)

""" for object in op.list("/"):
    print(object) """

# Write data to an object
op.write("test_s3_wasabi_2.txt", b"Hello World!")

# Read data from the object
content = op.read("test_s3_wasabi_2.txt")
print(content.decode())

# Get metadata
metadata = op.stat("test_s3_wasabi_2.txt")
print(f"Content length: {metadata}")

# WRemove all data
op.remove_all("/")

# Read data from the object
content = op.read("test_s3_wasabi_2.txt")
print(content.decode())
