import matplotlib.pyplot as plt
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

df1 = pd.read_csv('report_query_0.csv')
df2 = pd.read_csv('report_query_1.csv')
df1.sort_values(by=['Summary Size', 'Time Window Size'], inplace=True)
df2.sort_values(by=['Summary Size', 'Time Window Size'], inplace=True)


df1['Throughput SuSe'] = (df1['stream_size'] / df1['Execution Time SuSe']) * 1e9
df2['Throughput SuSe'] = (df2['stream_size'] / df2['Execution Time SuSe']) * 1e9


queries_of_interest = [df1['Query'].unique()[0], df2['Query'].unique()[0]]
summary_sizes = df1['Summary Size'].unique()
time_window_sizes = [size for size in df1['Time Window Size'].unique() if size <= 500]


markers = ['o', '^', 's', 'D', 'P', 'v']
colors_set1 = ['#F49AC2', '#AEDFF7', '#B19CD9']
colors_set2 = ['#FFB347', '#77DD77', '#AEC6CF']

fig, ax = plt.subplots()

marker_idx = 0
for q_idx, dfs in enumerate([(df1, colors_set1), (df2, colors_set2)]):
    df, colors = dfs
    query = queries_of_interest[q_idx]
    
    
    for idx, time_window_size in enumerate(time_window_sizes):
        plot_data = []

        for summary_size in summary_sizes:
            filtered_df = df[(df['Query'] == query) &
                             (df['Summary Size'] == summary_size) &
                             (df['Time Window Size'] == time_window_size)]

            for val in filtered_df['Throughput SuSe']:
                plot_data.append([summary_size, val])

        if all(val == 0 for _, val in plot_data):
            continue

        plot_df = pd.DataFrame(plot_data, columns=['Summary Size', 'Throughput SuSe'])
        means = plot_df.groupby(['Summary Size'])['Throughput SuSe'].mean().reset_index()

        ax.plot(means['Summary Size'], means['Throughput SuSe'],
                label = f"$q_\\tau: \\mathbf{{{time_window_size}}}; \\mathbf{{Q{q_idx}}}$",
                marker=markers[marker_idx], color=colors[idx], linestyle='--', linewidth=2, markersize=8)

        marker_idx += 1


ax.set_xticks([100, 250, 500])
ax.set_yscale('log')
ax.set_xlabel(r"Summary Sizes $|\mathcal{S}|$", fontsize=24)
ax.set_ylabel('Throughput (\#Elements/sec.)', fontsize=24, labelpad=-50)
ax.yaxis.set_label_coords(-0.1, 0.44)
ax.set_title(r'Citi Bike \textsc{SuSe} Throughput', fontsize=22)
ax.tick_params(axis='both', which='major', labelsize=24)
ax.set_ylim(10**1, 10**4)
ax.legend(loc='lower left', fontsize='large', ncol=2, columnspacing=0.4, prop={'weight':'bold', 'size':20}, framealpha=0.66, handletextpad=0.3, labelspacing=0.2, borderpad=0.2)

plt.grid()
plt.tight_layout()
plt.savefig('CitiBike_throughput_lineplot.pdf', format='pdf')
