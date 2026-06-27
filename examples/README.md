# SecureDAL Examples

This directory contains example usages of SecureDAL, demonstrating its use under different backends and functionalities.

SecureDAL is designed to provide an identical interface to OpenDAL, not necessarily requiring any changes to any application code using OpenDAL. 
An example from the [OpenDAL Python Binding documentation](https://opendal.apache.org/docs/bindings/python/connecting/) is provided below.

```python
import opendal

op = opendal.Operator("fs", root="/tmp/opendal")
```

The exact same code can be used with SecureDAL, simply by adapting to the correct SecureDAL naming. The example below demonstrates this.

```python
import securedal

op = securedal.TamperOperator("fs", root="/tmp/opendal")
```

This is because the SecureDAL `TamperOperator` default argument values allows for a seamless transition from OpenDAL to SecureDAL, without requiring any changes to the application code.
However, for more advanced customization, the `TamperOperator` constructor allows for the specification of a `mapping_path` and `eis_address`, usage of the Pinata service for remote IPFS pinning through the `pinata_token` argument, and the use of a custom `EISLayer` and `MappingLayer`, which can be used to adapt SecureDAL to different integrity-related backends.

```python
import securedal
import os
from dotenv import load_dotenv
load_dotenv()

op = securedal.TamperOperator(
    scheme="fs", 
    root="./storage",
    eis_address = "/ip4/127.0.0.1/tcp/5001",
    mapping_path= "./storage/mapping/tamper_mapping.db",
    pinata_token=os.getenv('JWT'),
    eis = None,        # optional custom EIS layer
    mapping = None,    # optional custom mapping
)
```

Note that to use the Pinata service, you must generate an [API Key](https://app.pinata.cloud/developers/api-keys) from your Pinata account and save the `JWT (secret access token)`. It is highly recommended to store this token in a `.env` file as:

```
JWT=your_pinata_jwt_token_here
```

Then you can use the normal SecureDAL `TamperOperator` functions as you would with OpenDAL:

```python
# Write data to a file
op.write("test_paths/test_paths1.txt", b"Hello World!")

# Read data from the file
content = op.read("test_paths/test_paths1.txt")
```

However, it is highly recommended the use of `try-except` blocks to catch any exceptions that may arise especially from read operations. SecureDAL raises exceptions to report operation failures (actually the same behavior as OpenDAL), but with the addition of new exceptions to report tampering detection and integrity verification failures. The following example demonstrates this:

```python
try:
    content = op.read("test_paths/test_paths1.txt")
except securedal.exceptions.TamperDetectedException:
    print("Tampering detected!")
except securedal.exceptions.MissingAnchorException:
    print("Missing anchor!")
except securedal.exceptions.MissingDataException:
    print("Missing data!")
except securedal.exceptions.UntrackedObjectException:
    print("Untracked object!")
except securedal.exceptions.OrphanMappingException:
    print("Orphan mapping!")
```

This allows you to handle tampering detection gracefully, without crashing the application, while letting you deal with the exceptions the way you see fit. The `read_all()` function can also be used to read multiple objects at once, and it will raise a `BulkTamperException` if any of the objects have been tampered with. The following example demonstrates this:

```python
# Read (and verify) all files
try:
    content = op.read_all("test_readall/")
except securedal.exceptions.BulkTamperException as e:
    print("----TAMPERED READALL----"), 
    print(e.results) # Still print the successful results
    print(e.violations) # Print the tampered objects
```

Some other SecureDAL `TamperOperator` functions also perform integrity verification, and because of this, they may also raise exceptions if tampering is detected and therefore should also be used with `try-except` blocks.

```python
# Append data to a file (verifies the integrity of the file before appending)
try:
    op.write("test_paths/test_paths1.txt", b"Hello World!", append=True)
except securedal.exceptions.TamperException as e:
    print("Tampering detected!", e)

# Copy a file (verifies the integrity of the source file before copying)
try:
    op.copy("test_paths/test_paths1.txt", "test_paths/test_paths2.txt")
except securedal.exceptions.TamperException as e:
    print("Tampering detected!", e)

# Rename a file (verifies the integrity of the source file before renaming)
try:
    op.rename("test_paths/test_paths1.txt", "test_paths/test_paths3.txt")
except securedal.exceptions.TamperException as e:
    print("Tampering detected!", e)
```

Here's a complete table of the SecureDAL `TamperOperator` supported functions and whether they perform integrity verification or not:

| Function | Description | Has Verification? | Possible Tampering Exceptions |
|----------|-------------|------------------|--------------------|
| `read` | Read data from a single file | Yes | `TamperDetectedException`, `MissingAnchorException`, `MissingDataException`, `UntrackedObjectException`, `OrphanMappingException` |
| `read_all` | Read data from multiple files (unique to SecureDAL) | Yes | `BulkTamperException` |
| `write (no append)` | Write data to a file (overwrites if exists) | No | None |
| `write (append)` | Append data to a file | Yes | `TamperDetectedException`, `MissingAnchorException`, `MissingDataException`, `UntrackedObjectException`, `OrphanMappingException` |
| `copy` | Copy a file | Yes | `TamperDetectedException`, `MissingAnchorException`, `MissingDataException`, `UntrackedObjectException`, `OrphanMappingException` |
| `rename` | Rename a file | Yes | `TamperDetectedException`, `MissingAnchorException`, `MissingDataException`, `UntrackedObjectException`, `OrphanMappingException` |
| `delete` | Delete a single file | No | None |
| `remove_all` | Delete multiple files | No | None |
| `list` | List files in a directory (no modification: pass-through to OpenDAL) | No | None |
| `stat` | Get file metadata (no modification: pass-through to OpenDAL) | No | None |
| `layer` | Add new layers upon the current operator (no modification: pass-through to OpenDAL) | No | None |
| `open` | Open a file for reading or writing (**Unsupported by SecureDAL**) | No | None |
| `create_dir` | Create a directory (no modification: pass-through to OpenDAL) | No | None |
| `exists` | Check if a file exists (no modification: pass-through to OpenDAL) | No | None |
| `capabilty` | Check if a capability is supported (no modification: pass-through to OpenDAL) | No | None |
| `to_async_operator` | Convert to an async operator (**Unsupported by SecureDAL**) | No | None |

You can find more examples in this directory, running them for example with:

```bash
uv run python examples/demo.py # From the root of the repository
```