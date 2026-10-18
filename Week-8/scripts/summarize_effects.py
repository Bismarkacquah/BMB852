"""Summarize SnpEff annotations and retain per-sample missing calls."""
import argparse
import csv
import gzip
import json
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('vcf', type=Path)
    parser.add_argument('--output', type=Path, default=Path('results'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    impacts, effects, warnings = Counter(), Counter(), Counter()
    samples, sample_counts = [], {}
    records = annotated = 0
    rank = {'HIGH': 0, 'MODERATE': 1, 'LOW': 2, 'MODIFIER': 3}
    candidates = []
    high_biotypes = Counter()
    with gzip.open(args.vcf, 'rt') as handle, (args.output / 'variant_effects.tsv').open('w', newline='') as out:
        writer = csv.writer(out, delimiter='\t')
        writer.writerow(['chrom', 'pos', 'ref', 'alt', 'effect', 'impact', 'gene', 'gene_id', 'transcript', 'hgvs_c', 'hgvs_p', 'annotation_warnings', 'sample_genotypes'])
        for line in handle:
            if line.startswith('#CHROM'):
                samples = line.rstrip().split('\t')[9:]
                if len(samples) != 5 or len(set(samples)) != 5:
                    raise ValueError('Expected five distinct samples')
                sample_counts = {s: Counter() for s in samples}
            if line.startswith('#'):
                continue
            fields = line.rstrip().split('\t')
            records += 1
            fmt = fields[8].split(':')
            genotypes = []
            for sample, value in zip(samples, fields[9:]):
                gt = dict(zip(fmt, value.split(':'))).get('GT', '.')
                alleles = gt.replace('|', '/').split('/')
                category = 'missing' if '.' in alleles else ('nonreference' if any(a != '0' for a in alleles) else 'reference')
                sample_counts[sample][category] += 1
                genotypes.append(f'{sample}={gt}')
            info = dict(item.split('=', 1) for item in fields[7].split(';') if '=' in item)
            annotations = [entry.split('|') for entry in info.get('ANN', '').split(',') if entry]
            if any(len(ann) != 16 for ann in annotations):
                raise ValueError(f'ANN does not contain 16 fields at {fields[0]}:{fields[1]}')
            if not annotations:
                continue
            annotated += 1
            high_types = {ann[7] for ann in annotations if ann[2] == 'HIGH'}
            high_biotypes.update(high_types)
            # One most severe impact per record; effect counts include all transcripts.
            best = min(annotations, key=lambda a: rank.get(a[2], 9))
            impacts[best[2]] += 1
            for ann in annotations:
                ann += [''] * max(0, 16 - len(ann))
                effects.update(ann[1].split('&'))
                if ann[15]:
                    warnings.update(ann[15].split('&'))
                row = fields[:2] + fields[3:5] + [ann[1], ann[2], ann[3], ann[4], ann[6], ann[9], ann[10], ann[15], ';'.join(genotypes)]
                writer.writerow(row)
                if ann[2] in ('HIGH', 'MODERATE'):
                    candidates.append(row)
    summary = dict(records=records, annotated_records=annotated, unannotated_records=records-annotated, samples=samples,
                   per_record_most_severe_impact=dict(impacts), all_transcript_effect_counts=dict(effects),
                   annotation_warnings=dict(warnings), per_sample_site_counts={s: dict(c) for s, c in sample_counts.items()},
                   high_impact_records_by_biotype=dict(high_biotypes),
                   interpretation='Missing genotypes are unknown, not reference. Impacts are computational predictions. Transcript effect totals can exceed variant record counts.')
    (args.output / 'effect_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    report = ['# Five-sample variant-effect results', '',
              f'Merged records: **{records:,}**. Records with SnpEff annotations: **{annotated:,}**.', '',
              '## Most severe predicted impact per record', '', '| Impact | Records |', '|---|---:|']
    report.extend(f'| {impact} | {impacts[impact]:,} |' for impact in ('HIGH', 'MODERATE', 'LOW', 'MODIFIER'))
    report += ['', '## Sample calls at merged variant sites', '', '| Sample | Nonreference | Reference | Missing |', '|---|---:|---:|---:|']
    report.extend(f'| {s} | {sample_counts[s]["nonreference"]:,} | {sample_counts[s]["reference"]:,} | {sample_counts[s]["missing"]:,} |' for s in samples)
    report += ['', 'Missing means not called in that sample, not confirmed reference. These are independently called, PASS-only VCFs, so this table cannot establish absence of a variant or treatment-specific effects.', '',
               'See [effect candidates](effect_candidates.tsv) and [all transcript effects](variant_effects.tsv). Inspect read evidence before interpreting candidates. The custom database was built without independent CDS/protein sequence validation; annotation warnings must be reviewed.', '']
    (args.output / 'analysis_report.md').write_text('\n'.join(report))
    candidates.sort(key=lambda r: (rank.get(r[5], 9), bool(r[11]), r[0], int(r[1])))
    with (args.output / 'effect_candidates.tsv').open('w', newline='') as out:
        writer = csv.writer(out, delimiter='\t')
        writer.writerow(['chrom', 'pos', 'ref', 'alt', 'effect', 'impact', 'gene', 'gene_id', 'transcript', 'hgvs_c', 'hgvs_p', 'annotation_warnings', 'sample_genotypes'])
        seen = set()
        for row in candidates:
            key = tuple(row[:4])
            if key not in seen:
                writer.writerow(row)
                seen.add(key)
            if len(seen) == 30:
                break
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
