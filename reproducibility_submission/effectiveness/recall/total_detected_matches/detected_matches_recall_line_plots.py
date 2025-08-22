import pandas as pd
import seaborn as sns
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

df = pd.read_csv('report_suse.csv')
df2 = pd.read_csv('report_suse_wo_expected.csv')

def get_ratios(df, unique_summary_sizes, unique_time_windows):
    data_for_plot = []
    stream_size = 2000
    for summary_size in unique_summary_sizes:
        for time_window in unique_time_windows:
            suse_results = df[(df['stream_size'] == stream_size) & (df['Summary Size'] == summary_size) & (df['Time Window Size'] == time_window) & (df['Alphabet Probability Distribution'] == 'uniform')]
            optimal_results = df[(df['stream_size'] == stream_size) & (df['Summary Size'] == 2000) & (df['Time Window Size'] == time_window) & (df['Alphabet Probability Distribution'] == 'uniform')]

            ratios = []
            for _, row in suse_results.iterrows():
                random_seed = row['Random Seed']
                matching_rows = optimal_results[optimal_results['Random Seed'] == random_seed]
                if not matching_rows.empty:
                    ratio = int(row['SuSe Total Detected Matches']) / int(matching_rows.iloc[0]['SuSe Total Detected Matches'])
                    ratios.append(ratio)

            for ratio in ratios:
                data_for_plot.append([summary_size, ratio, time_window, 'zipf'])
    return data_for_plot

unique_summary_sizes = [size for size in df['Summary Size'].unique() if size < 750]
unique_time_windows = [size for size in df['Time Window Size'].unique() if size <= 500 and size > 50]


data1 = get_ratios(df, unique_summary_sizes, unique_time_windows)
data2 = get_ratios(df2, unique_summary_sizes, unique_time_windows)

df_for_plot1 = pd.DataFrame(data1, columns=['Summary Size', 'Ratio', 'Time Window Size', 'Alphabet Probability Distribution'])
df_for_plot2 = pd.DataFrame(data2, columns=['Summary Size', 'Ratio', 'Time Window Size', 'Alphabet Probability Distribution'])

mean_ratios1 = df_for_plot1.groupby(['Summary Size', 'Time Window Size', 'Alphabet Probability Distribution'])['Ratio'].mean().reset_index()
mean_ratios2 = df_for_plot2.groupby(['Summary Size', 'Time Window Size', 'Alphabet Probability Distribution'])['Ratio'].mean().reset_index()

fig, ax = plt.subplots()
markers = ['o', 'v', '^', '<', '>', 's', '.', 'p']
line_styles = ['-', '--']  
colors = colors = ['#FFB347', '#77DD77', '#AEC6CF', '#F49AC2', '#AEDFF7', '#B19CD9']
tw_color_map = {100: colors[0], 250: colors[1], 500: colors[2]}  # pin exact colors for these windows
for idx, time_window in enumerate(unique_time_windows):
    subset1 = mean_ratios1[mean_ratios1['Time Window Size'] == time_window]
    subset2 = mean_ratios2[mean_ratios2['Time Window Size'] == time_window]
    c = tw_color_map.get(int(time_window), colors[idx % len(colors)]) 
    
    sns.lineplot(x='Summary Size', y='Ratio', data=subset1, ax=ax,
                 label=fr"$\boldsymbol{{\mathcal{{B}}}}; \boldsymbol{{q_{{\tau}}}}$: \textbf{{{time_window}}}",
                 linestyle=line_styles[0],
                 marker=markers[idx], color=c,
                 linewidth=3, markersize=15)
    
    sns.lineplot(x='Summary Size', y='Ratio', data=subset2, ax=ax,
                 label=fr"$\boldsymbol{{\mathcal{{B}}_{{\boldsymbol{{\mathrm{{pres}}}}}}}}; \boldsymbol{{q_{{\tau}}}}$: \textbf{{{time_window}}}",
                 linestyle=line_styles[1],
                 marker=markers[idx], color=c,
                 linewidth=3, markersize=15)


sns.set_palette("pastel")

query = df['Query'].iloc[0]
stream_size = 2000
alphabet_prob = 'uniform'

ax.set_xticks([100, 250, 500])
ax.set_xlabel(r"Summary Sizes $|\mathcal{S}|$", fontsize=24)
plt.ylabel('Detected Matches Recall', fontsize=24)
plt.title('Detected Matches Recall', fontsize=24)

handles, labels = ax.get_legend_handles_labels()
ax.set_ylim(-0.1,1.1)
new_labels = labels

ax.legend(handles=handles, labels=new_labels, loc='lower right', ncol=1, columnspacing=0.4, bbox_to_anchor=(.94, 0.1), framealpha=0.1 , prop={'weight':'bold', 'size':18})

plt.tick_params(axis='both', which='major', labelsize=23)

plt.grid()
plt.tight_layout()
plt.savefig('detected_matches_recall_stream_size_2000.pdf', format='pdf')
