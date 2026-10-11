"""Summarize streamed depths, including uncovered bases in the denominator."""
import argparse
import collections
import json
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--fai', required=True, type=Path)
parser.add_argument('--cutadapt', type=Path)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
genome = sum(int(line.split()[1]) for line in args.fai.read_text().splitlines())
covered = depth_sum = maximum = 0
histogram = collections.Counter()
for line in sys.stdin:
    depth = int(line.split()[2])
    if depth > 0:
        covered += 1
        histogram[depth] += 1
    depth_sum += depth
    maximum = max(maximum, depth)
histogram[0] += genome - covered
result = dict(genome_bases=genome, covered_bases=covered,
              covered_percent=100 * covered / genome,
              mean_depth_genome=depth_sum / genome,
              mean_depth_covered=depth_sum / covered if covered else 0,
              max_depth=maximum, mapping_quality_minimum=20,
              base_quality_minimum=0, overlaps_removed=False,
              depth_histogram=dict(sorted(histogram.items())))
if args.cutadapt:
    trim = json.loads(args.cutadapt.read_text())
    result.update(input_pairs=trim['read_counts']['input'], trimmed_pairs=trim['read_counts']['output'])
args.output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'depth_histogram'}, indent=2))
