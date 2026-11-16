"""Prepare an IGV batch using this checkout's own ten BAMs and merged VCF."""
import argparse
import json
from pathlib import Path
from workflow import design

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--design',default='design.csv')
p.add_argument('--output',type=Path,default=Path('output'))
p.add_argument('--reference',type=Path,required=True)
a=p.parse_args()
out=a.output.resolve()
images=out/'igv'
images.mkdir(exist_ok=True)
rows=design(a.design)
examples=json.loads((out/'igv_examples.json').read_text())
lines=['new','setSleepInterval 1000',f'genome {a.reference.resolve()}',
       f'snapshotDirectory {images}',f'load {out/"merged.vcf.gz"}',
       'maxPanelHeight 4200','setSequenceShowTranslation false','expand']
for row in rows:
    bam=out/row['sample_id']/'aligned.bam'
    aliases=images/'bams'
    aliases.mkdir(exist_ok=True)
    alias=aliases/f'{row["sample_id"]}.bam'
    if not alias.is_symlink() and not alias.exists():
        alias.symlink_to(bam)
    index=Path(str(alias)+'.bai')
    if not index.is_symlink() and not index.exists():
        index.symlink_to(Path(str(bam)+'.bai'))
    lines += [f'load {alias}']
lines += ['expand','colorBy READ_STRAND','scrollToTop','setTrackHeight 260 merged.vcf.gz']
for row in rows:
    lines += [f'setTrackHeight 160 {row["sample_id"]}.bam']
for i,v in enumerate(examples,1):
    locus=f'{v["chrom"]}:{max(1,v["pos"]-40)}-{v["pos"]+40}'
    lines += [f'goto {locus}', f'sort BASE {v["chrom"]}:{v["pos"]}',f'snapshot example_{i}.png']
v=examples[0]
lines += [f'goto {v["chrom"]}:{max(1,v["pos"]-2500)}-{v["pos"]+2500}',
          'snapshot regional.png',f'saveSession {images/"ten_samples.session.xml"}','exit']
(images/'ten_samples.batch.txt').write_text('\n'.join(lines)+'\n')
print(images/'ten_samples.batch.txt')
