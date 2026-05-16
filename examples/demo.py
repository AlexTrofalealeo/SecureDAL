from securedal import TamperOperator
from opendal.exceptions import NotFound
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize the operator for the local filesystem
op = TamperOperator(
    scheme="fs", 
    mapping_path="./storage/mapping/tamper_mapping.db",
    #pinata_token=os.getenv('JWT'),
    root="./storage"
)

print("Support for writes with append: ", op.capability().write_can_append)

""" for file in op.list("/"):
    print(file) """

# Write data to a file
op.write("test_paths/test_paths1.txt", b"Hello World!")

# Read data from the file
content = op.read("test_paths/test_paths1.txt")
print("\n----NORMAL READ:\n", content.decode())

# Get metadata
metadata = op.stat("test_paths/test_paths1.txt")
print(f"Content length: {metadata}")


# -- APPEND ------------------------------------
# Append data to a file
op.write("test_paths/test_paths1.txt", b"Hello World!", append=True)

# Read data from the file
content = op.read("test_paths/test_paths1.txt")
print("\n----APPENDED READ:\n", content.decode())

# Get metadata
metadata = op.stat("test_paths/test_paths1.txt")
print(f"Content length: {metadata}")


# -- TEST PATHS ---------------------------------
# Initialize the operator for the local filesystem with another root
op2 = TamperOperator(
    scheme="fs", 
    mapping_path="./storage/mapping/tamper_mapping.db",
    root="storage/test_paths/"
)

# Read data from the file
content = op2.read("test_paths1.txt")
print("\n----TEST PATHS READ:\n", content.decode())

# Get metadata
metadata = op2.stat("test_paths1.txt")
print(f"Content length: {metadata}")


# -- DELETE ------------------------------------
# Delete a file
op.delete("test_paths/test_paths1.txt")
content=b""

# Read data from the file - should raise exception
try:
    content = op.read("test_paths/test_paths1.txt")
except NotFound as e:
    print(e)
print("\n----DELETED READ:\n", content.decode())

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
print("\n----NORMAL READALL:\n", content)

# Tamper with file (bypass write through openDAL)
op._operator.write("test_readall/test_readall_10.txt", b"Hello World10! <- TAMPERED")

# Read (and verify) all files
try:
    content = op.read_all("test_readall/")
except Exception as e:
    print("\n----TAMPERED READALL:\n", e.results) # Still print the successful results
    print(e)
    # raise

# Initialize the operator for the local filesystem with another root
op3 = TamperOperator(
    scheme="fs", 
    mapping_path="./storage/mapping/tamper_mapping.db",
    root="storage\\test_readall\\"
)

# Read (and verify) all files
try:
    content = op3.read_all("/")
except Exception as e:
    print("\n----TEST PATHS READALL:\n", e.results) # Still print the successful results
    print(e)
    # raise

op3.remove_all("/")