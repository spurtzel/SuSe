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
fig, ax = plt.subplots()

df['Query Length'] = df['Query'].str.len()

summary_size = 500
time_window_size= 100
alphabet_probability_distribution = "uniform"

df = df[(df['Summary Size'] == summary_size) &
         (df['Time Window Size'] == time_window_size) &
         (df['Evaluation Timestamps Probability Distribution'] == "poisson") &
         (df['Alphabet Probability Distribution'] == alphabet_probability_distribution)]

grouped = df.groupby('Query Length').agg({
    'Total Ratio SuSe/FIFO': np.mean,
    'Total Ratio SuSe/Random': np.mean
}).reset_index()

ax.plot(grouped['Query Length'], grouped['Total Ratio SuSe/Random'], linestyle='--', marker='x', color='#abc9ea', label=r'$\textbf{\textsc{SuSe}}\mathbf{/Random}$', linewidth=3, markersize=10)
ax.plot(grouped['Query Length'], grouped['Total Ratio SuSe/FIFO'], linestyle='-', marker='o', color='#efb792' , label=r'$\textbf{\textsc{SuSe}}\mathbf{/FIFO}$', linewidth=3, markersize=10)

ax.set_xticks([2, 4, 6, 8, 10, 12])

ax.set_yscale('log')
ax.set_xlabel(r'Pattern Length', fontsize=24)
ax.set_ylabel('Rel. Recall Improvement', fontsize=24)
ax.set_title('Increasing the Pattern Length', fontsize=24)
ax.legend(loc='upper left', fontsize='large', ncol=1, columnspacing=0.4, prop={'weight':'bold', 'size':20}, framealpha=0.66)
ax.tick_params(axis='both', which='major', labelsize=24)
ax.set_ylim(10**-1,10**5)
ax.axhline(y=1, color='k', linestyle='--', linewidth=3) 
ax.text(x=1.3, y=.5, s='$10^0$', verticalalignment='bottom', horizontalalignment='right', fontsize=24)
plt.grid()
plt.tight_layout()
plt.savefig('query_length_plot.pdf', format='pdf')
