#!/usr/bin/env bash
# run_plots.sh — generate all SecureDAL benchmark plots
# Run from anywhere: bash /path/to/run_plots.sh

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GP="gnuplot"

echo "==> Output directory: $DIR"
echo ""

# Combined (3x2 multiplot per backend)
echo "[1/7] MinIO combined..."
$GP -e "scriptdir='$DIR'; backend='minio';      btitle='MinIO (S3-Compatible Storage)'" "$DIR/plot_backend.gp"

echo "[2/7] PostgreSQL combined..."
$GP -e "scriptdir='$DIR'; backend='postgresql'; btitle='PostgreSQL'"                     "$DIR/plot_backend.gp"

echo "[3/7] Redis combined..."
$GP -e "scriptdir='$DIR'; backend='redis';      btitle='Redis'"                          "$DIR/plot_backend.gp"

# Individual PDFs (6 per backend = 18 total)
echo "[4/7] MinIO individual..."
$GP -e "scriptdir='$DIR'; backend='minio';      btitle='MinIO (S3-Compatible Storage)'; individual=1" "$DIR/plot_backend.gp"

echo "[5/7] PostgreSQL individual..."
$GP -e "scriptdir='$DIR'; backend='postgresql'; btitle='PostgreSQL';                     individual=1" "$DIR/plot_backend.gp"

echo "[6/7] Redis individual..."
$GP -e "scriptdir='$DIR'; backend='redis';      btitle='Redis';                          individual=1" "$DIR/plot_backend.gp"

# Overhead ratio summary
echo "[7/7] Overhead ratio..."
$GP -e "scriptdir='$DIR'" "$DIR/plot_overhead.gp"

echo ""
echo "Done. PDFs written to: $DIR"
ls "$DIR"/*.pdf
