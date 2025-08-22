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


df = pd.read_csv('report_query_0.csv')
df = df.sort_values(by=['Summary Size', 'Time Window Size'])

unique_queries = df['Query'].unique()
unique_summary_sizes = df['Summary Size'].unique()
unique_time_window_sizes = df['Time Window Size'].unique()

query = unique_queries[0]

fig, ax = plt.subplots()

colors_set1 = ['#F49AC2', '#AEDFF7', '#B19CD9']
markers = ['o', '^', 's', 'D', 'P', 'v']
marker_idx = 0
for idx, summary_size in enumerate(unique_summary_sizes):
    random_suse_ratios = []
    fifo_suse_ratios = []
    
    for time_window_size in unique_time_window_sizes:

        filtered_df = df[(df['Query'] == query) &
                         (df['Time Window Size'] == time_window_size) &
                         (df['Summary Size'] == summary_size)]
    
        random_suse_ratios.append(filtered_df['Total Ratio SuSe/Random'].mean())
        fifo_suse_ratios.append(filtered_df['Total Ratio SuSe/FIFO'].mean())
    ax.plot(unique_time_window_sizes, random_suse_ratios, linestyle='-', marker=markers[marker_idx], color=colors_set1[idx % len(colors_set1)], label=fr'$\textbf{{S/R; {summary_size}; Q0}}$', linewidth=2, markersize=8)
    ax.plot(unique_time_window_sizes, fifo_suse_ratios, linestyle='--', marker=markers[marker_idx], color=colors_set1[idx % len(colors_set1)], label=fr'$\textbf{{S/F; {summary_size}; Q0}}$', linewidth=2, markersize=8)
    marker_idx += 1

df2 = pd.read_csv('report_query_1.csv')
df2 = df2.sort_values(by=['Summary Size', 'Time Window Size'])

query2 = df2['Query'].unique()[0]
colors_set2 = ['#77DD77','#FFB347', '#77DD77', '#AEC6CF']
for idx, summary_size in enumerate(df2['Summary Size'].unique()):
    random_suse_ratios_2 = []
    fifo_suse_ratios_2 = []
    
    for time_window_size in df2['Time Window Size'].unique():

        filtered_df2 = df2[(df2['Query'] == query2) &
                           (df2['Time Window Size'] == time_window_size) &
                           (df2['Summary Size'] == summary_size)]

        random_suse_ratios_2.append(filtered_df2['Total Ratio SuSe/Random'].mean())
        fifo_suse_ratios_2.append(filtered_df2['Total Ratio SuSe/FIFO'].mean())
    if not all(v == 0 for v in random_suse_ratios_2):
        ax.plot(df2['Time Window Size'].unique(), random_suse_ratios_2, linestyle='-', marker=markers[marker_idx], color=colors_set2[idx % len(colors_set2)], label=fr'$\textbf{{S/R; {summary_size}; Q1}}$', linewidth=2, markersize=8)
    if not all(v == 0 for v in fifo_suse_ratios_2):
        ax.plot(df2['Time Window Size'].unique(), fifo_suse_ratios_2, linestyle='--', marker=markers[marker_idx], color=colors_set2[idx % len(colors_set2)], label=fr'$\textbf{{S/F; {summary_size}; Q1}}$', linewidth=2, markersize=8)




ax.set_xticks([100, 250, 500])
#ax.set_ylim(10**-3,10**12)
ax.set_yscale('log')
ax.set_xlabel(r'Time Window Sizes $q_\tau$', fontsize=24)
ax.set_ylabel('Rel. Recall Improvement', fontsize=24)
ax.set_title('Citi Bike Real-World Dataset', fontsize=22)
ax.legend(loc='lower right', fontsize='large', ncol=1, columnspacing=0.4, bbox_to_anchor=(.85, 0.25), prop={'weight':'bold', 'size':16}, framealpha=0.33, handletextpad=0.3, labelspacing=0.2, borderpad=0.2)
ax.tick_params(axis='both', which='major', labelsize=24)
ax.axhline(y=1, color='k', linestyle='--', linewidth=3) 
#ax.text(x=min(unique_time_window_sizes) - 28.5, y=.3, s='$10^0$', verticalalignment='bottom', horizontalalignment='right', fontsize=20)
plt.grid()
plt.tight_layout()
plt.savefig('CitiBike_queries.pdf', format='pdf')
