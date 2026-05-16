#!/usr/bin/env python3
"""
prepare_data.py — generate gnuplot .dat files from benchmark JSON results.

Run this once from the directory containing the results_*.json files:
    python3 prepare_data.py

It will create the 9 .dat files gnuplot needs in the same directory.
"""

import json, glob, os, sys
import numpy as np
from collections import defaultdict

here = os.path.dirname(os.path.abspath(__file__))
pattern = os.path.join(here, "results_*.json")
files = sorted(glob.glob(pattern))

if not files:
    print(f"ERROR: no results_*.json files found in {here}", file=sys.stderr)
    sys.exit(1)

print(f"Found {len(files)} result files in {here}")

data = defaultdict(list)

for fpath in files:
    name = os.path.basename(fpath).replace("results_", "").replace(".json", "")
    combo, _ = name.rsplit("_run", 1)
    tokens = combo.split("_")
    workload = tokens[-1]
    backend = "_".join(tokens[:-1])
    if backend == "s3":
        backend = "minio"

    with open(fpath) as f:
        d = json.load(f)

    for b in d["benchmarks"]:
        system = "opendal" if "baseline" in b["name"] else "securedal"
        size = b["params"]["name"]
        mean_ms   = b["stats"]["mean"]   * 1000
        stddev_ms = b["stats"]["stddev"] * 1000
        ops       = b["stats"]["ops"]
        data[(backend, workload, system, size)].append((mean_ms, ops, stddev_ms))

backends  = ["s3_minio", "postgresql", "redis"]
workloads = ["read", "write", "mixed"]
sizes     = ["4kb", "64kb", "1mb", "16mb"]
size_labels = ["4 KB", "64 KB", "1 MB", "16 MB"]

for backend in backends:
    for workload in workloads:
        fname = os.path.join(here, f"{backend}_{workload}.dat")
        with open(fname, "w") as f:
            f.write("# x  opendal_lat  opendal_lat_err  securedal_lat  securedal_lat_err"
                    "  opendal_ops  opendal_ops_err  securedal_ops  securedal_ops_err\n")
            for i, size in enumerate(sizes):
                od = data[(backend, workload, "opendal",   size)]
                sd = data[(backend, workload, "securedal", size)]
                if not od or not sd:
                    print(f"  WARNING: missing data for {backend}/{workload}/{size}", file=sys.stderr)
                    continue
                od_lat     = np.mean([v[0] for v in od])
                od_lat_err = np.std( [v[0] for v in od])
                sd_lat     = np.mean([v[0] for v in sd])
                sd_lat_err = np.std( [v[0] for v in sd])
                od_ops     = np.mean([v[1] for v in od])
                od_ops_err = np.std( [v[1] for v in od])
                sd_ops     = np.mean([v[1] for v in sd])
                sd_ops_err = np.std( [v[1] for v in sd])
                f.write(f"{i+1}  {od_lat:.6f}  {od_lat_err:.6f}"
                        f"  {sd_lat:.6f}  {sd_lat_err:.6f}"
                        f"  {od_ops:.4f}  {od_ops_err:.4f}"
                        f"  {sd_ops:.4f}  {sd_ops_err:.4f}\n")
        print(f"  Written: {os.path.basename(fname)}")

print("\nDone. Now run:  bash run_plots.sh")
