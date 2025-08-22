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


def percent_formatter(x, pos):
    return f"{int(x)}%"


df = pd.read_csv('report.csv')

df['Num_Overlaps'] = df['Query'].apply(lambda x: 0 if x.find("|") == -1 else (len(x[x.find("|"):])-1)*10)

fig, ax = plt.subplots()

summary_size = 500
time_window_size = 100
alphabet_probability_distribution = "uniform"

df = df[(df['Summary Size'] == summary_size) &
         (df['Time Window Size'] == time_window_size) &
         (df['Evaluation Timestamps Probability Distribution'] == "poisson") &
         (df['Alphabet Probability Distribution'] == alphabet_probability_distribution)]


grouped_df = df.groupby('Num_Overlaps').agg({
    'Total Ratio SuSe/Random': 'mean',
    'Total Ratio SuSe/FIFO': 'mean'
}).reset_index()

grouped_df = grouped_df.sort_values('Num_Overlaps')

ax.plot(grouped_df['Num_Overlaps'], grouped_df['Total Ratio SuSe/Random'], linestyle='--', marker='x', color='#abc9ea', label=r'$\textbf{\textsc{SuSe}}\mathbf{/Random}$', linewidth=3, markersize=10)
ax.plot(grouped_df['Num_Overlaps'], grouped_df['Total Ratio SuSe/FIFO'], linestyle='-', marker='o', color='#efb792' , label=r'$\textbf{\textsc{SuSe}}\mathbf{/FIFO}$', linewidth=3, markersize=10)

ax.set_xticks([0, 20, 40, 60, 80])

ax.set_xticklabels(["$\mathbf{0\\%}$", "$\mathbf{20\%}$", "$\mathbf{40\%}$", "$\mathbf{60\%}$", "$\mathbf{80\%}$"])

#ax.xaxis.set_major_formatter(FuncFormatter(percent_formatter))
ax.set_yscale('log')
ax.set_xlabel('Pattern Character Overlap', fontsize=24)
ax.set_ylabel('Rel. Recall Improvement', fontsize=24)
ax.set_title('Increasing Pattern Character Overlap', fontsize=22)
ax.set_ylim(10**0,10**5)
ax.tick_params(axis='both', which='major', labelsize=24)
ax.grid(True, which="major", ls="-", c='0.66')

ax.legend(fontsize="large", prop={'weight':'bold', 'size':20}, loc='upper right')

plt.tight_layout()
plt.savefig('disjunction_operator_overlapping_percentage.pdf', format='pdf', bbox_inches='tight')
