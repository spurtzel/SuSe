from ast import literal_eval
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors
import colorsys
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


def adjust_brightness(color, factor):
    r, g, b = matplotlib.colors.to_rgb(color)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = max(min(l * factor, 1.0), 0.0)
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return r, g, b

df = pd.read_csv('report.csv')
df = df.sort_values(by=['Summary Size', 'Time Window Size'])

unique_summary_sizes = [100, 250, 500]
unique_time_window_sizes = df['Time Window Size'].unique()
alphabet_distributions = ['uniform', 'normal']

fig, ax = plt.subplots()

base_colors = ['bisque', '#CFF800']
markers = ['o', 'v', '^', 'p', '>', 's',]
marker_count = 0
for idx, summary_size in enumerate(unique_summary_sizes):
    brightness = 1 - 0.2 * idx 
    
    for j, distribution in enumerate(alphabet_distributions):
        color = adjust_brightness(base_colors[j], brightness)
        
        random_suse_ratios = []
        fifo_suse_ratios = []
        
        for time_window_size in unique_time_window_sizes:
            filtered_df = df[(df['Time Window Size'] == time_window_size) & 
                             (df['Summary Size'] == summary_size) &
                             (df['Evaluation Timestamps Probability Distribution'] == "poisson") &
                             (df['Alphabet Probability Distribution'] == distribution)]
            
            random_suse_ratios.append(filtered_df['Total Ratio SuSe/Random'].mean())
            fifo_suse_ratios.append(filtered_df['Total Ratio SuSe/FIFO'].mean())
        
        ax.plot(unique_time_window_sizes, random_suse_ratios, linestyle='-', marker=markers[marker_count], color=color, label=fr'\textbf{{S/R;}} \textbf{{{summary_size};}} \textbf{{{distribution[:1]}}}', linewidth=2, markersize=8)
        ax.plot(unique_time_window_sizes, fifo_suse_ratios, linestyle='--', marker=markers[marker_count], color=color, label=fr'\textbf{{S/F;}} \textbf{{{summary_size};}} \textbf{{{distribution[:1]}}}', linewidth=2, markersize=8)
        marker_count += 1


ax.set_yscale('log')
ax.set_xlabel(r'Time Window Sizes $q_\tau$', fontsize=24)
ax.set_ylabel('Rel. Recall Improvement', fontsize=24)
ax.set_title(r'Changing $|\mathcal{S}|$, $q_\tau$, and $P_\Sigma$', fontsize=24)
ax.set_ylim(10**-1)
#ax.legend(loc='upper left', fontsize='large', ncol=3, handlelength=1.5,  handletextpad=0.25, columnspacing=0.1, prop={'weight':'bold', 'size':16}, framealpha=0.1, bbox_to_anchor=(-0.02,1))
ax.legend(loc='upper left', fontsize='large', ncol=3, handlelength=1.5,  handletextpad=0.25, columnspacing=0.1, prop={'weight':'bold', 'size':16}, framealpha=0.1, bbox_to_anchor=(-0.02,1.05))
ax.tick_params(axis='both', which='major', labelsize=24)
ax.axhline(y=1, color='k', linestyle='--', linewidth=3)
ax.text(x=min(unique_time_window_sizes) - 17, y=.325, s='$10^0$', verticalalignment='bottom', horizontalalignment='right', fontsize=24)
plt.grid()
plt.tight_layout()
plt.savefig('probability_distribution_plot_uni_norm.pdf', format='pdf')
