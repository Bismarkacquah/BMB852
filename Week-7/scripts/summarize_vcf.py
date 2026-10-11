"""Summarize observed VCF records without additional dependencies."""
import argparse
import collections
import gzip
import json
from pathlib import Path


def summarize(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    counts = collections.Counter()
    filters = collections.Counter()
    depths, qualities, samples, top = [], [], [], []
    with opener(path, 'rt') as handle:
        for line in handle:
            if line.startswith('#CHROM'):
                samples = line.rstrip().split('\t')[9:]
            if line.startswith('#'):
                continue
            fields = line.rstrip().split('\t')
            chrom, pos, _, ref, alt, qual, filt = fields[:7]
            alts = alt.split(',')
            counts['records'] += 1
            if all(len(ref) == len(a) == 1 for a in alts):
                counts['snp_records'] += 1
            elif any(len(ref) != len(a) for a in alts):
                counts['indel_records'] += 1
            else:
                counts['other_records'] += 1
            filters[filt] += 1
            fmt = dict(zip(fields[8].split(':'), fields[9].split(':')))
            depth = int(fmt['DP']) if fmt.get('DP', '.') != '.' else None
            quality = float(qual) if qual != '.' else None
            if depth is not None:
                depths.append(depth)
            if quality is not None:
                qualities.append(quality)
            top.append(dict(chrom=chrom, pos=int(pos), ref=ref, alt=alt,
                            qual=quality, filter=filt, dp=depth,
                            gt=fmt.get('GT'), ad=fmt.get('AD')))
    top.sort(key=lambda r: r['qual'] if r['qual'] is not None else -1, reverse=True)
    return dict(path=str(path), samples=samples,
                records=counts['records'], snp_records=counts['snp_records'],
                indel_records=counts['indel_records'], other_records=counts['other_records'],
                filters=dict(filters),
                min_dp=min(depths, default=None), max_dp=max(depths, default=None),
                mean_dp=sum(depths) / len(depths) if depths else None,
                min_qual=min(qualities, default=None), max_qual=max(qualities, default=None),
                top_calls=top[:10])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('vcfs', nargs='+', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps([summarize(p) for p in args.vcfs], indent=2) + '\n')
