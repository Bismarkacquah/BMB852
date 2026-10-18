"""Measure comparable reference coverage from the five real BAMs."""
import argparse
import csv
import json
import re
import subprocess
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--reference', type=Path, required=True)
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
total_length = sum(int(line.split('\t')[1]) for line in Path(str(a.reference)+'.fai').read_text().splitlines())
rows = []
for run in [f'ERR898218{i}' for i in range(3, 8)]:
    directory = root / f'samples/{run}'
    bam = directory / f'{run}.sorted.bam'
    flagstat = directory / 'flagstat.txt'
    if run == 'ERR8982185' and not bam.exists():
        bam = root.parent / 'Week-7/expanded/bam/ERR8982185.20M.sorted.bam'
        flagstat = root.parent / 'Week-7/expanded/results/flagstat.txt'
    output = root / f'results/{run}.coverage.tsv'
    with output.open('w') as handle:
        subprocess.run(['samtools', 'coverage', '-q', '20', '-Q', '0', str(bam)], stdout=handle, check=True)
    covered = weighted_depth = 0
    with output.open() as handle:
        for row in csv.DictReader(handle, delimiter='\t'):
            length = int(row['endpos'])-int(row['startpos'])+1
            covered += int(row['covbases'])
            weighted_depth += float(row['meandepth']) * length
    primary = mapped = None
    for line in flagstat.read_text().splitlines():
        match = re.match(r'(\d+) \+ (\d+) primary$', line)
        if match:
            primary = int(match[1])+int(match[2])
        match = re.match(r'(\d+) \+ (\d+) primary mapped ', line)
        if match:
            mapped = int(match[1])+int(match[2])
    rows.append(dict(sample=run, covered_bases=covered, reference_bases=total_length,
                     percent_reference_covered=100*covered/total_length,
                     genome_mean_depth=weighted_depth/total_length,
                     primary_alignment_records=primary, primary_mapped_records=mapped,
                     primary_mapped_percent=100*mapped/primary if primary else None))
with (root / 'results/coverage_comparison.tsv').open('w', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter='\t')
    writer.writeheader()
    writer.writerows(rows)
(root / 'results/coverage_comparison.json').write_text(json.dumps(dict(command='samtools coverage -q 20 -Q 0; full FASTA length as denominator', samples=rows), indent=2) + '\n')
print(json.dumps(rows, indent=2))
