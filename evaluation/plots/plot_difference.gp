# plot_difference.gp

set style data linespoints

# MinIO
set linetype 1 lc rgb "#2166ac" lw 2 pt 7 ps 0.9

# PostgreSQL
set linetype 2 lc rgb "#1a9641" lw 2 pt 5 ps 0.9

# Redis
set linetype 3 lc rgb "#d6604d" lw 2 pt 9 ps 0.9

workloads = "read write mixed"
wtitles   = "Read-Only Write-Only Mix{/=9 Read/Write}"

set terminal pdfcairo enhanced color font "Times New Roman,10" size 18cm,22cm
set output scriptdir . "/plots/performance_difference.pdf"

set multiplot layout 3,2 \
    title "{/Times-Bold=12 Prototype Performance Difference Relative to Baseline}" \
    margins 0.10,0.97,0.04,0.93 spacing 0.12,0.10

do for [wi=1:3] {

    wl = word(workloads, wi)
    wt = word(wtitles, wi)

    # ==========================================================
    # LATENCY DIFFERENCE
    # prototype - baseline
    # ==========================================================

    set title sprintf("{/Times-Bold=11 %s — Latency Difference}", wt)

    set ylabel "Latency Difference (ms)"
    set xlabel "Payload Size"

    set xrange [0.5:4.5]
    set xtics ("4 KB" 1, "64 KB" 2, "1 MB" 3, "16 MB" 4)

    set yrange [0:*]

    set grid ytics lt 0 lw 0.5 lc rgb "#cccccc"
    set border 3
    set tics out nomirror

    set key top left

    plot \
        scriptdir."/dat/s3_minio_".wl.".dat" using 1:($4-$2) \
            with linespoints lt 1 title "MinIO", \
        scriptdir."/dat/postgresql_".wl.".dat" using 1:($4-$2) \
            with linespoints lt 2 title "PostgreSQL", \
        scriptdir."/dat/redis_".wl.".dat" using 1:($4-$2) \
            with linespoints lt 3 title "Redis", \
        \
        scriptdir."/dat/s3_minio_".wl.".dat" using \
            1:($4-$2):(sprintf("%.2f",$4-$2)) \
            with labels tc ls 1 offset -3,0.7 notitle, \
        scriptdir."/dat/postgresql_".wl.".dat" using \
            1:($4-$2):(sprintf("%.2f",$4-$2)) \
            with labels tc ls 2 offset 0,1.4 notitle, \
        scriptdir."/dat/redis_".wl.".dat" using \
            1:($4-$2):(sprintf("%.2f",$4-$2)) \
            with labels tc ls 3 offset 3,0.7 notitle

    # ==========================================================
    # THROUGHPUT DIFFERENCE
    # baseline - prototype
    # ==========================================================

    set title sprintf("{/Times-Bold=11 %s — Throughput Difference}", wt)

    set ylabel "Throughput Difference (ops/s)"
    set xlabel "Payload Size"

    set key top right

    plot \
        scriptdir."/dat/s3_minio_".wl.".dat" using 1:($6-$8) \
            with linespoints lt 1 title "MinIO", \
        scriptdir."/dat/postgresql_".wl.".dat" using 1:($6-$8) \
            with linespoints lt 2 title "PostgreSQL", \
        scriptdir."/dat/redis_".wl.".dat" using 1:($6-$8) \
            with linespoints lt 3 title "Redis", \
        \
        scriptdir."/dat/s3_minio_".wl.".dat" using \
            1:($6-$8):(sprintf("%.0f",$6-$8)) \
            with labels tc ls 1 offset -3,0.7 notitle, \
        scriptdir."/dat/postgresql_".wl.".dat" using \
            1:($6-$8):(sprintf("%.0f",$6-$8)) \
            with labels tc ls 2 offset 0,1.4 notitle, \
        scriptdir."/dat/redis_".wl.".dat" using \
            1:($6-$8):(sprintf("%.0f",$6-$8)) \
            with labels tc ls 3 offset 3,0.7 notitle
}

unset multiplot