from src.tamper_operator import TamperOperator

# Initialize the operator for IPFS
op = TamperOperator(
    "ipfs",
    endpoint="http://127.0.0.1:8080",
    root="/ipfs/"
)

cid="Qmf7rUYeb4tBeW3XkXrjDL6ktpEQmvAFrxgJQxMUGKosx6"
# Read data from the file
content = op.operator.read(cid)
print(content)

# Get metadata
metadata = op.stat(cid)
print(f"Content length: {metadata}")