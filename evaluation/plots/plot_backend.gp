# Master gnuplot script for one backend
# plot_backend.gp
# USAGE — from any directory:
#
#   # Recommended: use the companion shell script
#   bash run_plots.sh
#
#   # Or set scriptdir manually to wherever the .dat files live:
#   gnuplot -e "scriptdir='/abs/path/to/scripts'; backend='redis'; btitle='Redis'" plot_backend.gp
#
# Combined vertical PDF (default):
#   gnuplot -e "scriptdir='/path'; backend='s3_minio'; btitle='MinIO (S3-Compatible Storage)'" plot_backend.gp
#
# Combined horizontal PDF (add orientation='horizontal'):
#   gnuplot -e "scriptdir='/path'; backend='s3_minio'; btitle='MinIO (S3-Compatible Storage)'; orientation='horizontal'" plot_backend.gp
#
# Individual PDFs per workload x metric (add individual=1):
#   gnuplot -e "scriptdir='/path'; backend='redis'; btitle='Redis'; individual=1" plot_backend.gp

# ── Colour / style ──────────────────────────────────────────────────────────
set style data histogram
set style histogram errorbars linewidth 1.2
set style fill solid 0.85 border -1
set boxwidth 0.35

# OpenDAL   = dark blue  (#2166ac)
# SecureDAL = dark red   (#d6604d)
set linetype 1 lc rgb "#2166ac" lw 1.5 pt 7 ps 0.8
set linetype 2 lc rgb "#d6604d" lw 1.5 pt 5 ps 0.8

# ── Workload definitions ─────────────────────────────────────────────────────
workloads  = "read write mixed"
wtitles    = "Read-Only Write-Only Mix{/=9 Read/Write}"
wfilenames = "read-only write-only mix-read-write"

# ── Main loop ────────────────────────────────────────────────────────────────
do for [wi=1:3] {
    wl  = word(workloads,  wi)
    wt  = word(wtitles,    wi)
    wfn = word(wfilenames, wi)
    datafile = scriptdir . "/dat/" . backend . "_" . wl . ".dat"

    if (!exists("individual") || individual == 0) {
        # Check orientation (default to vertical if not specified)
        if (!exists("orientation")) { orientation = "vertical" }

        if (orientation eq "horizontal") {
            # -- COMBINED: 2x3 multiplot (Latency row, Throughput row) -----------------
            set terminal pdfcairo enhanced color font "Times New Roman,10" size 26cm,14cm
            set output scriptdir . "/plots/" . backend . "_horizontal.pdf"
            set multiplot layout 2,3 \
                title sprintf("{/Times-Bold=12 %s - Latency and Throughput}", btitle) \
                margins 0.06, 0.98, 0.10, 0.90 spacing 0.08, 0.12

            # Row 1: Mean Latency across workloads (read, write, mixed)
            do for [wi=1:3] {
                wl  = word(workloads,  wi)
                wt  = word(wtitles,    wi)
                datafile = scriptdir . "/dat/" . backend . "_" . wl . ".dat"

                set key top left samplen 2 spacing 1.2 font ",9"
                set title sprintf("{/Times-Bold=11 %s - Mean Latency}", wt) offset 0,-0.3
                set ylabel "Mean Latency (ms)" font ",9" offset 1,0
                set xlabel "Payload Size" font ",9"
                set yrange [0:*]
                set xrange [0.5:4.5]
                set xtics ("4 KB" 1, "64 KB" 2, "1 MB" 3, "16 MB" 4) font ",8"
                set ytics font ",8"
                set grid ytics lt 0 lw 0.5 lc rgb "#cccccc"
                set border 3
                set tics out nomirror
                plot \
                    datafile using ($1-0.19):2:3 with boxerrorbars lt 1 title "Baseline", \
                    datafile using ($1+0.19):4:5 with boxerrorbars lt 2 title "Prototype", \
                    datafile using ($1-0.19):2:(sprintf("%.2f",$2)) with labels offset 0,0.8 notitle, \
                    datafile using ($1+0.19):4:(sprintf("%.2f",$4)) with labels offset 0,0.8 notitle
            }

            # Row 2: Throughput across workloads (read, write, mixed)
            do for [wi=1:3] {
                wl  = word(workloads,  wi)
                wt  = word(wtitles,    wi)
                datafile = scriptdir . "/dat/" . backend . "_" . wl . ".dat"

                set key top right samplen 2 spacing 1.2 font ",9"
                set title sprintf("{/Times-Bold=11 %s - Throughput}", wt) offset 0,-0.3
                set ylabel "Throughput (ops/s)" font ",9" offset 1,0
                set xlabel "Payload Size" font ",9"
                set yrange [0:*]
                set xrange [0.5:4.5]
                set xtics ("4 KB" 1, "64 KB" 2, "1 MB" 3, "16 MB" 4) font ",8"
                set ytics font ",8"
                set grid ytics lt 0 lw 0.5 lc rgb "#cccccc"
                set border 3
                set tics out nomirror
                plot \
                    datafile using ($1-0.19):6:7 with boxerrorbars lt 1 title "Baseline", \
                    datafile using ($1+0.19):8:9 with boxerrorbars lt 2 title "Prototype", \
                    datafile using ($1-0.19):6:(sprintf("%.0f",$6)) with labels offset 0,0.8 notitle, \
                    datafile using ($1+0.19):8:(sprintf("%.0f",$8)) with labels offset 0,0.8 notitle
            }

            unset multiplot

        } else {
            # ── COMBINED: 3x2 multiplot, one PDF per backend ──────────────────
            if (wi == 1) {
                set terminal pdfcairo enhanced color font "Times New Roman,10" size 18cm,22cm
                set output scriptdir . "/plots/" . backend . ".pdf"
                set multiplot layout 3,2 \
                    title sprintf("{/Times-Bold=12 %s — Latency and Throughput}", btitle) \
                    margins 0.10, 0.97, 0.04, 0.93 spacing 0.12, 0.10
            }

            # Left panel: Mean Latency
            set key top left samplen 2 spacing 1.2 font ",9"
            set title sprintf("{/Times-Bold=11 %s — Mean Latency}", wt) offset 0,-0.3
            set ylabel "Mean Latency (ms)" font ",9" offset 1,0
            set xlabel "Payload Size" font ",9"
            set yrange [0:*]
            set xrange [0.5:4.5]
            set xtics ("4 KB" 1, "64 KB" 2, "1 MB" 3, "16 MB" 4) font ",8"
            set ytics font ",8"
            set grid ytics lt 0 lw 0.5 lc rgb "#cccccc"
            set border 3
            set tics out nomirror
            plot \
                datafile using ($1-0.19):2:3 with boxerrorbars lt 1 title "Baseline", \
                datafile using ($1+0.19):4:5 with boxerrorbars lt 2 title "Prototype", \
                datafile using ($1-0.19):2:(sprintf("%.2f",$2)) with labels offset 0,0.8 notitle, \
                datafile using ($1+0.19):4:(sprintf("%.2f",$4)) with labels offset 0,0.8 notitle

            # Right panel: Throughput
            set key top right samplen 2 spacing 1.2 font ",9"
            set title sprintf("{/Times-Bold=11 %s — Throughput}", wt) offset 0,-0.3
            set ylabel "Throughput (ops/s)" font ",9" offset 1,0
            set xlabel "Payload Size" font ",9"
            set yrange [0:*]
            plot \
                datafile using ($1-0.19):6:7 with boxerrorbars lt 1 title "Baseline", \
                datafile using ($1+0.19):8:9 with boxerrorbars lt 2 title "Prototype", \
                datafile using ($1-0.19):6:(sprintf("%.0f",$6)) with labels offset 0,0.8 notitle, \
                datafile using ($1+0.19):8:(sprintf("%.0f",$8)) with labels offset 0,0.8 notitle

            if (wi == 3) { unset multiplot }
        }

    } else {
        # ── INDIVIDUAL: one PDF per workload x metric ─────────────────────

        # Latency
        set terminal pdfcairo enhanced color font "Times New Roman,10" size 9cm,7cm
        set output scriptdir . "/plots/" . backend . "_" . wfn . "_latency.pdf"
        set key top left samplen 2 spacing 1.2 font ",9"
        set title sprintf("{/Times-Bold=11 %s — %s — Mean Latency}", btitle, wt) offset 0,-0.3
        set ylabel "Mean Latency (ms)" font ",9" offset 1,0
        set xlabel "Payload Size" font ",9"
        set yrange [0:*]
        set xrange [0.5:4.5]
        set xtics ("4 KB" 1, "64 KB" 2, "1 MB" 3, "16 MB" 4) font ",8"
        set ytics font ",8"
        set grid ytics lt 0 lw 0.5 lc rgb "#cccccc"
        set border 3
        set tics out nomirror
        plot datafile using ($1-0.19):2:3 with boxerrorbars lt 1 title "Baseline", \
             datafile using ($1+0.19):4:5 with boxerrorbars lt 2 title "Prototype"

        # Throughput
        set terminal pdfcairo enhanced color font "Times New Roman,10" size 9cm,7cm
        set output scriptdir . "/plots/" . backend . "_" . wfn . "_throughput.pdf"
        set key top right samplen 2 spacing 1.2 font ",9"
        set title sprintf("{/Times-Bold=11 %s — %s — Throughput}", btitle, wt) offset 0,-0.3
        set ylabel "Throughput (ops/s)" font ",9" offset 1,0
        set xlabel "Payload Size" font ",9"
        set yrange [0:*]
        plot datafile using ($1-0.19):6:7 with boxerrorbars lt 1 title "Baseline", \
             datafile using ($1+0.19):8:9 with boxerrorbars lt 2 title "Prototype"
    }
}
