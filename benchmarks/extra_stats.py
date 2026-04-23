# benchmarks/extra_stats.py
import json
import sys
import os
import numpy as np

def add_percentiles(input_path: str, output_path: str):
    with open(input_path) as f:
        results = json.load(f)

    for bench in results["benchmarks"]:
        data = bench["stats"].get("data", [])
        if data:
            bench["stats"]["p95"] = float(np.percentile(data, 95))
            bench["stats"]["p99"] = float(np.percentile(data, 99))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"  Processed: {os.path.basename(input_path)}")

if __name__ == "__main__":
    input_dir  = "./evaluation/results"
    output_dir = "./evaluation/final_results"

    files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    if not files:
        print("No result files found.")
        sys.exit(1)

    for filename in sorted(files):
        input_path  = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        add_percentiles(input_path, output_path)

    print(f"\nDone. {len(files)} file(s) processed → {output_dir}")