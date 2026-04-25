#!/bin/bash
# run_benchmarks.sh

set -e

BACKENDS=("s3" "redis" "postgresql")
WORKLOADS=("write" "read" "mixed")
N_ROUNDS=10000
N_REPEATS=3
RESULTS_DIR="./evaluation/results"
HISTOGRAM_DIR="./evaluation"

mkdir -p "$RESULTS_DIR"
mkdir -p "$HISTOGRAM_DIR"

for backend in "${BACKENDS[@]}"; do
    echo ""
    echo "========================================"
    echo "  Backend: $backend"
    echo "========================================"

    for run in $(seq 1 $N_REPEATS); do
        echo ""
        echo "  --- Run $run/$N_REPEATS ---"

        for workload in "${WORKLOADS[@]}"; do
            echo ""
            echo "  --- Workload: $workload ---"

            pytest benchmarks/test_bench_${workload}.py \
                --benchmark-json="${RESULTS_DIR}/results_${backend}_${workload}_run${run}.json" \
                --benchmark-histogram="${HISTOGRAM_DIR}/histogram_${backend}_${workload}_run${run}" \
                --backend="$backend" \
                --n-rounds="$N_ROUNDS" \
                --no-header \
                -q

            echo "  Done: $backend/$workload (run $run)"
        done
    done
done

echo ""
echo "Adding p95/p99 to result files..."
python benchmarks/extra_stats.py

echo ""
echo "================================================"
echo "  All benchmarks complete"
echo "  Raw results in: $RESULTS_DIR"
echo "  Final results in: ./evaluation/final_results"
echo "  Histograms in: $HISTOGRAM_DIR"
echo "================================================"