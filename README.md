# SecureDAL

### Install `uv`

```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
For more information check [uv website](https://docs.astral.sh/uv/getting-started/installation/).

### Install project package

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


### Run benchmark script

```bash
./benchmarks/run_benchmarks.sh
```

Or with `uv`:

```bash
uv run ./benchmarks/run_benchmarks.sh
```
