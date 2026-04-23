# benchmarks/test_bench_mixed.py
import random
import pytest
from benchmarks.conftest import TEST_CASE, N_WARMUP

# -- Baseline benchmarks ------------------------------------

@pytest.mark.parametrize("name,size", TEST_CASE)
def test_baseline_mixed(benchmark, clean, baseline_op, name, size, key_pool, data_pool, n_rounds):
    key_iter = iter(key_pool[name])

    def workload():
        key = f"mixed_{next(key_iter)}"
        data = random.choice(data_pool[name])
        baseline_op.write(key, data)
        baseline_op.read(key)

    benchmark.pedantic(
        workload,
        rounds=n_rounds,
        warmup_rounds=N_WARMUP,
    )

# -- SDK benchmarks -----------------------------------------

@pytest.mark.parametrize("name,size", TEST_CASE)
def test_sdk_mixed(benchmark, clean, tamper_op_local, name, size, key_pool, data_pool, n_rounds):
    key_iter = iter(key_pool[name])

    def workload():
        key = f"mixed_{next(key_iter)}"
        data = random.choice(data_pool[name])
        tamper_op_local.write(key, data)
        tamper_op_local.read(key)

    benchmark.pedantic(
        workload,
        rounds=n_rounds,
        warmup_rounds=N_WARMUP,
    )