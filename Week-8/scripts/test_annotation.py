"""Smoke-test database loading and summary generation using synthetic genotypes."""
import gzip
import json
import subprocess
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    fixture = root / 'fixture.vcf'
    with gzip.open('../Week-7/expanded/results/ERR8982185.20M.pass.vcf.gz', 'rt') as source, fixture.open('w') as out:
        for line in source:
            if line.startswith('#CHROM'):
                out.write('\t'.join(line.rstrip().split('\t')[:9] + ['test1', 'test2', 'test3', 'test4', 'test5']) + '\n')
            elif line.startswith('#'):
                out.write(line)
            else:
                fields = line.rstrip().split('\t')
                fields[8:] = ['GT', '1', '.', '.', '.', '.']
                out.write('\t'.join(fields) + '\n')
                break
    annotated = root / 'annotated.vcf'
    with annotated.open('w') as out:
        subprocess.run(['java', '-Xmx2g', '-jar', 'tools/snpEff/snpEff.jar', '-c', 'annotation/snpEff.config', '-dataDir', str(Path('annotation/data').resolve()), '-noDownload', '-noStats', 'Phypa_V3', str(fixture)], stdout=out, check=True)
    compressed = root / 'annotated.vcf.gz'
    with annotated.open('rb') as source, gzip.open(compressed, 'wb') as out:
        out.write(source.read())
    subprocess.run(['python3', 'scripts/summarize_effects.py', str(compressed), '--output', str(root / 'results')], stdout=subprocess.DEVNULL, check=True)
    summary = json.loads((root / 'results/effect_summary.json').read_text())
    assert summary['records'] == summary['annotated_records'] == 1, summary
    assert summary['per_sample_site_counts']['test1']['nonreference'] == 1
    assert all(summary['per_sample_site_counts'][s]['missing'] == 1 for s in ('test2', 'test3', 'test4', 'test5'))
    assert (root / 'results/analysis_report.md').is_file()
print('PASS: custom database annotation and five-sample effect summaries')
