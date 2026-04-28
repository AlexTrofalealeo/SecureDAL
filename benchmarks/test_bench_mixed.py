# benchmarks/test_bench_mixed.py
import pytest
from benchmarks.conftest import TEST_CASE, N_WARMUP, RNG_SEED
from random import Random

# -- Baseline benchmarks ------------------------------------

@pytest.mark.parametrize("name,size", TEST_CASE)
@pytest.mark.usefixtures("clean_before", "clean_after", "clean_baseline")
def test_baseline_mixed(benchmark, baseline_op, name, size, key_pool, data_pool, n_rounds):
    rng = Random(RNG_SEED)
    key_iter = iter(key_pool[name])

    def workload():
        key = f"mixed_{next(key_iter)}"
        data = rng.choice(data_pool[name])
        baseline_op.write(key, data)
        baseline_op.read(key)

    benchmark.pedantic(
        workload,
        rounds=n_rounds,
        warmup_rounds=N_WARMUP,
    )

# -- SDK benchmarks -----------------------------------------

@pytest.mark.parametrize("name,size", TEST_CASE)
@pytest.mark.usefixtures("clean_before", "clean_after")
def test_sdk_mixed(benchmark, tamper_op_local, name, size, key_pool, data_pool, n_rounds):
    rng = Random(RNG_SEED)
    key_iter = iter(key_pool[name])

    def workload():
        key = f"mixed_sdk_{next(key_iter)}"
        data = rng.choice(data_pool[name])
        tamper_op_local.write(key, data)
        tamper_op_local.read(key)

    benchmark.pedantic(
        workload,
        rounds=n_rounds,
        warmup_rounds=N_WARMUP,
    )