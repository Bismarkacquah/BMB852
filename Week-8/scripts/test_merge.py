"""Check that merge retains five sample IDs, the allele union, and missing calls."""
import subprocess
import tempfile
from pathlib import Path

header = '##fileformat=VCFv4.2\n##contig=<ID=chr1,length=100>\n##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n'
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    inputs = []
    for i in range(5):
        source = root / f's{i}.vcf'
        source.write_text(header + f'#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\ts{i}\nchr1\t{i+1}\t.\tA\tT\t40\tPASS\t.\tGT\t1\n')
        target = Path(str(source) + '.gz')
        subprocess.run(['bcftools', 'view', '-Oz', '-o', str(target), str(source)], check=True)
        subprocess.run(['bcftools', 'index', str(target)], check=True)
        inputs.append(str(target))
    merged = root / 'merged.vcf.gz'
    subprocess.run(['bcftools', 'merge', '-m', 'none', '-Oz', '-o', str(merged), *inputs], check=True)
    samples = subprocess.check_output(['bcftools', 'query', '-l', str(merged)], text=True).splitlines()
    assert samples == ['s0', 's1', 's2', 's3', 's4'], samples
    rows = subprocess.check_output(['bcftools', 'query', '-f', '%POS[\t%GT]\n', str(merged)], text=True).splitlines()
    assert len(rows) == 5, rows
    for i, line in enumerate(rows):
        values = line.split('\t')
        assert values[0] == str(i + 1), values
        assert values[1:] == ['1' if j == i else '.' for j in range(5)], values
    # Different ALT alleles at one coordinate must remain separate with -m none.
    for i, alt in enumerate(('C', 'G')):
        source = root / f's{i}.vcf'
        source.write_text(header + f'#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\ts{i}\nchr1\t1\t.\tA\t{alt}\t40\tPASS\t.\tGT\t1\n')
        subprocess.run(['bcftools', 'view', '-Oz', '-o', inputs[i], str(source)], check=True)
        subprocess.run(['bcftools', 'index', '-f', inputs[i]], check=True)
    subprocess.run(['bcftools', 'merge', '-m', 'none', '-Oz', '-o', str(merged), *inputs], check=True)
    same_position = subprocess.check_output(['bcftools', 'query', '-f', '%POS\t%ALT[\t%GT]\n', str(merged)], text=True).splitlines()
    expected = {'C': ['1', '.', '.', '.', '.'], 'G': ['.', '1', '.', '.', '.']}
    checked = set()
    for line in same_position:
        pos, alt, *gt = line.split('\t')
        if pos == '1':
            assert gt == expected[alt], (alt, gt)
            checked.add(alt)
    assert checked == {'C', 'G'}, checked
print('PASS: five samples, allele union, and unknown genotypes preserved')
