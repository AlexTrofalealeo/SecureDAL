# Relative throughput: SecureDAL throughput as a percentage of OpenDAL throughput
# plot_throughput_retention.gp
# USAGE — from any directory:
#   bash run_plots.sh
#   # or manually:
#   gnuplot -e "scriptdir='/abs/path/to/scripts'" plot_throughput_retention.gp

set terminal pdfcairo enhanced color font "Times New Roman,10" size 18cm,9cm
set output scriptdir . "/plots/throughput_retention_percentage.pdf"

set multiplot layout 1,3 \
    title "{/Times-Bold=12 Prototype Throughput Relative to Baseline (\%)}" \
    margins 0.08, 0.97, 0.12, 0.88 spacing 0.10, 0.08

set style data linespoints

set linetype 1 lc rgb "#2166ac" lw 2 pt 7 ps 0.9   # MinIO
set linetype 2 lc rgb "#1a9641" lw 2 pt 5 ps 0.9   # PostgreSQL
set linetype 3 lc rgb "#d6604d" lw 2 pt 9 ps 0.9   # Redis

workloads = "read write mixed"
wtitles   = "Read-Only Write-Only Mix Read/Write"

do for [wi=1:3] {
    wl = word(workloads, wi)
    wt = word(wtitles, wi)

    set title sprintf("{/Times-Bold=11 %s}", wt) offset 0,-0.3
    set ylabel (wi==1 ? "Relative Throughput (\%)" : "") font ",9" offset 1,0
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
        scriptdir . "/dat/s3_minio_" . wl . ".dat" \
            using 1:(100.0*$8/$6) with linespoints lt 1 title "MinIO", \
        scriptdir . "/dat/postgresql_" . wl . ".dat" \
            using 1:(100.0*$8/$6) with linespoints lt 2 title "PostgreSQL", \
        scriptdir . "/dat/redis_" . wl . ".dat" \
            using 1:(100.0*$8/$6) with linespoints lt 3 title "Redis", \
        100 with lines lc rgb "#888888" lw 1 dt 2 notitle, \
        scriptdir . "/dat/s3_minio_" . wl . ".dat" \
            using 1:(100.0*$8/$6):(sprintf("%.1f%%",100.0*$8/$6)) \
            with labels tc ls 1 offset 0,1.4 notitle, \
        scriptdir . "/dat/postgresql_" . wl . ".dat" \
            using 1:(100.0*$8/$6):(sprintf("%.1f%%",100.0*$8/$6)) \
            with labels tc ls 2 offset -3.5,0.3 notitle, \
        scriptdir . "/dat/redis_" . wl . ".dat" \
            using 1:(100.0*$8/$6):(sprintf("%.1f%%",100.0*$8/$6)) \
            with labels tc ls 3 offset 3.5,-0.3 notitle
}

unset multiplot
unset output
