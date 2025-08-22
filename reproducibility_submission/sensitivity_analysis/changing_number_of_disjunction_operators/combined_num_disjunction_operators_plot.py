import pandas as pd
import matplotlib.pyplot as plt
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

df['Num_Disjunction_Operators'] = df['Query'].apply(lambda x: x.count('|'))


fig, ax = plt.subplots()

summary_size = 500
time_window_size= 100
alphabet_probability_distribution = "uniform"

df = df[(df['Summary Size'] == summary_size) &
         (df['Time Window Size'] == time_window_size) &
         (df['Evaluation Timestamps Probability Distribution'] == "poisson") &
         (df['Alphabet Probability Distribution'] == alphabet_probability_distribution)]

grouped_df = df.groupby('Num_Disjunction_Operators').agg({
    'Total Ratio SuSe/Random': 'mean',
    'Total Ratio SuSe/FIFO': 'mean'
}).reset_index()

grouped_df = grouped_df.sort_values('Num_Disjunction_Operators')

ax.plot(grouped_df['Num_Disjunction_Operators'], grouped_df['Total Ratio SuSe/Random'], linestyle='--', marker='x', color='#abc9ea', label=r'$\textbf{\textsc{SuSe}}\mathbf{/Random}$', linewidth=3, markersize=10)
ax.plot(grouped_df['Num_Disjunction_Operators'], grouped_df['Total Ratio SuSe/FIFO'], linestyle='-', marker='o', color='#efb792' , label=r'$\textbf{\textsc{SuSe}}\mathbf{/FIFO}$', linewidth=3, markersize=10)



ax.set_yscale('log')
ax.set_xlabel('\#Union Operators', fontsize=24)
ax.set_ylabel('Rel. Recall Improvement', fontsize=24)
ax.set_title('Increasing \#Union Operators', fontsize=24)

ax.tick_params(axis='both', which='major', labelsize=24)
ax.grid(True, which="major", ls="-", c='0.66')

ax.legend(loc='upper left', fontsize="large", prop={'weight':'bold', 'size':20}, ncol=2, columnspacing=0.5, handletextpad=0.3, bbox_to_anchor=(-0.00775, 1),)
ax.set_ylim(10**0,10**2)
plt.tight_layout()
plt.savefig('number_of_disjunction_operators_combined_plot.pdf', format='pdf', bbox_inches='tight')
