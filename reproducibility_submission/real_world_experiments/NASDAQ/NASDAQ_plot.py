# Import modules
from ast import literal_eval
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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


df = pd.read_csv('report.csv')
df = df.sort_values(by=['Summary Size', 'Time Window Size'])

unique_queries = df['Query'].unique()
unique_summary_sizes = [size for size in df['Summary Size'].unique() if size > 50]
unique_time_window_sizes = [size for size in df['Time Window Size'].unique() if size <= 500]


fig, ax = plt.subplots()

markers = ['o', '^', 's', 'D', 'P', 'v']

colors_set1 = ['#F49AC2', '#AEDFF7', '#B19CD9']
colors_set2 = ['#FFB347', '#77DD77', '#AEC6CF']

marker_idx = 0
for q_idx, query in enumerate([unique_queries[0], unique_queries[1]]):
    colors = colors_set1 if q_idx == 0 else colors_set2
    for idx, summary_size in enumerate(unique_summary_sizes):
        random_suse_ratios = []
        fifo_suse_ratios = []

        for time_window_size in unique_time_window_sizes:
            filtered_df = df[(df['Query'] == query) & 
                             (df['Time Window Size'] == time_window_size) & 
                             (df['Summary Size'] == summary_size)]
            random_suse_ratios.append(filtered_df['Total Ratio SuSe/Random'].mean())
            fifo_suse_ratios.append(filtered_df['Total Ratio SuSe/FIFO'].mean())

        ax.plot(unique_time_window_sizes, random_suse_ratios, linestyle='-', marker=markers[marker_idx], color=colors[idx % len(colors)], label = f'$\\mathbf{{S/R; {summary_size}; Q{q_idx}}}$', linewidth=2, markersize=8)
        ax.plot(unique_time_window_sizes, fifo_suse_ratios, linestyle='--', marker=markers[marker_idx], color=colors[idx % len(colors)], label = f'$\\mathbf{{S/F; {summary_size}; Q{q_idx}}}$', linewidth=2, markersize=8)
        marker_idx += 1



ax.set_xticks([100, 250, 500])
ax.set_yscale('log')
ax.set_xlabel(r'Time Window Sizes $q_\tau$', fontsize=24)
ax.set_ylabel('Rel. Recall Improvement', fontsize=24)
ax.set_title('NASDAQ Real-World Dataset', fontsize=22)
ax.legend(loc='lower right', fontsize='large', ncol=1, columnspacing=0.4, bbox_to_anchor=(.85, 0.005), prop={'weight':'bold', 'size':16}, framealpha=0.33, handletextpad=0.3, labelspacing=0.2, borderpad=0.2)
ax.tick_params(axis='both', which='major', labelsize=24)
ax.axhline(y=1, color='k', linestyle='--', linewidth=3) 
ax.text(x=min(unique_time_window_sizes) - 28, y=.125, s='$10^0$', verticalalignment='bottom', horizontalalignment='right', fontsize=24)
plt.grid()
plt.tight_layout()
plt.savefig('NASDAQ_queries.pdf', format='pdf')
