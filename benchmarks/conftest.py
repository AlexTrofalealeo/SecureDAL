# benchmarks/conftest.py
import os
import pytest
import random
import opendal
from securedal import TamperOperator

# -- Global config  --

random.seed(42)

TEST_CASE = [
    ("4kb",   4_096),
    ("64kb",  65_536),
    ("1mb",   1_048_576),
    ("16mb",  16_777_216),
]

N_FILES  = 100
N_ROUNDS = 10000
N_WARMUP = 10

# -- Backend definitions ------------------------------------

BACKENDS = {
    "fs": {
        "scheme": "fs",
        "baseline": {"root": "./benchmarks/bench_storage/baseline"},
        "sdk":      {"root": "./benchmarks/bench_storage/sdk"},
    },
    "s3": {
        "scheme": "s3",
        "baseline": {
            "bucket":            "bench-baseline",
            "endpoint":          "http://localhost:9000",
            "access_key_id":     "minioadmin",
            "secret_access_key": "minioadmin",
            "region":            "us-east-1",
        },
        "sdk": {
            "bucket":            "bench-sdk",
            "endpoint":          "http://localhost:9000",
            "access_key_id":     "minioadmin",
            "secret_access_key": "minioadmin",
            "region":            "us-east-1",
        },
    },
    "postgresql": {
        "scheme": "postgresql",
        "baseline": {
            "connection_string": "postgresql://tamper_user:password@localhost:5432/tamper",
            "table":             "baseline_store",
        },
        "sdk": {
            "connection_string": "postgresql://tamper_user:password@localhost:5432/tamper",
            "table":             "sdk_store",
        },
    },
    "redis": {
        "scheme": "redis",
        "baseline": {
            "endpoint": "redis://localhost:6379",
            "db":        "0",
        },
        "sdk": {
            "endpoint": "redis://localhost:6379",
            "db":        "1",
        },
    },
}

MAPPING_PATH="./benchmarks/bench_storage/bench_mapping.db"

# -- CLI option ---------------------------------------------

def pytest_addoption(parser):
    parser.addoption(
        "--backend",
        action="store",
        default="fs",
        choices=list(BACKENDS.keys()),
        help="Storage backend to benchmark (fs, s3, postgresql, redis)",
    )

    parser.addoption(
        "--n-rounds",
        action="store",
        default=N_ROUNDS,
        type=int,
        help="Number of benchmark rounds per test",
    )

@pytest.fixture(scope="session")
def backend(request):
    name = request.config.getoption("--backend")
    return BACKENDS[name]

@pytest.fixture(scope="session")
def n_rounds(request):
    return request.config.getoption("--n-rounds")


# -- Fixtures -----------------------------------------------

@pytest.fixture(scope="module")
def baseline_op(backend):
    """Plain OpenDAL."""
    return opendal.Operator(backend["scheme"], **backend["baseline"])

@pytest.fixture(scope="module")
def tamper_op_local(backend):
    """Full SDK with local Kubo node."""
    return TamperOperator(
        scheme=backend["scheme"],
        mapping_path=MAPPING_PATH,
        **backend["sdk"]
    )


# -- Content pools --------------------------------------------

@pytest.fixture(scope="module")
def key_pool(n_rounds):
    pool = {}
    for name, _ in TEST_CASE:
        pool[name] = [f"bench_{name}_{i}.bin" for i in range(n_rounds + N_WARMUP)]
    return pool

@pytest.fixture(scope="module")
def data_pool():
    pool = {}
    for name, size in TEST_CASE:
        pool[name] = [os.urandom(size) for _ in range(N_FILES)]
    return pool


# -- Cleaners -----------------------------------------------

def _clean_sqlite():
    import sqlite3
    if os.path.exists(MAPPING_PATH):
        conn = sqlite3.connect(MAPPING_PATH)
        conn.execute("DELETE FROM mapping")
        conn.commit()
        conn.close()

@pytest.fixture(scope="module")
def clean(baseline_op, tamper_op_local):
    baseline_op.remove_all("/")
    tamper_op_local.operator.remove_all("/")
    _clean_sqlite()
    yield