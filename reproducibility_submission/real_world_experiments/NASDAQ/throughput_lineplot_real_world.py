import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

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
df.sort_values(by=['Summary Size', 'Time Window Size'], inplace=True)

df['Throughput SuSe'] = (df['stream_size'] / df['Execution Time SuSe']) * 1e9

queries_of_interest = [df['Query'].unique()[0], df['Query'].unique()[1]]  # Replace these with the actual query strings you're interested in
summary_sizes = df['Summary Size'].unique()
time_window_sizes = df['Time Window Size'].unique()
time_window_sizes = [size for size in df['Time Window Size'].unique() if size <= 500]
markers = ['o', '^', 's', 'D', 'P', 'v']
colors_set1 = ['#F49AC2', '#AEDFF7', '#B19CD9']
colors_set2 = ['#FFB347', '#77DD77', '#AEC6CF']
marker_idx = 0
fig, ax = plt.subplots()

for q_idx, query in enumerate(queries_of_interest):
    colors = colors_set1 if q_idx == 0 else colors_set2

    for idx, time_window_size in enumerate(time_window_sizes):
        plot_data = []

        for summary_size in summary_sizes:
            filtered_df = df[(df['Query'] == query) &
                             (df['Summary Size'] == summary_size) &
                             (df['Time Window Size'] == time_window_size)]

            for val in filtered_df['Throughput SuSe']:
                plot_data.append([summary_size, val])

        plot_df = pd.DataFrame(plot_data, columns=['Summary Size', 'Throughput SuSe'])
        means = plot_df.groupby(['Summary Size'])['Throughput SuSe'].mean().reset_index()

        ax.plot(means['Summary Size'], means['Throughput SuSe'],
                label = f"$q_\\tau: \\mathbf{{{time_window_size}}}; \\mathbf{{Q{q_idx}}}$",
                marker=markers[marker_idx], color=colors[idx], linestyle='--', linewidth=2, markersize=8)
        marker_idx += 1


ax.set_xticks([100, 250, 500])
ax.set_yscale('log')
ax.set_xlabel(r"Summary Sizes $|\mathcal{S}|$", fontsize=24)
ax.set_ylabel('Throughput (\#Elements/sec.)', fontsize=24)
ax.set_title('NASDAQ SuSe Throughput', fontsize=22)
ax.tick_params(axis='both', which='major', labelsize=24)
ax.set_ylim(10**1, 10**4)
ax.legend(loc='lower left', fontsize='large', ncol=2, columnspacing=0.4, prop={'weight':'bold', 'size':20}, framealpha=0.66, handletextpad=0.3, labelspacing=0.2, borderpad=0.2)

plt.grid()
plt.tight_layout()
plt.savefig('NASDAQ_throughput_lineplot.pdf', format='pdf')
