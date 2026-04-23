from src.tamper_operator import TamperOperator
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize the operator for the local filesystem
op = TamperOperator(
    scheme="fs", 
    mapping_path="./storage/mapping/tamper_mapping.db",
    pinata_token=os.getenv('JWT'),
    root="./storage"
)

print("Support for writes with append: ", op.capability().write_can_append)

""" for file in op.list("/"):
    print(file) """

# Write data to a file
op.write("test_pinning9.txt", b"Hello World!")

# Read data from the file
content = op.read("test_pinning9.txt")
print(content.decode())

# Get metadata
metadata = op.stat("test_pinning9.txt")
print(f"Content length: {metadata}")


# -- APPEND ------------------------------------
# Append data to a file
op.write("test_pinning9.txt", b"Hello World!", append=True)

# Read data from the file
content = op.read("test_pinning9.txt")
print(content.decode())

# Get metadata
metadata = op.stat("test_pinning9.txt")
print(f"Content length: {metadata}")


# -- DELETE ------------------------------------
""" # Delete a file
op.delete("test_pinning9.txt")

# Read data from the file - should raise exception
content = op.read("test_pinning9.txt")
print(content.decode()) """

# -- READ ALL ----------------------------------
# Populate
op.write("/test_readall/test_readall_1.txt", b"Hello World1!")
op.write("/test_readall/test_readall_2.txt", b"Hello World2!")
op.write("/test_readall/test_readall_3.txt", b"Hello World3!")
op.write("/test_readall/test_readall_4.txt", b"Hello World4!")
op.write("/test_readall/test_readall_5.txt", b"Hello World5!")
op.write("/test_readall/test_readall_6.txt", b"Hello World6!")
op.write("/test_readall/test_readall_7.txt", b"Hello World7!")
op.write("/test_readall/test_readall_8.txt", b"Hello World8!")
op.write("/test_readall/test_readall_9.txt", b"Hello World9!")
op.write("/test_readall/test_readall_10.txt", b"Hello World10!")

# Read (and verify) all files
content = op.read_all("/test_readall/")
print(content)

# Tamper with file (bypass write through openDAL)
op.operator.write("test_readall/test_readall_10.txt", b"Hello World10! <- TAMPERED")

# Read (and verify) all files
try:
    content = op.read_all("test_readall/")
except Exception as e:
    print(e.results) # Still print the successful results
    raise

