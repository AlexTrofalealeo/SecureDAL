# benchmarks/conftest.py
import os
from random import Random
import pytest
import opendal
from securedal import TamperOperator
from dotenv import load_dotenv
load_dotenv()

# -- Global config  --

RNG_SEED = 42

TEST_CASE = [
    ("4kb",   4_096),
    ("64kb",  65_536),
    ("1mb",   1_048_576),
    ("16mb",  16_777_216),
]

N_FILES  = 500
N_ROUNDS = 10000
N_WARMUP = 10

# -- Backend definitions ------------------------------------

BACKENDS = {
    "fs": {
        "scheme": "fs",
        "kwargs": {"root": "./benchmarks/bench_storage"},
    },
    "s3": {
        "scheme": "s3",
        "kwargs": {
            "bucket":            "bench-storage",
            "endpoint":          "http://localhost:9000",
            "access_key_id":     "minioadmin",
            "secret_access_key": "minioadmin",
            "region":            "us-east-1",
        },
    },
    "postgresql": {
        "scheme": "postgresql",
        "kwargs": {
            "connection_string": "postgresql://tamper_user:password@localhost:5432/tamper",
            "table":             "bench_storage",
        },
    },
    "redis": {
        "scheme": "redis",
        "kwargs": {
            "endpoint": "redis://localhost:6379",
            "db":        "0",
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


# -- Config --------------------------------------------------

def pytest_collection_modifyitems(config, items):
    order = {
        "test_baseline_write": 0,
        "test_sdk_write": 1,
        "test_baseline_read": 2,
        "test_sdk_read": 3,
        "test_baseline_mixed": 4,
        "test_sdk_mixed": 5,
    }

    def get_key(item):
        for key in order:
            if key in item.nodeid:
                return order[key]
        return 999  # anything unknown goes last

    items.sort(key=get_key)

# -- Fixtures -----------------------------------------------

@pytest.fixture(scope="module")
def baseline_op(backend):
    """Plain OpenDAL."""
    return opendal.Operator(backend["scheme"], **backend["kwargs"])

@pytest.fixture(scope="module")
def tamper_op_local(backend):
    """Full SDK with local Kubo node."""
    return TamperOperator(
        scheme=backend["scheme"],
        mapping_path=MAPPING_PATH,
        **backend["kwargs"]
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
    rng = Random(RNG_SEED)
    pool = {}
    for name, size in TEST_CASE:
        pool[name] = [rng.randbytes(size) for _ in range(N_FILES)]
    return pool

@pytest.fixture(scope="module")
def dataset(backend, tamper_op_local, key_pool, data_pool):
    if backend["scheme"] == "redis":
        _clean_redis()

        keys = {}
        for s in TEST_CASE:
            (name, size) = s
            keys[name] = []
            for i in range(N_FILES):
                key = f"read_bench_{name}_{i}.bin"
                tamper_op_local.write(f"sdk_{key}", data_pool[name][i])
                keys[name].append(key)

        return keys
    else:
        return key_pool


# -- Cleaners -----------------------------------------------

def _clean_redis():
    import redis
    r = redis.Redis.from_url(BACKENDS["redis"]["kwargs"]["endpoint"])
    r.flushall(asynchronous=False)

def _clean_postgresql():
    import psycopg2
    conn = psycopg2.connect(BACKENDS["postgresql"]["kwargs"]["connection_string"])
    cur = conn.cursor()
    cur.execute(f"TRUNCATE TABLE {BACKENDS['postgresql']['kwargs']['table']};")
    conn.commit()
    conn.close()

def _clean_sqlite():
    import sqlite3
    if os.path.exists(MAPPING_PATH):
        conn = sqlite3.connect(MAPPING_PATH)
        conn.execute("DELETE FROM mapping")
        conn.commit()
        conn.close()

def _clean(backend, baseline_op=None, tamper_op_local=None):
    if backend["scheme"] == "redis":
        _clean_redis()
    elif backend["scheme"] == "postgresql":
        _clean_postgresql()
    else:
        if baseline_op:
            baseline_op.remove_all("/") 
        if tamper_op_local:
            tamper_op_local._operator.remove_all("/")
    if tamper_op_local:
        _clean_sqlite()

@pytest.fixture(scope="module")
def clean_before(backend, baseline_op, tamper_op_local):
    print("\n  --- CLEANING BACKEND... ---")
    _clean(backend, baseline_op, tamper_op_local)
    print("  --- BACKEND CLEANED! ---")
    yield

@pytest.fixture(scope="module")
def clean_after(backend, baseline_op, tamper_op_local):
    yield
    print("\n  --- CLEANING BACKEND... ---")
    _clean(backend, baseline_op, tamper_op_local)
    print("  --- BACKEND CLEANED! ---")

@pytest.fixture(scope="function")
def clean_baseline(backend, baseline_op):
    yield
    print("|-", end="")
    _clean(backend, baseline_op=baseline_op)
    print("|", end="")

@pytest.fixture(scope="function")
def clean_sdk(backend, tamper_op_local):
    yield
    print("|-", end="")
    _clean(backend, tamper_op_local=tamper_op_local)
    print("|", end="")