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

df1 = pd.read_csv('report_query_0.csv')
df2 = pd.read_csv('report_query_1.csv')
df1.sort_values(by=['Summary Size', 'Time Window Size'], inplace=True)
df2.sort_values(by=['Summary Size', 'Time Window Size'], inplace=True)

for df in [df1, df2]:
    df['Average Latency SuSe (s)'] = df['Average Latency SuSe'] / 1e9
    df['Min Latency SuSe (s)'] = df['Min Latency SuSe'] / 1e9
    df['Max Latency SuSe (s)'] = df['Max Latency SuSe'] / 1e9

queries = [df1['Query'].iloc[0], df2['Query'].iloc[0]]
#metrics = [('Avg', 'Average Latency SuSe (s)'), ('Min', 'Min Latency SuSe (s)'), ('Max', 'Max Latency SuSe (s)')]
metrics = [('Max', 'Max Latency SuSe (s)'),
           ('Avg', 'Average Latency SuSe (s)'),
           ('Min', 'Min Latency SuSe (s)')]

linestyles = ['-', '--']
summary_sizes = [100, 250, 500]
time_window_size = 500

fig, ax = plt.subplots()

for df_idx, df in enumerate([df1, df2]):
    data = []
    linestyle = linestyles[df_idx]
    
    for query in queries:
        for summary_size in summary_sizes:
            filtered_df = df[(df['Summary Size'] == summary_size) & (df['Time Window Size'] == time_window_size) & (df['Query'] == query)]
            
            for metric, column_name in metrics:
                for latency in filtered_df[column_name]:
                    data.append([summary_size, metric, latency])

    df_long = pd.DataFrame(data, columns=['Summary Size', 'Metric', 'Latency'])
    means = df_long.groupby(['Summary Size', 'Metric'])['Latency'].mean().reset_index()

    custom_palette = {'Avg': '#AEDFF7', 'Min': '#B19CD9', 'Max': '#F49AC2'}
    markers = {'Avg': 'v', 'Min': 'x', 'Max': 'X'}

    for metric, color in custom_palette.items():
        metric_data = means[means['Metric'] == metric]
        ax.plot(metric_data['Summary Size'], metric_data['Latency'], label = f"\\textbf{{Avg. {metric}; Q{df_idx}}}", color=color, marker=markers[metric], linestyle=linestyle, linewidth=3, markersize=8)



ax.set_xticks([100, 250, 500])
ax.set_ylim(10**-7, 10**-1)
ax.set_yscale("log")
ax.set_xlabel(r"Summary Sizes $|\mathcal{S}|$", fontsize=24)
ax.set_ylabel('Latency (s) Per Element', fontsize=24)
ax.set_title(r'Citi Bike \textsc{SuSe} Processing Latency', fontsize=22)
ax.tick_params(axis='both', which='major', labelsize=24)

handles, labels = ax.get_legend_handles_labels()


desired_order = [
    '\\textbf{Avg. Max; Q0}',
    '\\textbf{Avg. Max; Q1}',
    '\\textbf{Avg. Avg; Q0}',
    '\\textbf{Avg. Avg; Q1}',
    '\\textbf{Avg. Min; Q0}',
    '\\textbf{Avg. Min; Q1}',
]

order_indices = [labels.index(lbl) for lbl in desired_order]

reordered_handles = [handles[i] for i in order_indices]
reordered_labels  = [labels[i] for i in order_indices]

ax.legend(reordered_handles, reordered_labels, title=None, loc='upper left', bbox_to_anchor=(0.4, 0.75), ncols=1, fontsize='large', prop={'weight':'bold', 'size':18.5}, framealpha=0.66, handletextpad=0.3, labelspacing=0.2, borderpad=0.2, columnspacing=.4)

plt.grid()
plt.tight_layout()
plt.savefig('CitiBike_latency_lineplot.pdf', format='pdf')
