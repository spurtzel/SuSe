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

unique_summary_sizes = df['Summary Size'].unique()
unique_time_window_sizes = df['Time Window Size'].unique()

fig, ax = plt.subplots()

colors = ['#FFB347', '#77DD77', '#AEC6CF', '#F49AC2', '#AEDFF7', '#B19CD9', '#D1A3DD', '#FFF176', '#BBB1AC']


markers = ['x', 'o', 's', '^', 'v', '<', '>', 'X', '.']

for idx, summary_size in enumerate(unique_summary_sizes):
    suse_times = []
    random_times = []
    
    for time_window_size in unique_time_window_sizes:
        filtered_df = df[(df['Time Window Size'] == time_window_size) & 
                         (df['Summary Size'] == summary_size)]
        
        suse_times.append(filtered_df['Execution Time SuSe'].mean() / 1e9)
    
    ax.plot(unique_time_window_sizes, suse_times, linestyle='--', marker=markers[idx % len(markers)], color=colors[idx % len(colors)], label=fr"$\textbf{{\textsc{{SuSe}}}}\ {summary_size}$", linewidth=3, markersize=10)

query = df['Query'].iloc[0]
stream_size = df['stream_size'].iloc[0]
alphabet_prob = df['Alphabet Probability Distribution'].iloc[0]


ax.set_xticks([10, 100, 250, 500])
ax.set_xticklabels(['$\mathbf{10}$', '$\mathbf{100}$', '$\mathbf{250}$', '$\mathbf{500}$'])

ax.set_xlabel(r'Time Window Sizes $q_\tau$', fontsize=24)
ax.set_ylabel('Average Execution Time (s)', fontsize=24)
ax.tick_params(axis='y', which='major', labelsize=24)
ax.tick_params(axis='x', which='major', labelsize=24)
ax.set_yscale('log')
leg = ax.legend(loc='upper left', ncol=3, columnspacing=.2, bbox_to_anchor=(-0.0175, 1.04), framealpha=0.66, prop={'weight':'bold', 'size':18}, handletextpad=0.3, labelspacing=0.2, borderpad=0.005)
leg._legend_box.sep = 5

ax.set_title(r'Execution Times for Increasing $|\mathcal{S}|$ and $q_\tau$', fontsize=20, x=0.5, y=1.02)

#ax.text(x=-25, y=(10**5)-50000, s='$10^5$', verticalalignment='bottom', horizontalalignment='right', fontsize=24)
#ax.axhline(y=10**5, color='k', linestyle='--', linewidth=3) 
ax.set_ylim(10**0,20**5)
plt.grid()
plt.tight_layout()
plt.savefig('execution_time_summary_time_window_comparison.pdf', format='pdf')
