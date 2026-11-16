"""Verify that ANN formatting changes leave all variants and sample fields intact."""
import gzip
from itertools import zip_longest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
before = root / 'results/five_samples.annotated.vcf.gz'
after = root / 'results/five_samples.annotated.fixed.vcf.gz'


def rows(path):
    with gzip.open(path, 'rt') as handle:
        for line in handle:
            if not line.startswith('#'):
                yield line.rstrip().split('\t')


count = 0
for old, new in zip_longest(rows(before), rows(after)):
    assert old is not None and new is not None, 'Record count changed'
    assert old[:7] == new[:7] and old[8:] == new[8:], 'Variant or sample fields changed'
    old_info = [item for item in old[7].split(';') if not item.startswith('ANN=')]
    new_info = [item for item in new[7].split(';') if not item.startswith('ANN=')]
    assert old_info == new_info, 'Non-ANN INFO fields changed'
    entries = next(item[4:] for item in new[7].split(';') if item.startswith('ANN=')).split(',')
    assert all(len(entry.split('|')) == 16 for entry in entries)
    count += 1
assert count == 39458, count
print(f'PASS: all {count:,} records and five-sample fields unchanged; all ANN entries have 16 fields')
