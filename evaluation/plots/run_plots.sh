#!/usr/bin/env bash
# run_plots.sh — generate all SecureDAL benchmark plots
# Run from anywhere: bash /path/to/run_plots.sh

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLT_DIR="$DIR/plots"
GP="gnuplot"

echo ""
echo "==> Generating plots in: $DIR"
echo ""

# Combined (3x2 multiplot per backend)
echo "[1/12] MinIO combined..."
$GP -e "scriptdir='$DIR'; backend='s3_minio';      btitle='MinIO (S3-Compatible Storage)'" "$DIR/plot_backend.gp"

echo "[2/12] PostgreSQL combined..."
$GP -e "scriptdir='$DIR'; backend='postgresql'; btitle='PostgreSQL'"                     "$DIR/plot_backend.gp"

echo "[3/12] Redis combined..."
$GP -e "scriptdir='$DIR'; backend='redis';      btitle='Redis'"                          "$DIR/plot_backend.gp"

# Individual PDFs (6 per backend = 18 total)
echo "[4/12] MinIO individual..."
$GP -e "scriptdir='$DIR'; backend='s3_minio';      btitle='MinIO (S3-Compatible Storage)'; individual=1" "$DIR/plot_backend.gp"

echo "[5/12] PostgreSQL individual..."
$GP -e "scriptdir='$DIR'; backend='postgresql'; btitle='PostgreSQL';                     individual=1" "$DIR/plot_backend.gp"

echo "[6/12] Redis individual..."
$GP -e "scriptdir='$DIR'; backend='redis';      btitle='Redis';                          individual=1" "$DIR/plot_backend.gp"

# Overhead ratio summary
echo "[7/12] Latency overhead ratio..."
$GP -e "scriptdir='$DIR'" "$DIR/plot_latency_overhead.gp"

echo "[8/12] Throughput retention percentage..."
$GP -e "scriptdir='$DIR'" "$DIR/plot_throughput_retention.gp"

echo "[9/12] Overhead ratio table..."
python3 $DIR/export_overhead.py

echo "[10/12] Backend comparison plots..."
$GP -e "scriptdir='$DIR'" "$DIR/plot_comparison.gp"

echo "[11/12] Performance difference plots..."
$GP -e "scriptdir='$DIR'" "$DIR/plot_difference.gp"

echo "[12/12] Overhead vs. Baseline plots..."
$GP -e "scriptdir='$DIR'" "$DIR/plot_overhead_vs_baseline.gp"

echo ""
echo "Done. PDFs written to: $PLT_DIR"
ls "$PLT_DIR"/*.pdf
