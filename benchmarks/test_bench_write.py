# benchmarks/test_bench_write.py
import pytest
from benchmarks.conftest import TEST_CASE, N_WARMUP
import random

# -- Baseline benchmarks ------------------------------------

@pytest.mark.parametrize("name,size", TEST_CASE)
def test_baseline_write(benchmark, clean, baseline_op, name, size, key_pool, data_pool, n_rounds):
    key_iter = iter(key_pool[name])

    def workload():
        key = next(key_iter)
        data = random.choice(data_pool[name])
        baseline_op.write(key, data)

    benchmark.pedantic(
        workload,
        rounds=n_rounds,
        warmup_rounds=N_WARMUP,
    )

# -- SDK benchmarks -----------------------------------------

@pytest.mark.parametrize("name,size", TEST_CASE)
def test_sdk_write(benchmark, clean, tamper_op_local, name, size, key_pool, data_pool, n_rounds):
    key_iter = iter(key_pool[name])

    def workload():
        key = next(key_iter)
        data = random.choice(data_pool[name])
        tamper_op_local.write(key, data)

    benchmark.pedantic(
        workload,
        rounds=n_rounds,
        warmup_rounds=N_WARMUP,
    )