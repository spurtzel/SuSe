import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import seaborn as sns

from matplotlib.patches import Patch, Rectangle

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

def make_boxplot_legend_patch(facecolor, edgecolor):
    return Rectangle((0, 0), 1, 1, linewidth=1, edgecolor=edgecolor, facecolor=facecolor)

df = pd.read_csv('report.csv')
df = df.sort_values(by=['Summary Size', 'Time Window Size'])
df['Average Latency SuSe (s)'] = df['Average Latency SuSe'] / 1e9
df['Min Latency SuSe (s)'] = df['Min Latency SuSe'] / 1e9
df['Max Latency SuSe (s)'] = df['Max Latency SuSe'] / 1e9

summary_sizes = [25, 50, 100, 250, 500, 1000, 2500, 5000]
time_window_sizes = [10, 50, 1000, 250, 500]
alphabet_probability_distribution = "uniform"

data = []
for summary_size in summary_sizes:
    for time_window_size in time_window_sizes:
        filtered_df = df[
            (df['Summary Size'] == summary_size) &
            (df['Time Window Size'] == time_window_size) &
            (df['Evaluation Timestamps Probability Distribution'] == "uniform") &
            (df['Alphabet Probability Distribution'] == alphabet_probability_distribution)
        ]
        
        for latency in filtered_df['Average Latency SuSe (s)']:
            data.append([summary_size, 'Avg', latency])
        for latency in filtered_df['Min Latency SuSe (s)']:
            data.append([summary_size, 'Min', latency])
        for latency in filtered_df['Max Latency SuSe (s)']:
            data.append([summary_size, 'Max', latency])

df_long = pd.DataFrame(data, columns=['Summary Size', 'Metric', 'Latency'])

custom_palette = {
    'Min': '#66C2A5',   
    'Max': '#FC8D62',   
    'Avg': '#8DA0CB'    
}

markers = ['o', 'x', 'v']

ordered_metrics = ['Max', 'Avg', 'Min']

ax = sns.boxplot(
    x='Summary Size', y='Latency',
    hue='Metric', data=df_long,
    dodge=False, palette=custom_palette, width=0.6, boxprops=dict(alpha=.66), linewidth=1.5, hue_order=ordered_metrics
)

for patch in ax.artists:
    patch.set_edgecolor('black')
    patch.set_linewidth(1)


box_legend_handles = [
    Patch(facecolor=custom_palette[metric], label=fr"$\textbf{{Box. {metric}}}$")
    for metric in ordered_metrics
]

line_legend_handles = [
    mlines.Line2D([], [], color=custom_palette[metric], linestyle='--',
                  marker=markers[ordered_metrics.index(metric)],
                  markersize=10, label=fr"$\textbf{{Avg. {metric}}}$")
    for metric in ordered_metrics
]

final_legend_handles = box_legend_handles + line_legend_handles

means = df_long.groupby(['Summary Size', 'Metric'])['Latency'].mean().reset_index()

summary_sizes_sorted = sorted(df_long['Summary Size'].unique())
dodge_shift = [0,0,0]

metrics = ordered_metrics

for i, metric in enumerate(metrics):
    metric_means = means[means['Metric'] == metric]
    x = [summary_sizes_sorted.index(size) + dodge_shift[i] for size in metric_means['Summary Size']]
    y = metric_means['Latency']
    
    ax.scatter(x, y, marker='o', color=custom_palette[metric])
    sns.lineplot(x=x, y=y, sort=False, ax=ax,
                 color=custom_palette[metric], linewidth=3, markersize=10)

line_styles = ['--', '--', '--']
for i, line in enumerate(ax.lines[-3:]):  #assuming 3 metrics (Avg, Min, Max)
    line.set_linestyle(line_styles[i])
    line.set_marker(markers[i])


plt.legend(
    handles=final_legend_handles,
    title=None,
    loc='upper left',
    bbox_to_anchor=(-0.005, 1.035),  
    ncols=2,                      
    framealpha=0.66,
    prop={'weight': 'bold', 'size': 20},
    columnspacing=0.4,            
    labelspacing=0.05,            
    handletextpad=0.3,             
    borderpad=0.1
)

plt.yscale("log")
plt.ylim(10**-7, 10**3)
plt.xlabel(r"Summary Sizes $|\mathcal{S}|$", fontsize=24)
plt.ylabel('Latency (s) Per Element', fontsize=24)
plt.title(r'\textsc{SuSe} Processing Latency per Element', fontsize=22, y=1.025)
plt.tick_params(axis='both', which='major', labelsize=23)
plt.tick_params(axis='x', which='major', labelsize=22)

ax.set_xticklabels([
    r"\textbf{50}", r"\textbf{100}", r"\textbf{250}",
    r"\textbf{500}", r"\textbf{1000}", r"\textbf{2500}",
    r"\textbf{5000}"
])

plt.setp( ax.xaxis.get_majorticklabels(), rotation=15 ) 

plt.grid()
plt.tight_layout()
plt.savefig('latency_boxplot.pdf', format='pdf')
plt.show()
