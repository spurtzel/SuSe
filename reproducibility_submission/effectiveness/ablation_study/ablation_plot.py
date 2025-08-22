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

df_present = pd.read_csv('report_present.csv')
df_present = df_present.sort_values(by=['Summary Size', 'Time Window Size'])

merged_df = pd.merge(df, df_present, on=['Random Seed', 'Summary Size', 'Time Window Size'], suffixes=('', '_present'))

unique_summary_sizes = merged_df['Summary Size'].unique()
unique_time_window_sizes = merged_df['Time Window Size'].unique()

fig, ax = plt.subplots()

colors = ['#FFB347', '#77DD77', '#AEC6CF', '#F49AC2', '#AEDFF7', '#B19CD9']
markers = ['o', 'v', 's', 'p', '>', 's', '.', 'p']
seeds = "SEEDS=("
for idx, summary_size in enumerate(unique_summary_sizes):
    suse_vs_suse_present_ratios = []
    
    for time_window_size in unique_time_window_sizes:
        filtered_df = merged_df[(merged_df['Time Window Size'] == time_window_size) & 
                                (merged_df['Summary Size'] == summary_size) &
                                (merged_df['Alphabet Probability Distribution'] == 'zipf')] 
        

        for seed in filtered_df['Random Seed']:
            seeds += str(seed) + " "
#            print(filtered_df['Random Seed'])
        if not filtered_df.empty:
            suse_matches = literal_eval(filtered_df['SuSe Complete Matches'].iloc[0])
            suse_present_matches = literal_eval(filtered_df['SuSe Complete Matches_present'].iloc[0])

            ratios = [a/b if b != 0 else 0 for a, b in zip(suse_matches, suse_present_matches)]
            suse_vs_suse_present_ratios.append(np.mean(ratios))
        else:
            suse_vs_suse_present_ratios.append(np.nan)

    ax.plot(unique_time_window_sizes, suse_vs_suse_present_ratios, linestyle='--', marker=markers[idx % len(markers)], color=colors[idx % len(colors)], label=fr"$\boldsymbol{{\mathcal{{B}}}} / \boldsymbol{{\mathcal{{B}}_{{\boldsymbol{{\mathrm{{pres}}}}}}}}$; $\boldsymbol{{|\mathcal{{S}}}}|$: \textbf{{{summary_size}}}", linewidth=3, markersize=10)

seeds += ")"

ax.set_yscale('log')
ax.set_xlabel(r'Time Window Sizes $q_\tau$', fontsize=24)
ax.set_ylabel('Rel. Recall Improvement', fontsize=24)
ax.set_title(r"Comparing $\boldsymbol{\mathcal{B}}$ with $\boldsymbol{\mathcal{B}_{\mathrm{pres}}}$", fontsize=24)
ax.legend(loc='upper left', fontsize='large', ncol=1, columnspacing=0.4, prop={'weight':'bold', 'size':18})
ax.set_ylim(10**-1)
ax.tick_params(axis='both', which='major', labelsize=23)
ax.axhline(y=1, color='k', linestyle='--', linewidth=3) 
ax.text(x=min(unique_time_window_sizes) - 14, y=.25, s='$10^0$', verticalalignment='bottom', horizontalalignment='right', fontsize=20)
plt.grid()
plt.tight_layout()
plt.savefig('ablation_plot.pdf', format='pdf')
