import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
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


df['Pos_Kleene'] = df['Query'].apply(lambda x: 0 if x.find('*') == -1 else (1 if x.find('*') == 1 else (2 if x.find('*') == (len(x) - 1) else 3)))

fig, ax = plt.subplots()

summary_size = 500
time_window_size = 100
alphabet_probability_distribution = "uniform"

df = df[(df['Summary Size'] == summary_size) &
         (df['Time Window Size'] == time_window_size) &
         (df['Evaluation Timestamps Probability Distribution'] == "poisson") &
         (df['Alphabet Probability Distribution'] == alphabet_probability_distribution)]


grouped_df = df.groupby('Pos_Kleene').agg({
    'Total Ratio SuSe/Random': 'mean',
    'Total Ratio SuSe/FIFO': 'mean'
}).reset_index()

grouped_df = grouped_df.sort_values('Pos_Kleene')

ax.plot(grouped_df['Pos_Kleene'], grouped_df['Total Ratio SuSe/Random'], linestyle='--', marker='x', color='#abc9ea', label=r'$\textbf{\textsc{SuSe}}\mathbf{/Random}$', linewidth=3, markersize=10)
ax.plot(grouped_df['Pos_Kleene'], grouped_df['Total Ratio SuSe/FIFO'], linestyle='-', marker='o', color='#efb792' , label=r'$\textbf{\textsc{SuSe}}\mathbf{/FIFO}$', linewidth=3, markersize=10)

ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels(["$\mathbf{No}$ $\mathbf{Kleene}$", "$\mathbf{Initiator}$", "$\mathbf{Terminator}$", "$\mathbf{Mid}$"], y=-0.015)

ax.set_yscale('log')
ax.set_xlabel('Position of Kleene Star Operator', fontsize=24)
ax.set_ylabel('Rel. Recall Improvement', fontsize=24)
ax.set_title('Changing Kleene Star Operator Position', fontsize=20)
ax.set_ylim(10**0,10**4)
ax.tick_params(axis='both', which='major', labelsize=23)
ax.grid(True, which="major", ls="-", c='0.66')

ax.legend(loc='lower right', fontsize="large", prop={'weight':'bold', 'size':20})

plt.tight_layout()
plt.savefig('positional_kleene_plot.pdf', format='pdf', bbox_inches='tight')
