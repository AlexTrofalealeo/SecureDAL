# benchmarks/test_bench_read.py
import pytest
from benchmarks.conftest import TEST_CASE, N_WARMUP, N_FILES, RNG_SEED
from random import Random

# -- Helpers -----------------------------------------------

def random_read(op, files, rng):
    f = rng.choice(files)
    return op.read(f"sdk_{f}")

# -- Baseline benchmarks ------------------------------------

@pytest.mark.parametrize("name,size", TEST_CASE)
def test_baseline_read(benchmark, baseline_op, name, size, n_rounds, dataset):
    rng = Random(RNG_SEED)
    keys = dataset[name]

    #benchmark.group = f"read-{name}"
    #benchmark.extra_info["impl"] = "baseline"
    benchmark.pedantic(
        random_read, 
        args=(baseline_op, keys, rng), 
        rounds=n_rounds,
        warmup_rounds=N_WARMUP,
    )

# -- SDK benchmarks -----------------------------------------

@pytest.mark.parametrize("name,size", TEST_CASE)
def test_sdk_read(benchmark, tamper_op_local, name, size, n_rounds, dataset):
    rng = Random(RNG_SEED)
    keys = dataset[name]

    #benchmark.group = f"read-{name}"
    #benchmark.extra_info["impl"] = "sdk"
    benchmark.pedantic(
        random_read, 
        args=(tamper_op_local, keys, rng), 
        rounds=n_rounds,
        warmup_rounds=N_WARMUP,
    )