# SecureDAL Instructions

This document provides instructions for setting up the SecureDAL environment and installing dependencies on your machine.

### Install `uv`

```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
For more information check [uv website](https://docs.astral.sh/uv/getting-started/installation/).

### Install project package

Clone the repository and navigate to the project directory:

```bash
# Install package
pip install .

# Install with dev dependencies
pip install ".[dev]"
```

Or through `uv`:

```bash
# Install package
uv sync

# Install with dev dependencies
uv sync --extra dev
```

### Deploy local IPFS node:

To install IPFS Kubo check the [IPFS Kubo installation guide](https://docs.ipfs.tech/install/command-line/).

Or set up a local IPFS node using Docker Compose:
```bash
# From the repository root directory
docker compose up -d ipfs
```

For more information check [IPFS documentation](https://docs.ipfs.tech/install/).