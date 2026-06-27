# plot_comparison.gp
#
# Produces:
#   baseline_comparison.pdf
#   prototype_comparison.pdf

set style data linespoints

# MinIO
set linetype 1 lc rgb "#2166ac" lw 2 pt 7 ps 0.9

# PostgreSQL
set linetype 2 lc rgb "#1a9641" lw 2 pt 5 ps 0.9

# Redis
set linetype 3 lc rgb "#d6604d" lw 2 pt 9 ps 0.9

workloads = "read write mixed"
wtitles   = "Read-Only Write-Only Mix{/=9 Read/Write}"

do for [mode=0:1] {

    if (mode == 0) {
        outfile = "baseline_comparison.pdf"
        title_prefix = "Baseline"
        lat_col = 2
        ops_col = 6
    } else {
        outfile = "prototype_comparison.pdf"
        title_prefix = "Prototype"
        lat_col = 4
        ops_col = 8
    }

    set terminal pdfcairo enhanced color font "Times New Roman,10" size 18cm,22cm
    set output scriptdir . "/plots/" . outfile

    set multiplot layout 3,2 \
        title sprintf("{/Times-Bold=12 %s Performance Comparison Across Backends}", title_prefix) \
        margins 0.10,0.97,0.04,0.93 spacing 0.12,0.10

    do for [wi=1:3] {

        wl = word(workloads, wi)
        wt = word(wtitles, wi)

        # --------------------------------------------------------------
        # LATENCY
        # --------------------------------------------------------------

        set title sprintf("{/Times-Bold=11 %s — Mean Latency}", wt)
        set ylabel "Mean Latency (ms)" font ",9"
        set xlabel "Payload Size" font ",9"

        set xrange [0.5:4.5]
        set yrange [0:*]

        set xtics ("4 KB" 1, "64 KB" 2, "1 MB" 3, "16 MB" 4) font ",8"
        set ytics font ",8"

        set grid ytics lt 0 lw 0.5 lc rgb "#cccccc"
        set border 3
        set tics out nomirror

        set key top left samplen 2 spacing 1.2 font ",9"

        plot \
            scriptdir."/dat/s3_minio_".wl.".dat" using 1:lat_col \
                with linespoints lt 1 title "MinIO", \
            scriptdir."/dat/postgresql_".wl.".dat" using 1:lat_col \
                with linespoints lt 2 title "PostgreSQL", \
            scriptdir."/dat/redis_".wl.".dat" using 1:lat_col \
                with linespoints lt 3 title "Redis", \
            \
            scriptdir."/dat/s3_minio_".wl.".dat" using \
                1:lat_col:(sprintf("%.2f",column(lat_col))) \
                with labels tc ls 1 offset -3,0.7 notitle, \
            scriptdir."/dat/postgresql_".wl.".dat" using \
                1:lat_col:(sprintf("%.2f",column(lat_col))) \
                with labels tc ls 2 offset 0,1.4 notitle, \
            scriptdir."/dat/redis_".wl.".dat" using \
                1:lat_col:(sprintf("%.2f",column(lat_col))) \
                with labels tc ls 3 offset 3,0.7 notitle

        # --------------------------------------------------------------
        # THROUGHPUT
        # --------------------------------------------------------------

        set title sprintf("{/Times-Bold=11 %s — Throughput}", wt)
        set ylabel "Throughput (ops/s)" font ",9"
        set xlabel "Payload Size" font ",9"

        set key top right samplen 2 spacing 1.2 font ",9"

        plot \
            scriptdir."/dat/s3_minio_".wl.".dat" using 1:ops_col \
                with linespoints lt 1 title "MinIO", \
            scriptdir."/dat/postgresql_".wl.".dat" using 1:ops_col \
                with linespoints lt 2 title "PostgreSQL", \
            scriptdir."/dat/redis_".wl.".dat" using 1:ops_col \
                with linespoints lt 3 title "Redis", \
            \
            scriptdir."/dat/s3_minio_".wl.".dat" using \
                1:ops_col:(sprintf("%.0f",column(ops_col))) \
                with labels tc ls 1 offset -3,0.7 notitle, \
            scriptdir."/dat/postgresql_".wl.".dat" using \
                1:ops_col:(sprintf("%.0f",column(ops_col))) \
                with labels tc ls 2 offset 0,1.4 notitle, \
            scriptdir."/dat/redis_".wl.".dat" using \
                1:ops_col:(sprintf("%.0f",column(ops_col))) \
                with labels tc ls 3 offset 3,0.7 notitle
    }

    unset multiplot
}