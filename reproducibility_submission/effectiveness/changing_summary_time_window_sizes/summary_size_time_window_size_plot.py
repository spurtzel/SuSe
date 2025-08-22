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

colors = ['#FFB347', '#77DD77', '#AEC6CF', '#F49AC2', '#AEDFF7', '#B19CD9']
markers = ['o', 'v', '^', 'p', '>', 's',]
for idx, summary_size in enumerate(unique_summary_sizes):
    random_suse_ratios = []
    fifo_suse_ratios = []
    
    for time_window_size in unique_time_window_sizes:
        filtered_df = df[(df['Time Window Size'] == time_window_size) & 
                         (df['Evaluation Timestamps Probability Distribution'] == "poisson") &
                         (df['Summary Size'] == summary_size)]
        
        random_suse_ratios.append(filtered_df['Total Ratio SuSe/Random'].mean())
        fifo_suse_ratios.append(filtered_df['Total Ratio SuSe/FIFO'].mean())

    ax.plot(unique_time_window_sizes, random_suse_ratios, linestyle='-', marker=markers[idx % 8], color=colors[idx % len(colors)], label=fr'\textbf{{S/R;}} \textbf{{{summary_size}}}', linewidth=2, markersize=8)
    ax.plot(unique_time_window_sizes, fifo_suse_ratios, linestyle='--', marker=markers[idx % 8], color=colors[idx % len(colors)], label=fr'\textbf{{S/F;}} \textbf{{{summary_size}}}', linewidth=2, markersize=8)





ax.set_yscale('log')
ax.set_xlabel(r'Time Window Sizes $q_\tau$', fontsize=24)
ax.set_ylabel('Rel. Recall Improvement', fontsize=24)
ax.set_ylim(10**-1)
ax.set_title(r'Increasing Summary Size $|\mathcal{S}|$ and $q_\tau$', fontsize=22)
ax.legend(loc='upper left', fontsize='large', ncol=3, columnspacing=0.1, prop={'weight':'bold', 'size':16}, framealpha=0.15, handletextpad=0.3)
ax.tick_params(axis='both', which='major', labelsize=24)
ax.axhline(y=1, color='k', linestyle='--', linewidth=3) 
ax.text(x=min(unique_time_window_sizes) - 17, y=.325, s='$10^0$', verticalalignment='bottom', horizontalalignment='right', fontsize=24)
plt.grid()
plt.tight_layout()
plt.savefig('summary_time_window_comparison.pdf', format='pdf')
