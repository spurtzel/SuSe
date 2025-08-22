import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

plt.rcParams.update({
    'text.usetex': True,
    'font.family': 'serif',
    'font.serif': ['Palatino'],
    'axes.labelsize': 25,
    'axes.titlesize': 25,
    'xtick.labelsize': 25,
    'ytick.labelsize': 25,
    'text.latex.preamble': r'''
        \usepackage[T1]{fontenc}
        \usepackage{amsmath}
        \usepackage{amssymb}
        \usepackage{bm}
        \boldmath
    '''
})

LEN_RE = re.compile(r'Input length:\s*(\d+)')
SEC_RE = re.compile(r'([\d.]+)\s*seconds')

def parse_length_times(filename: str) -> dict[int, float]:
    times = {}
    cur = None
    with open(filename, 'r') as f:
        for line in f:
            m = LEN_RE.search(line)
            if m:
                cur = int(m.group(1))
                continue
            m = SEC_RE.search(line)
            if m and cur is not None:
                times[cur] = float(m.group(1))
                cur = None
    return times

def throughput_gain(suse_time_by_size: dict[int, float], other_time_by_size: dict[int, float]) -> tuple[list[int], list[float]]:
    xs = sorted(set(suse_time_by_size).intersection(other_time_by_size))
    ys = [other_time_by_size[s] / suse_time_by_size[s] for s in xs]
    return xs, ys

df = pd.read_csv('report.csv').sort_values('stream_size')
stream_sizes = df['stream_size'].tolist()
suse_time_by_size = dict(zip(df['stream_size'], df['Execution Time SuSe'] / 1e9))

core_time_by_size    = parse_length_times('times_core.txt')     
flink_time_by_size   = parse_length_times('times_flink.txt')    
rematch_time_by_size = parse_length_times('times_rematch.txt')  

suse_throughput = [s / suse_time_by_size[s] for s in sorted(suse_time_by_size)]

rematch_throughput = [s / rematch_time_by_size[s] for s in sorted(rematch_time_by_size)]


x_r, tg_r = throughput_gain(suse_time_by_size, rematch_time_by_size)
x_f, tg_f = throughput_gain(suse_time_by_size, flink_time_by_size)
x_c, tg_c = throughput_gain(suse_time_by_size, core_time_by_size)

plt.figure()

plt.plot(
    x_r, tg_r,
    label=r'$\textbf{\textsc{StateSummary}}$$\textbf{/REmatch}$',
    marker='o', linestyle='-.', linewidth=3, markersize=10, color='#efb792'
)
plt.plot(
    x_f, tg_f,
    label=r'$\textbf{\textsc{StateSummary}}$$\textbf{/FlinkCEP}$',
    marker='^', linestyle=':', linewidth=3, markersize=10, color='#e2068c'
)
plt.plot(
    x_c, tg_c,
    label=r'$\textbf{\textsc{StateSummary}}$$\textbf{/CORE}$',
    marker='v', linestyle='-', linewidth=3, markersize=10, color='#bfff00'
)

plt.xscale('log')
plt.yscale('log')
plt.xlabel(r'\#Elements to Process', fontsize=24)
plt.ylabel(r'Throughput Gain', fontsize=24)
plt.title(r'$\textsc{StateSummary}$ Throughput Gain', fontsize=22)
plt.tick_params(axis='both', which='major', labelsize=24)
plt.grid()

plt.axhline(y=1, color='k', linestyle='--', linewidth=3)
plt.text(x=min(stream_sizes)*0.8, y=1.0, s='$10^0$',
         verticalalignment='bottom', horizontalalignment='right', fontsize=24)

plt.ylim(0.5 * 10**0, 10**8)

plt.legend(
    loc='upper left',
    fontsize='large',
    ncol=1,
    columnspacing=0.3,
    prop={'weight': 'bold', 'size': 18},
    borderpad=0.1,
    bbox_to_anchor=(0, 1.035),
    labelspacing=0.05,
    framealpha=0.5
)

plt.tight_layout()
plt.savefig('throughput_gain_over_rematch_core_flinkcep.pdf', format='pdf')
