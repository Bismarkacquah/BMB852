"""Plot measured counts, distributions, impacts, and observed PASS-call overlap."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / 'results'
OUT = ROOT / 'png'
OUT.mkdir(exist_ok=True)
summary = json.loads((R / 'comparison_summary.json').read_text())
effects = json.loads((R / 'effect_summary.json').read_text())
data = json.loads((R / 'plot_data.json').read_text())['distributions']
samples = summary['samples']
labels = ['Control#1', 'Control#2', 'CRIS1#1\nWeek 7', 'CRIS1#2', 'CRIS2#1']
palette = ['#136F8A', '#208EA0', '#E59B30', '#CB6C32', '#8B64A7']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': '#FFFFFF', 'axes.labelcolor': '#243746', 'text.color': '#243746', 'axes.titleweight': 'bold', 'savefig.dpi': 180})


def save(fig, name):
    fig.savefig(OUT / name, bbox_inches='tight')
    plt.close(fig)


fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(5)
snps = [row['snps'] for row in summary['sample_counts']]
indels = [row['indels'] for row in summary['sample_counts']]
ax.bar(x, snps, label='SNP records', color='#136F8A')
ax.bar(x, indels, bottom=snps, label='Indel records', color='#E59B30')
for i, total in enumerate(np.array(snps) + np.array(indels)):
    ax.text(i, total, f'{total:,}', ha='center', va='bottom', fontsize=10)
ax.set(xticks=x, xticklabels=labels, ylabel='PASS variant records', title='Independent calls against the same moss reference')
ax.margins(y=0.18)
ax.legend(frameon=False, loc='upper left')
save(fig, '01_sample_variant_counts.png')

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
axes[0].boxplot([data[s]['depth'] for s in samples], showfliers=False, tick_labels=labels)
axes[0].set(title='Usable depth at PASS sites', ylabel='FORMAT/DP (outliers hidden)')
axes[1].boxplot([data[s]['qual'] for s in samples], showfliers=False, tick_labels=labels)
axes[1].set(title='Variant quality at PASS sites', ylabel='QUAL (outliers hidden)')
for ax in axes:
    ax.tick_params(axis='x', labelsize=9)
    ax.grid(axis='y', alpha=0.15)
save(fig, '02_quality_depth.png')

fig, ax = plt.subplots(figsize=(8, 4.5))
order = ['HIGH', 'MODERATE', 'LOW', 'MODIFIER']
counts = [effects['per_record_most_severe_impact'].get(k, 0) for k in order]
ax.barh(order[::-1], counts[::-1], color=['#82A8AD', '#5C8AA5', '#E59B30', '#BB4B45'])
for i, value in enumerate(counts[::-1]):
    ax.text(value, i, f'  {value:,}', va='center')
ax.set(xlabel='Merged variant records', title='Most severe predicted impact per record')
ax.margins(x=0.2)
save(fig, '03_predicted_impacts.png')

patterns = sorted(summary['presence_patterns'].items(), key=lambda item: (-item[1], item[0]))[:12]
fig, (top, bottom) = plt.subplots(2, 1, figsize=(12, 6), gridspec_kw={'height_ratios': [3, 1.7]}, sharex=True)
top.bar(range(len(patterns)), [c for _, c in patterns], color='#136F8A')
top.set(ylabel='Variant records', title='Observed overlap among independent PASS callsets')
for j, (_, count) in enumerate(patterns):
    top.text(j, count, f'{count:,}', ha='center', va='bottom', fontsize=8)
for j, (pattern, _) in enumerate(patterns):
    for i, value in enumerate(pattern):
        bottom.scatter(j, i, color=palette[i] if value == '1' else '#DDE3E8', s=75)
bottom.set(yticks=range(5), yticklabels=[s.replace('\n', ' ') for s in labels], xticks=[], xlabel='Colored dot = a retained PASS call; gray = no retained call, not confirmed reference')
bottom.invert_yaxis()
bottom.spines[['left', 'bottom']].set_visible(False)
top.margins(y=0.15)
save(fig, '04_observed_call_overlap.png')
print('Generated four comparison figures from completed VCFs')
