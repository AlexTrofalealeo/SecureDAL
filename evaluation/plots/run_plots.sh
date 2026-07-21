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
echo "[1/11] MinIO combined..."
$GP -e "scriptdir='$DIR'; backend='s3_minio';      btitle='MinIO (S3-Compatible Storage)'" "$DIR/plot_backend.gp"

echo "[2/11] PostgreSQL combined..."
$GP -e "scriptdir='$DIR'; backend='postgresql'; btitle='PostgreSQL'"                     "$DIR/plot_backend.gp"

echo "[3/11] Redis combined..."
$GP -e "scriptdir='$DIR'; backend='redis';      btitle='Redis'"                          "$DIR/plot_backend.gp"

# Individual PDFs (6 per backend = 18 total)
echo "[4/11] MinIO individual..."
$GP -e "scriptdir='$DIR'; backend='s3_minio';      btitle='MinIO (S3-Compatible Storage)'; individual=1" "$DIR/plot_backend.gp"

echo "[5/11] PostgreSQL individual..."
$GP -e "scriptdir='$DIR'; backend='postgresql'; btitle='PostgreSQL';                     individual=1" "$DIR/plot_backend.gp"

echo "[6/11] Redis individual..."
$GP -e "scriptdir='$DIR'; backend='redis';      btitle='Redis';                          individual=1" "$DIR/plot_backend.gp"

# Overhead ratio summary
echo "[7/11] Overhead ratio..."
$GP -e "scriptdir='$DIR'" "$DIR/plot_overhead.gp"

echo "[8/11] Overhead ratio table..."
python3 export_overhead.py

echo "[9/11] Backend comparison plots..."
$GP -e "scriptdir='$DIR'" "$DIR/plot_comparison.gp"

echo "[10/11] Performance difference plots..."
$GP -e "scriptdir='$DIR'" "$DIR/plot_difference.gp"

echo "[11/11] Overhead vs. Baseline plots..."
$GP -e "scriptdir='$DIR'" "$DIR/plot_overhead_vs_baseline.gp"

echo ""
echo "Done. PDFs written to: $PLT_DIR"
ls "$PLT_DIR"/*.pdf
