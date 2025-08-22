import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import seaborn as sns
from matplotlib.patches import PathPatch  
import matplotlib.patches as mpatches
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

def closest_number(n):
    candidates = [10, 25, 100, 200]
    return min(candidates, key=lambda x: abs(x - n))

df = pd.read_csv('report.csv')
df = df.sort_values(by=['Summary Size', 'Time Window Size'])

df['Number Evaluation Timestamps'] = df['Number Evaluation Timestamps'].apply(closest_number)
summary_size = 500
time_window_size= 100
alphabet_probability_distribution = "uniform"

plot_data = []

for num_of_evaluation_timestamp in df['Number Evaluation Timestamps'].unique():
    filtered_df = df[(df['Number Evaluation Timestamps'] == num_of_evaluation_timestamp) &
                     (df['Summary Size'] == summary_size) &
                     (df['Time Window Size'] == time_window_size) &
                     (df['Evaluation Timestamps Probability Distribution'] == "poisson") &
                     (df['Alphabet Probability Distribution'] == alphabet_probability_distribution)]

    for ratio_type, col_name in zip(['SuSe/Random', 'SuSe/FIFO'], ['Total Ratio SuSe/Random', 'Total Ratio SuSe/FIFO']):
        for val in filtered_df[col_name]:
            plot_data.append([num_of_evaluation_timestamp, val, ratio_type])

plot_df = pd.DataFrame(plot_data, columns=['Number Evaluation Timestamps', 'Ratio', 'Type'])

fig, ax = plt.subplots()
palette_used = "pastel"

colors = sns.color_palette("pastel", 2)
suse_random_color, suse_fifo_color = colors

sns.boxplot(data=plot_df, x='Number Evaluation Timestamps', y='Ratio', hue='Type', hue_order=['SuSe/Random', 'SuSe/FIFO'], ax=ax, palette=palette_used, legend=False, saturation=1)



boxes = [child for child in ax.get_children() if isinstance(child, PathPatch)]
for i, box in enumerate(boxes):
    hatch = '//' if i < 4 else '\\\\'
    box.set_hatch(hatch)
  


ax.axhline(y=1, color='k', linestyle='--', linewidth=3)
min_x = min(df['Number Evaluation Timestamps'].unique())
ax.text(x=-0.02, y=0.085, s='$10^0$', verticalalignment='bottom', horizontalalignment='right', fontsize=24, transform=ax.transAxes)
ax.set_ylim(10**-1,10**7)
ax.grid(True, linestyle='-')
leg = ax.legend(title=None, loc='upper right', bbox_to_anchor=(1, 1.025), fontsize='12', framealpha=0.1, prop={'weight':'bold', 'size':16}, ncol=2, columnspacing=3)
leg._legend_box.align = "right"

handles, labels = ax.get_legend_handles_labels()

new_labels = [rf"$\mathbf{{{lbl}}}$" for lbl in labels]

legend_handles = [
    mpatches.Patch(facecolor=suse_random_color, hatch='//', label=r'$\textbf{\textsc{SuSe}}\mathbf{/Random}$'),
    mpatches.Patch(facecolor=suse_fifo_color, hatch='\\\\', label=r'$\textbf{\textsc{SuSe}}\mathbf{/FIFO}$')
]
ax.legend(handles=legend_handles, prop={'weight': 'bold', 'size': 18}, loc='lower center', ncols=2, framealpha=0.66, bbox_to_anchor=(.5,-.025), borderpad=0.1)

ticks = [10, 25, 100, 200] 

bold_tick_labels = [rf"$\mathbf{{{int(t)}}}$" for t in ticks]
ax.set_xticklabels(bold_tick_labels)

ax.set_yscale('log')
ax.set_xlabel(r"\#Evaluation Timestamps $|\mathcal{E}|$", fontsize=24, labelpad=-1)
ax.set_ylabel('Rel. Recall Improvement', fontsize=24, labelpad=-5)
ax.set_title(r'Increasing \#Evaluation Timestamps $|\mathcal{E}|$', fontsize=21)
ax.tick_params(axis='both', which='major', labelsize=24)
ax.xaxis.label.set_position((.5, -0.9))
ax.yaxis.label.set_position((-0.15, .5))
plt.tight_layout()
plt.savefig('number_of_evaluation_timestamps_plot.pdf', format='pdf')
