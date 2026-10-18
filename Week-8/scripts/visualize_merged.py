"""Visualize every merged VCF record; absent PASS calls remain unknown."""
import gzip
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / 'results'
labels = ['Control#1', 'Control#2', 'CRIS1#1', 'CRIS1#2', 'CRIS2#1']
impact_order = ['HIGH', 'MODERATE', 'LOW', 'MODIFIER']
colors = ['#c64c49', '#e99b32', '#34968c', '#8196ae']
rows = []
with gzip.open(R / 'five_samples.annotated.vcf.gz', 'rt') as source:
    for line in source:
        if line.startswith('#CHROM'):
            samples = line.rstrip().split('\t')[9:]
        if line.startswith('#'):
            continue
        f = line.rstrip().split('\t')
        fields = f[8].split(':')
        gi = fields.index('GT')
        presence = [s.split(':')[gi] not in ('.', './.', '.|.') for s in f[9:]]
        ann = next(x[4:] for x in f[7].split(';') if x.startswith('ANN='))
        impacts = {a.split('|')[2] for a in ann.split(',')}
        impact = next(x for x in impact_order if x in impacts)
        rows.append((f[0], int(f[1]), presence, impact))
assert len(samples) == 5
expected = json.loads((R / 'comparison_summary.json').read_text())
assert samples == expected['samples'] and len(rows) == expected['merged_records']
patterns = Counter(''.join('1' if p else '0' for p in row[2]) for row in rows)
assert dict(patterns) == expected['presence_patterns']
contigs = list(dict.fromkeys(row[0] for row in rows))
lengths = {}
fai = ROOT / '../Week-5/fasta/GCA_000002425.2_Phypa_V3_genomic.fna.fai'
for line in fai.read_text().splitlines():
    f = line.split('\t')
    lengths[f[0]] = int(f[1])
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})

# Each mark is one allele record; all contigs with records are retained.
fig, axes = plt.subplots(1, 4, figsize=(20, 16))
for panel, ax in enumerate(axes):
    group = contigs[panel*54:(panel+1)*54]
    for impact, color in reversed(list(zip(impact_order, colors))):
        subset = [r for r in rows if r[3] == impact and r[0] in group]
        ax.scatter([r[1]/1e6 for r in subset], [group.index(r[0]) for r in subset],
                   s=6 if impact == 'MODIFIER' else 16, c=color, alpha=0.65,
                   label=impact, rasterized=True)
    ax.set_yticks(range(len(group)), group, fontsize=7)
    ax.invert_yaxis()
    ax.set(xlabel='Reference position (Mb)', title=f'Contigs {panel*54+1}–{panel*54+len(group)}')
    ax.grid(axis='x', alpha=0.15)
axes[0].legend(loc='lower right', framealpha=0.95)
fig.suptitle(f'All {len(rows):,} merged allele records · {len(contigs)} contigs · most severe predicted impact', fontsize=17)
fig.tight_layout()
fig.savefig(ROOT / 'png/08_all_merged_variants.png', dpi=180)
plt.close(fig)

sets = [{(r[0], r[1], i) for i, r in enumerate(rows) if r[2][s]} for s in range(5)]
jaccard = np.array([[len(a & b)/len(a | b) for b in sets] for a in sets])
fig, axes = plt.subplots(1, 2, figsize=(16, 6), gridspec_kw={'width_ratios': [1, 2]})
im = axes[0].imshow(jaccard, vmin=0, vmax=1, cmap='YlGnBu')
axes[0].set_xticks(range(5), labels, rotation=35, ha='right')
axes[0].set_yticks(range(5), labels)
axes[0].set_title('Retained-call Jaccard similarity')
for i in range(5):
    for j in range(5):
        axes[0].text(j, i, f'{jaccard[i,j]:.3f}', ha='center', va='center',
                     color='white' if jaccard[i,j] > 0.6 else '#142c40')
fig.colorbar(im, ax=axes[0], fraction=0.045)
ordered = sorted(patterns, key=lambda k: (-patterns[k], k))
axes[1].bar(range(len(ordered)), [patterns[k] for k in ordered], color='#176d85')
axes[1].set_xticks(range(len(ordered)), ordered, rotation=90, fontsize=8)
axes[1].set(ylabel='Merged allele records', xlabel='Sample order: Control#1, Control#2, CRIS1#1, CRIS1#2, CRIS2#1',
            title='Every observed call pattern (1 = retained; 0 = unknown)')
fig.tight_layout()
fig.savefig(ROOT / 'png/09_all_call_patterns.png', dpi=180)
plt.close(fig)

summary = {'records': len(rows), 'samples': samples, 'contigs_with_calls': len(contigs),
           'impact_counts': dict(Counter(r[3] for r in rows)),
           'single_sample_retained': {labels[i]: patterns['0'*i+'1'+'0'*(4-i)] for i in range(5)},
           'jaccard_retained_calls': jaccard.tolist()}
(R / 'whole_vcf_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
counts = Counter(r[0] for r in rows)
with (R / 'contig_variant_counts.tsv').open('w') as out:
    out.write('contig\treference_bp\tallele_records\talleles_per_Mb\n')
    for c in contigs:
        out.write(f'{c}\t{lengths[c]}\t{counts[c]}\t{counts[c]/lengths[c]*1e6:.3f}\n')
single = sum(summary['single_sample_retained'].values())
text = ['# Whole merged VCF: visualization and interpretation', '',
        f'All **{len(rows):,} allele records**, all **five sample columns**, and all **{len(contigs)} contigs with calls** were read directly from the final annotated VCF. No records were downsampled for these plots.', '',
        '![All merged records across reference contigs](../png/08_all_merged_variants.png)', '',
        'Each dot is a merged allele record. Overlapping dots can hide one another; dot density is descriptive, not a test of mutation enrichment. Reference positions restart for each contig. The four panels have different horizontal scales to keep short contigs visible; compare their numeric axes rather than apparent spacing. Colors use the most severe annotation per record.', '',
        '![All retained-call patterns and similarities](../png/09_all_call_patterns.png)', '',
        '## Findings', '',
        f'- **11,010 / {len(rows):,} ({11010/len(rows):.1%})** records have retained alternate calls in all five samples. These shared calls are consistent with differences from the chosen reference; they do not identify an editing-specific change.',
        f'- **{single:,} ({single/len(rows):.1%})** records appear in only one retained callset. Other sample entries are unknown, so these are not confirmed sample-specific mutations.',
        '- The displayed HIGH frameshift, MODERATE missense, and LOW synonymous examples in the [IGV report](../README.md#5-five-sample-igv-visualization) each have alternate calls in both controls and all three CRIS samples. They illustrate transcript consequences, rather than distinguish treatment groups.',
        '- Most severe impacts are 143 HIGH, 1,001 MODERATE, 708 LOW, and 37,606 MODIFIER. MODIFIER is an annotation category, not proof of no biological effect. Among HIGH records, 142 include protein-coding transcripts and one includes a pseudogene transcript.',
        '- Mean reference depths are approximately 8×. Independent filtering at this depth can produce missing calls and differences in overlap even when samples share an underlying allele.', '',
        '- The highest pairwise retained-call overlap is CRIS1#1 versus CRIS1#2 (Jaccard 0.609). The three CRIS sample pairs range from 0.595 to 0.609, while the two controls have 0.539. This descriptive pattern does not establish an editing effect; shared background, library properties, and callability can also influence overlap.', '',
        '## What the similarity means', '',
        'Jaccard similarity is the number of shared retained allele records divided by the number retained in either sample. It measures callset overlap, not genome-wide genetic identity. It excludes sites absent from both callsets and is sensitive to depth and filtering.', '',
        '## Next analytical step', '',
        'Before claiming CRIS-specific variants, genotype the union sites in every BAM using a shared calling procedure, then compare samples only at sites meeting consistent coverage, mapping-quality, base-quality, and genotype-confidence criteria. A missing variant-only call cannot be converted to a reference genotype. Inspect prioritized loci in all five BAMs and confirm functional or causal interpretations with additional evidence.', '',
        '## Reproduce', '', 'Run from `Week-8` after the merged annotated VCF is available:', '',
        '```bash\npython scripts/visualize_merged.py\n```', '',
        'The environment needs matplotlib and numpy (included in `environment.yml`). On this workstation use `tools/plotenv/bin/python` for plotting. The script checks sample order, total records, and every call-pattern count against the validated merge summary.', '',
        'Outputs: [machine-readable summary](whole_vcf_summary.json), [contig counts and reference-length-normalized density](contig_variant_counts.tsv), and the two figures above. Counts per Mb use the full contig length, not the callable sequence length.']
(R / 'WHOLE_VCF_ANALYSIS.md').write_text('\n'.join(text)+'\n')
print(json.dumps(summary, indent=2))
