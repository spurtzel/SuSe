import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

df['Throughput SuSe'] = (df['stream_size'] / df['Execution Time SuSe']) * 1e9  # throughput per second

summary_sizes = [25, 50, 100, 250, 500, 1000, 2500, 5000]
time_window_sizes = [10, 50, 1000, 250, 500]
alphabet_probability_distribution = "uniform"

plot_data = []

for summary_size in summary_sizes:
    for time_window_size in time_window_sizes:
        filtered_df = df[
                (df['Summary Size'] == summary_size) &
                (df['Time Window Size'] == time_window_size) &
                (df['Evaluation Timestamps Probability Distribution'] == "uniform") &
                (df['Alphabet Probability Distribution'] == alphabet_probability_distribution)
            ]
        
        for val in filtered_df['Throughput SuSe']:
            plot_data.append([summary_size, val])

plot_df = pd.DataFrame(plot_data, columns=['Summary Size', 'Throughput SuSe'])

fig, ax = plt.subplots()
sns.boxplot(data=plot_df, x='Summary Size', y='Throughput SuSe', ax=ax, palette="pastel")

means = plot_df.groupby(['Summary Size'])['Throughput SuSe'].mean().reset_index()
mins = plot_df.groupby(['Summary Size'])['Throughput SuSe'].min().reset_index()
maxs = plot_df.groupby(['Summary Size'])['Throughput SuSe'].max().reset_index()

xticks_locs = ax.get_xticks()

ax.plot(
    xticks_locs,
    means['Throughput SuSe'],
    linestyle='--',
    marker='X',                 
    color='#000000',
    alpha=.9,
    linewidth=3,
    markersize=13,              
    label=r'$\textbf{\textsc{SuSe}}$ Average Throughput',
)
ax.set_yscale('log')


ax.set_xlabel(r"Summary Sizes $|\mathcal{S}|$", fontsize=24, labelpad=0)
ax.set_ylabel('Throughput (\#Elements/sec.)', fontsize=24, labelpad=-50)
ax.yaxis.set_label_coords(-0.1, 0.44) 


ax.set_title(r'$\textsc{SuSe}$ Throughput', fontsize=24)

ax.tick_params(axis='both', which='major', labelsize=23)
ax.set_ylim(10**0,10**6)

ax.set_xticklabels([
    r"$\textbf{50}$", r"$\textbf{100}$", r"$\textbf{250}$", 
    r"$\textbf{500}$", r"$\textbf{1000}$", r"$\textbf{2500}$", 
    r"$\textbf{5000}$"
])

plt.setp( ax.xaxis.get_majorticklabels(), rotation=15 ) 

ax.legend(loc='upper left', fontsize=20, ncol=1, columnspacing=0.4)
plt.grid()
plt.tight_layout()
plt.savefig('throughput_boxplot.pdf', format='pdf')
