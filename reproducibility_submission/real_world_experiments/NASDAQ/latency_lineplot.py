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
df.sort_values(by=['Summary Size', 'Time Window Size'], inplace=True)
df['Average Latency SuSe (s)'] = df['Average Latency SuSe'] / 1e9
df['Min Latency SuSe (s)'] = df['Min Latency SuSe'] / 1e9
df['Max Latency SuSe (s)'] = df['Max Latency SuSe'] / 1e9

data = []
summary_sizes = [100, 250, 500]
time_window_size = 500
queries = [df['Query'].iloc[0], df['Query'].iloc[4]]
linestyles = ['-', '--']

for query in queries:
    for summary_size in summary_sizes:
        filtered_df = df[(df['Summary Size'] == summary_size) & (df['Time Window Size'] == time_window_size) & (df['Query'] == query)]
        for metric, column_name in [('Avg', 'Average Latency SuSe (s)'), ('Min', 'Min Latency SuSe (s)'), ('Max', 'Max Latency SuSe (s)')]:
            for latency in filtered_df[column_name]:
                data.append([summary_size, metric, latency, query])

df_long = pd.DataFrame(data, columns=['Summary Size', 'Metric', 'Latency', 'Query'])
means = df_long.groupby(['Summary Size', 'Metric', 'Query'])['Latency'].mean().reset_index()

custom_palette = {'Avg': '#AEDFF7', 'Min': '#B19CD9', 'Max': '#F49AC2'}
markers = {'Avg': 'v', 'Min': 'x', 'Max': 'X'}
fig, ax = plt.subplots()

for idx, query in enumerate(queries):
    linestyle = linestyles[idx]
    for metric, color in custom_palette.items():
        metric_data = means[(means['Metric'] == metric) & (means['Query'] == query)]
        ax.plot(metric_data['Summary Size'], metric_data['Latency'], label = f"\\textbf{{Avg. {metric}; Q{idx}}}", color=color, marker=markers[metric], linestyle=linestyle, linewidth=3, markersize=8)
                                                                            



ax.set_xticks([100, 250, 500])
ax.set_ylim(10**-7, 10**-1)
ax.set_yscale("log")
ax.set_xlabel(r"Summary Sizes $|\mathcal{S}|$", fontsize=24)
ax.set_ylabel('Latency (s) Per Element', fontsize=24)
ax.set_title('NASDAQ SuSe Processing Latency', fontsize=22)
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

label_to_handle = dict(zip(labels, handles))
sorted_handles = [label_to_handle[label] for label in desired_order if label in label_to_handle]
sorted_labels = [label for label in desired_order if label in label_to_handle]

ax.legend(sorted_handles, sorted_labels, title=None, loc='upper left', bbox_to_anchor=(0.4, 0.75), 
          ncols=1, fontsize='large', prop={'weight':'bold', 'size':18.5}, framealpha=0.66, 
          handletextpad=0.3, labelspacing=0.2, borderpad=0.2, columnspacing=.4)

plt.grid()
plt.tight_layout()
plt.savefig('NASDAQ_latency_lineplot.pdf', format='pdf')
