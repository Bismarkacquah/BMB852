"""Exercise five-sample comparison and plotting on isolated synthetic fixtures."""
import gzip
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

source = Path(__file__).resolve().parent
runs = [f'ERR898218{i}' for i in range(3, 8)]
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    (root / 'scripts').mkdir()
    (root / 'results').mkdir()
    for name in ('analyze_multisample.py', 'summarize_effects.py', 'plot_comparisons.py'):
        shutil.copy2(source / name, root / 'scripts' / name)
    header = '##fileformat=VCFv4.2\n'
    columns = '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t'
    annotation = 'MQ=60;ANN=C|missense_variant|MODERATE|test_gene|test_gene|transcript|test_tx|protein_coding|1/1|c.1A>C|p.Met1Leu|||||'
    reference = root / 'reference.fa'
    reference.write_text('>CM000001.1\n' + 'A'*100 + '\n')
    subprocess.run(['samtools', 'faidx', str(reference)], check=True)

    def row(pos, genotypes):
        return f'CM000001.1\t{pos}\t.\tA\tC\t90\tPASS\t{annotation}\tGT:DP:AD\t' + '\t'.join(genotypes) + '\n'

    for i, run in enumerate(runs):
        target = root / f'samples/{run}/{run}.pass.vcf.gz'
        target.parent.mkdir(parents=True)
        with gzip.open(target, 'wt') as handle:
            handle.write(header + columns + run + '\n')
            shared = row(1, ['1:12:0,12'])
            if i == 0:
                shared = shared.replace('\tA\tC\t', '\ta\tc\t')
            handle.write(shared)
            handle.write(row(i+2, ['1:12:0,12']))
        sam = target.parent / 'fixture.sam'
        sequence = list('A'*100)
        sequence[0] = sequence[i+1] = 'C'
        sam.write_text('@HD\tVN:1.6\tSO:coordinate\n@SQ\tSN:CM000001.1\tLN:100\n' + ''.join(f'read{j}\t0\tCM000001.1\t1\t60\t100M\t*\t0\t0\t{"".join(sequence)}\t{"I"*100}\n' for j in range(12)))
        bam = target.parent / f'{run}.sorted.bam'
        subprocess.run(['samtools', 'view', '-b', '-o', str(bam), str(sam)], check=True)
        subprocess.run(['samtools', 'index', str(bam)], check=True)
    merged = header + columns + '\t'.join(runs) + '\n' + row(1, ['1:12:0,12']*5)
    for i in range(5):
        merged += row(i+2, ['1:12:0,12' if j == i else '.:.:.' for j in range(5)])
    for name in ('five_samples.vcf.gz', 'five_samples.annotated.vcf.gz'):
        with gzip.open(root / 'results' / name, 'wt') as handle:
            handle.write(merged)
    (root / 'results/merged_samples.txt').write_text('\n'.join(runs) + '\n')
    subprocess.run([sys.executable, 'scripts/summarize_effects.py', 'results/five_samples.annotated.vcf.gz'], cwd=root, stdout=subprocess.DEVNULL, check=True)
    subprocess.run([sys.executable, 'scripts/analyze_multisample.py', '--reference', str(reference)], cwd=root, stdout=subprocess.DEVNULL, check=True)
    comparison = json.loads((root / 'results/comparison_summary.json').read_text())
    assert comparison['union_records'] == 6 and comparison['observed_in_all_five'] == 1
    assert comparison['sample_genotypes_verified']
    subprocess.run([sys.executable, 'scripts/plot_comparisons.py'], cwd=root, check=True)
    assert len(list((root / 'png').glob('*.png'))) == 4
    # A fabricated reference call at a missing site must fail validation.
    invalid = merged.replace('.:.:.', '0:.:.', 1)
    with gzip.open(root / 'results/five_samples.vcf.gz', 'wt') as handle:
        handle.write(invalid)
    result = subprocess.run([sys.executable, 'scripts/analyze_multisample.py', '--reference', str(reference)], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert result.returncode != 0, 'Fabricated reference genotype was accepted'
print('PASS: five-sample comparisons, real plotting code, and rejection of imputed reference calls')
