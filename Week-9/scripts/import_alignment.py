"""Optional local reuse of a documented earlier alignment; never used by default."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from workflow import design, sha, REFERENCE_SHA

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--sample', required=True)
p.add_argument('--bam', type=Path, required=True)
p.add_argument('--manifest', type=Path, required=True)
p.add_argument('--cutadapt', type=Path, required=True)
p.add_argument('--reference', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a=p.parse_args()
row=next(r for r in design('design.csv') if r['sample_id']==a.sample)
manifest=json.loads(a.manifest.read_text())
trim=json.loads(a.cutadapt.read_text())
args=trim['command_line_arguments']
trim_parameters={'-a':'AGATCGGAAGAGCACACGTCTGAACTCCAGTCA','-A':'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT','-q':'20,20','-m':'30'}
assert all(args[args.index(flag)+1]==value for flag,value in trim_parameters.items())
assert trim['read_counts']['input']==int(row['pairs'])
assert manifest['run']==a.sample and manifest['pairs']==int(row['pairs'])
assert all(m['records']==int(row['pairs']) for m in manifest['mates'])
assert manifest['mates'][0]['read_id_sha256']==manifest['mates'][1]['read_id_sha256']
assert sha(a.reference)==REFERENCE_SHA
subprocess.run(['samtools','quickcheck',str(a.bam)],check=True)
header=subprocess.check_output(['samtools','view','-H',str(a.bam)],text=True)
pg=next(line for line in header.splitlines() if line.startswith('@PG') and 'PN:bwa' in line.split('\t'))
command=next(field[3:] for field in pg.split('\t') if field.startswith('CL:'))
batch_match=re.search(r'(?:^|\s)-K\s+(\d+)',command)
thread_match=re.search(r'(?:^|\s)-t\s+(\d+)',command)
source_batch=int(batch_match.group(1)) if batch_match else 10000000*(int(thread_match.group(1)) if thread_match else 1)
assert source_batch==int(row['bwa_batch_bases'])
assert any(line.startswith('@RG') and ('SM:'+a.sample) in line.split('\t') for line in header.splitlines())
expected={f[0]:int(f[1]) for line in Path(str(a.reference)+'.fai').read_text().splitlines() if (f:=line.split('\t'))}
observed={}
for line in header.splitlines():
    if line.startswith('@SQ'):
        fields=dict(field.split(':',1) for field in line.split('\t')[1:])
        observed[fields['SN']]=int(fields['LN'])
assert observed==expected
a.output.mkdir(parents=True,exist_ok=True)
target=a.output/'aligned.bam'
assert not target.exists(), 'Use a new output directory for importing an alignment'
target.symlink_to(a.bam.resolve())
index=Path(str(a.bam)+'.bai')
assert index.is_file()
Path(str(target)+'.bai').symlink_to(index.resolve())
record={'sample':a.sample,'pairs':int(row['pairs']), 'bam_sha256':sha(a.bam),
        'reference_sha256':REFERENCE_SHA,'source_bam':str(a.bam.resolve()),
        'source_manifest':manifest,'read_preprocessing':'cutadapt Illumina adapters; -q 20,20 -m 30',
        'alignment':'BWA MEM; sample-specific read group; coordinate-sorted BAM',
        'cutadapt_version':trim['cutadapt_version'],'trim_parameters':trim_parameters,
        'bwa_batch_bases':source_batch,
        'verification':'quickcheck, all SQ lengths, sample RG, paired read IDs and counts, BAM SHA-256'}
(a.output/'reused-bam.json').write_text(json.dumps(record,indent=2)+'\n')
print(f'Imported verified {a.sample} alignment')
