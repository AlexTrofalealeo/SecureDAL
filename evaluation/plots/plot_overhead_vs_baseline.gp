# plot_latency_over_baseline_overhead.gp

set style data linespoints
set grid

# Colors (backends)
set linetype 1 lc rgb "#2166ac" lw 2 pt 7 ps 0.9   # MinIO
set linetype 2 lc rgb "#1a9641" lw 2 pt 5 ps 0.9   # PostgreSQL
set linetype 3 lc rgb "#d6604d" lw 2 pt 9 ps 0.9   # Redis

workloads = "read write mixed"
wtitles   = "Read-Only Write-Only Mix"

set terminal pdfcairo enhanced color font "Times New Roman,10" size 18cm,22cm
set output scriptdir . "/plots/latency_overhead_vs_baseline_2.pdf"

set multiplot layout 3,1 \
    title "{/Times-Bold=12 Latency Overhead vs Baseline Latency}" \
    margins 0.10,0.97,0.06,0.92 spacing 0.12,0.10

set logscale x

do for [wi=1:3] {

    wl = word(workloads, wi)
    wt = word(wtitles, wi)

    set title sprintf("{/Times-Bold=11 %s}", wt)

    set xlabel "Baseline Latency (ms)"
    set ylabel "Latency Overhead (×)"

    set xrange [*:*]
    set yrange [0:*]

    set key top right
    set grid

    plot \
        scriptdir."/dat/s3_minio_".wl.".dat" using 2:($4/$2) \
            with linespoints lt 1 title "MinIO", \
        scriptdir."/dat/postgresql_".wl.".dat" using 2:($4/$2) \
            with linespoints lt 2 title "PostgreSQL", \
        scriptdir."/dat/redis_".wl.".dat" using 2:($4/$2) \
            with linespoints lt 3 title "Redis"
}

unset multiplot