import os
import csv

RESULTS_DIR = "./plots/dat"

BACKENDS = ["s3_minio", "postgresql", "redis"]
WORKLOADS = ["read", "write", "mixed"]

OUTPUT_FILE = os.path.join("./plots/plots", "overhead_all_v2.csv")


def parse_line(parts):
    size = int(parts[0])

    op_lat = float(parts[1])
    op_ops = float(parts[5])

    sd_lat = float(parts[3])
    sd_ops = float(parts[7])

    lat_ov = sd_lat / op_lat if op_lat else None
    ops_ov = (sd_ops / op_ops)*100.0 if op_ops else None

    return size, op_lat, sd_lat, op_ops, sd_ops, lat_ov, ops_ov


def main():
    with open(OUTPUT_FILE, "w", newline="") as out:
        writer = csv.writer(out)

        writer.writerow([
            "backend",
            "workload",
            "size_index",
            "baseline_latency",
            "prototype_latency",
            "baseline_ops",
            "prototype_ops",
            "latency_overhead",
            "throughput_overhead"
        ])

        for backend in BACKENDS:
            for workload in WORKLOADS:
                path = os.path.join(
                    RESULTS_DIR,
                    f"{backend}_{workload}.dat"
                )

                if not os.path.exists(path):
                    print(f"[WARN] missing {path}")
                    continue

                with open(path, "r") as f:
                    for line in f:
                        line = line.strip()

                        if not line or line.startswith("#"):
                            continue

                        parts = line.split()
                        if len(parts) < 9:
                            continue

                        try:
                            (size,
                             op_lat,
                             sd_lat,
                             op_ops,
                             sd_ops,
                             lat_ov,
                             ops_ov) = parse_line(parts)

                            writer.writerow([
                                backend,
                                workload,
                                size,
                                op_lat,
                                sd_lat,
                                op_ops,
                                sd_ops,
                                lat_ov,
                                ops_ov
                            ])

                        except ValueError:
                            continue

    print(f"✔ Overhead CSV written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()