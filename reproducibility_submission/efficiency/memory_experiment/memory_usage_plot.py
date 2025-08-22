import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

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

def extract_max_resident_set_size(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "Maximum resident set size" in line:
                    return int(line.split()[-1]) / 1024  #convert from kilobytes to megabytes
    except Exception as e:
        print(f"Error while processing file {file_path}: {e}")

files = [f for f in os.listdir() if re.match(r'memory_metrics_run_\d+_\d+_\d+.txt', f)]
data = defaultdict(list)

for file in files:
    summary_size, time_window_size, _ = map(int, re.findall(r'\d+', file)[:3])
    max_resident_set_size = extract_max_resident_set_size(file)
    data['Summary Size'].append(summary_size)
    data['Time Window Size'].append(time_window_size)
    data['Max Resident Set Size'].append(max_resident_set_size)

df = pd.DataFrame(data)
df_grouped = df.groupby(['Summary Size', 'Time Window Size']).mean().reset_index()

colors = ['#FFB347', '#77DD77', '#AEC6CF', '#F49AC2', '#AEDFF7', '#B19CD9', '#D1A3DD', '#FFF176', '#BBB1AC']
markers = ['x', 'o', 's', '^', 'v', '<', '>', 'X', '.']

plt.figure()
unique_summary_sizes = df_grouped['Summary Size'].unique()
for idx, summary_size in enumerate(unique_summary_sizes):
    subset = df_grouped[df_grouped['Summary Size'] == summary_size]
    plt.plot(subset['Time Window Size'], subset['Max Resident Set Size'], label=fr'$\textbf{{\textsc{{SuSe}}}}$ \textbf{{{summary_size}}}', color=colors[idx % len(colors)], marker=markers[idx % len(markers)], linestyle='--', linewidth=3, markersize=10)

xtick_locations = [10, 100, 250, 500]  
xtick_labels = [r'\textbf{10}', r'\textbf{100}', r'\textbf{250}', r'\textbf{500}']  
plt.xticks(xtick_locations, xtick_labels)

plt.yscale('log')
#plt.ylim(10**1,10**3)
plt.xlabel(r'Time Window Size $q_\tau$', fontsize=24)
plt.ylabel('Avg. Max. Memory Usage (MB)', fontsize=24, y=0.45)
plt.title('Average Maximum Memory Usage', fontsize=22)
plt.tick_params(axis='both', which='both', labelsize=22)
plt.grid()
plt.legend(loc='upper left', ncol=2, columnspacing=0.4, bbox_to_anchor=(0.05, .99), framealpha=0.66, prop={'weight':'bold', 'size':20}, handletextpad=0.3, borderpad=0.15, labelspacing=0.1)
plt.tight_layout()
plt.savefig('average_maximum_memory_usage.pdf', format='pdf')
