"""Compare independent PASS calls, validate the merged union, and select IGV loci."""
import csv
import argparse
import gzip
import json
import subprocess
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
SAMPLES = [f'ERR898218{i}' for i in range(3, 8)]


def records(path):
    with gzip.open(path, 'rt') as handle:
        for line in handle:
            if line.startswith('#'):
                continue
            f = line.rstrip().split('\t')
            # The FASTA contains soft-masked bases; merge uppercases alleles.
            # Letter case is not a different biological allele.
            key = (f[0], int(f[1]), f[3].upper(), f[4].upper())
            yield key, f


def sample_data(f):
    fmt = dict(zip(f[8].split(':'), f[9].split(':')))
    depth = int(fmt['DP']) if fmt.get('DP', '.') != '.' else None
    ad = [int(v) for v in fmt.get('AD', '.').split(',')] if '.' not in fmt.get('AD', '.') else []
    info = dict(item.split('=', 1) for item in f[7].split(';') if '=' in item)
    return dict(qual=float(f[5]), dp=depth, ad=ad, gt=fmt.get('GT', '.'), mq=float(info.get('MQ', '0')))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, default=ROOT.parent / 'Week-5/fasta/GCA_000002425.2_Phypa_V3_genomic.fna')
    args = parser.parse_args()
    callsets, stats, distributions = {}, [], {}
    for run in SAMPLES:
        path = ROOT / f'samples/{run}/{run}.pass.vcf.gz'
        calls = {key: sample_data(f) for key, f in records(path)}
        callsets[run] = calls
        types = Counter('SNP' if len(k[2]) == len(k[3]) == 1 else 'indel' for k in calls)
        stats.append(dict(sample=run, pass_records=len(calls), snps=types['SNP'], indels=types['indel']))
        distributions[run] = dict(qual=[v['qual'] for v in calls.values()], depth=[v['dp'] for v in calls.values() if v['dp'] is not None])
    union = set().union(*(set(c) for c in callsets.values()))
    patterns = Counter()
    for key in union:
        patterns[''.join('1' if key in callsets[s] else '0' for s in SAMPLES)] += 1
    merged_path = RESULTS / 'five_samples.vcf.gz'
    assert (RESULTS / 'merged_samples.txt').read_text().splitlines() == SAMPLES, 'Unexpected merged sample order'
    merged_keys = set()
    merged_count = 0
    for key, fields in records(merged_path):
        merged_count += 1
        merged_keys.add(key)
        assert len(fields[9:]) == 5, 'Merged record does not have five samples'
        for run, value in zip(SAMPLES, fields[9:]):
            gt = dict(zip(fields[8].split(':'), value.split(':'))).get('GT', '.')
            if key in callsets[run]:
                assert gt == callsets[run][key]['gt'], (key, run, gt)
            else:
                assert all(a == '.' for a in gt.replace('|', '/').split('/')), (key, run, gt)
    assert merged_keys == union and merged_count == len(union), 'Merged alleles differ from independent input union'
    with (RESULTS / 'sample_comparison.tsv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['sample', 'pass_records', 'snps', 'indels'], delimiter='\t')
        writer.writeheader()
        writer.writerows(stats)
    summary = dict(samples=SAMPLES, union_records=len(union), merged_records=merged_count,
                   union_snp_records=sum(len(k[2]) == len(k[3]) == 1 for k in union),
                   union_indel_records=sum(not (len(k[2]) == len(k[3]) == 1) for k in union),
                   exact_union_verified=True, sample_genotypes_verified=True,
                   allele_identity='CHROM, POS, REF.upper(), ALT.upper(); soft-mask letter case is ignored',
                   observed_in_all_five=patterns['11111'], presence_patterns=dict(patterns),
                   sample_counts=stats, interpretation='Presence means retained in a sample PASS VCF; absence is not a reference genotype.')
    (RESULTS / 'comparison_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (RESULTS / 'plot_data.json').write_text(json.dumps(dict(distributions=distributions), separators=(',', ':')) + '\n')

    # Select supported, moderate-depth examples rather than extreme pileups.
    candidates = []
    rank = {'HIGH': 0, 'MODERATE': 1, 'LOW': 2, 'MODIFIER': 3}
    for key, f in records(RESULTS / 'five_samples.annotated.vcf.gz'):
        if not key[0].startswith('CM') or ',' in key[3] or max(len(key[2]), len(key[3])) > 12:
            continue
        supported = []
        for run in SAMPLES:
            value = callsets[run].get(key)
            if value and value['dp'] is not None and 8 <= value['dp'] <= 60 and value['qual'] >= 50 and value['mq'] >= 50 and value['ad']:
                alternate = sum(value['ad'][1:])
                if alternate >= 8 and alternate / max(sum(value['ad']), 1) >= 0.8:
                    supported.append(run)
        if not supported:
            continue
        info = dict(item.split('=', 1) for item in f[7].split(';') if '=' in item)
        annotations = [ann.split('|') for ann in info.get('ANN', '').split(',') if ann]
        if any(len(ann) != 16 for ann in annotations):
            raise ValueError(f'ANN field alignment is invalid at {key}')
        annotations = [ann for ann in annotations if ann[7] == 'protein_coding']
        if not annotations:
            continue
        ann = min(annotations, key=lambda a: (rank.get(a[2], 9), bool(a[15] if len(a) > 15 else '')))
        ann += [''] * max(0, 16 - len(ann))
        candidates.append(dict(chrom=key[0], pos=key[1], ref=key[2], alt=key[3], effect=ann[1], impact=ann[2], gene=ann[3],
                               transcript=unquote(ann[6]), hgvs_c=ann[9], hgvs_p=ann[10], warning=ann[15],
                               type='SNP' if len(key[2]) == len(key[3]) == 1 else 'indel', supported_samples=supported,
                               calls={s: callsets[s].get(key) for s in SAMPLES}))
    candidates.sort(key=lambda c: (bool(c['warning']), rank.get(c['impact'], 9), -len(c['supported_samples']), c['chrom'], c['pos']))
    selected = []
    bams = [ROOT / f'samples/{s}/{s}.sorted.bam' for s in SAMPLES]
    if not bams[2].exists():
        bams[2] = ROOT.parent / 'Week-7/expanded/bam/ERR8982185.20M.sorted.bam'
    reviewed = {}

    def suitable_read_view(candidate):
        key = (candidate['chrom'], candidate['pos'])
        if key in reviewed:
            return reviewed[key]
        chrom, pos = key
        window = f'{chrom}:{max(1, pos-40)}-{pos+40}'
        sequence = subprocess.check_output(['samtools', 'faidx', str(args.reference), window], text=True)
        if 'N' in ''.join(sequence.splitlines()[1:]).upper():
            reviewed[key] = False
            return False
        depth = subprocess.check_output(['samtools', 'depth', '-r', f'{chrom}:{pos}-{pos}', *map(str, bams)], text=True)
        values = [int(v) for v in depth.rstrip().split('\t')[2:]] if depth.strip() else [0]*5
        assert len(values) == 5
        candidate['unfiltered_depth_by_sample'] = dict(zip(SAMPLES, values))
        reviewed[key] = max(values) <= 100 and max(values) >= 12
        return reviewed[key]

    # Match the Week 7 evidence gallery: one indel and two distinct SNPs.
    # Prefer a HIGH indel and a MODERATE SNP among warning-free predictions.
    for variant_type, preferred_impact in (('indel', 'HIGH'), ('SNP', 'MODERATE'), ('SNP', 'synonymous_variant')):
        pool = [c for c in candidates if c['type'] == variant_type and
                (c['chrom'], c['pos']) not in {(s['chrom'], s['pos']) for s in selected}]
        clean = [c for c in pool if not c['warning']]
        pool = clean or pool
        separated = [c for c in pool if all(c['chrom'] != s['chrom'] or abs(c['pos']-s['pos']) > 500 for s in selected)]
        pool = separated or pool
        if preferred_impact:
            pool = sorted(pool, key=lambda c: preferred_impact not in (c['impact'], *c['effect'].split('&')))
        for candidate in pool:
            if suitable_read_view(candidate):
                selected.append(candidate)
                break
    if not selected:
        raise RuntimeError('No variants met the documented IGV selection criteria')
    (RESULTS / 'igv_selected_variants.json').write_text(json.dumps(selected, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
