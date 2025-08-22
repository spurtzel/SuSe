import pandas as pd
import matplotlib.pyplot as plt
import re

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

def parse_execution_times(filename):
    execution_times = []
    pattern = re.compile(r'([\d.]+)\s*seconds')

    with open(filename, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                execution_times.append(float(match.group(1)))
    return execution_times


def time_to_seconds(time_str):
    time_str = time_str.replace(',', '.')
    minutes, seconds = map(float, re.split('m|s', time_str)[:-1])
    return minutes * 60 + seconds


df = pd.read_csv('report.csv')
df = df.sort_values('stream_size')
stream_sizes = df['stream_size']
execution_time_suse_seconds = (df['Execution Time SuSe'] / 1e9).values.tolist()


CORE_times_s = parse_execution_times("times_core.txt")

FlinkCEP_times_s = parse_execution_times("times_flink.txt")
rematch_times = parse_execution_times("times_rematch.txt")

plt.figure()
plt.plot(stream_sizes, execution_time_suse_seconds, label=r'$\textsc{\textbf{StateSummary}}$', marker='x', linestyle='--', linewidth=3, markersize=10, color='#abc9ea')
plt.plot(stream_sizes[:len(rematch_times)], rematch_times, label=r'$\textbf{REmatch}$', marker='o', linestyle='-.', linewidth=3, markersize=10, color='#efb792')
plt.plot(stream_sizes[:len(CORE_times_s)], CORE_times_s, label=r'$\textbf{CORE}$', marker='v', linestyle='-', linewidth=3, markersize=10, color='#bfff00')
plt.plot(stream_sizes[:len(FlinkCEP_times_s)], FlinkCEP_times_s, label=r'$\textbf{FlinkCEP}$', marker='^', linestyle=':', linewidth=3, markersize=10, color='#e2068c')
plt.yscale('log')
plt.xscale('log')
plt.ylim(10**-5,10**7)
plt.xlabel(r'\#Elements to Process', fontsize=24)
plt.ylabel('Execution Time (seconds)', fontsize=24)
plt.title(r'$\textsc{StateSummary}$ vs SOTA RegEx/CEP Engines', fontsize=19, y=1.037, x=.47)
plt.tick_params(axis='both', which='major', labelsize=24)
plt.grid()
plt.legend(loc='upper left', fontsize='large', ncol=2, columnspacing=0.3, prop={'weight':'bold', 'size':18}, borderpad=0.1, bbox_to_anchor=(0,1.035), labelspacing=0.05, framealpha=0.5)
plt.tight_layout()
plt.savefig('suse_vs_rematch_vs_core_vs_flinkcep.pdf', format='pdf')
