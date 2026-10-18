"""Ensure embedded ID delimiters cannot shift HGVS, rank, or warning columns."""
import subprocess
import sys
from pathlib import Path
import tempfile

script = Path(__file__).with_name('fix_ann_delimiters.py')
ann = 'T|frameshift_variant|HIGH|PHYPA_TEST|gene-PHYPA_TEST|transcript|rna-gnl|WGS:ABEU|Pp_test|protein_coding|1/2|c.3dupT|p.Ala2CysfsTer3|3/100|3/90|2/30||WARNING_TRANSCRIPT_INCOMPLETE'
fixture = '##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\ttest\nCM_TEST\t1\t.\tA\tAT\t90\tPASS\tANN=' + ann + '\tGT\t1\n'
first = subprocess.run([sys.executable, str(script)], input=fixture, text=True, capture_output=True, check=True)
data = next(line for line in first.stdout.splitlines() if not line.startswith('#'))
fields = data.split('\t')[7][4:].split('|')
assert len(fields) == 16
assert fields[6] == 'rna-gnl%7CWGS:ABEU%7CPp_test'
assert fields[7:11] == ['protein_coding', '1/2', 'c.3dupT', 'p.Ala2CysfsTer3']
assert fields[15] == 'WARNING_TRANSCRIPT_INCOMPLETE'
second = subprocess.run([sys.executable, str(script)], input=first.stdout, text=True, capture_output=True, check=True)
assert first.stdout == second.stdout, 'Formatting repair is not idempotent'
bad = subprocess.run([sys.executable, str(script)], input=fixture.replace(ann, 'T|missense_variant'), text=True, capture_output=True)
assert bad.returncode != 0
with tempfile.TemporaryDirectory() as directory:
    gff = Path(directory) / 'fixture.gff'
    gff.write_text('##gff-version 3\nCM_TEST\tNCBI\tpseudogene\t1\t100\t.\t+\t.\tID=gene-PHYPA_TEST;gene_biotype=pseudogene;pseudo=true\nCM_TEST\tNCBI\tmRNA\t1\t100\t.\t+\t.\tID=rna-gnl|WGS:ABEU|Pp_test;Parent=gene-PHYPA_TEST\n')
    inherited = fixture.replace('|gene-PHYPA_TEST|transcript|', '|placeholder-gene|transcript|')
    pseudo = subprocess.run([sys.executable, str(script), '--gff', str(gff)], input=inherited, text=True, capture_output=True, check=True)
    record = next(line for line in pseudo.stdout.splitlines() if not line.startswith('#'))
    assert record.split('\t')[7][4:].split('|')[7] == 'pseudogene'
    again = subprocess.run([sys.executable, str(script), '--gff', str(gff)], input=pseudo.stdout, text=True, capture_output=True, check=True)
    assert pseudo.stdout == again.stdout
print('PASS: ANN field alignment, HGVS/warnings, idempotence, and malformed-entry rejection')
