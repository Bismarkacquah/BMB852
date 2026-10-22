"""Measure coverage, summarize retained-call patterns, and choose IGV examples."""
import argparse
import concurrent.futures
import csv
import gzip
from html import escape
import json
from collections import Counter
from pathlib import Path
import subprocess
from workflow import design

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--design',default='design.csv')
p.add_argument('--output',type=Path,default=Path('output'))
p.add_argument('--reference',type=Path,required=True)
a=p.parse_args()
rows=design(a.design)
out=a.output
length=sum(int(line.split('\t')[1]) for line in Path(str(a.reference)+'.fai').read_text().splitlines())
bams=[out/r['sample_id']/'aligned.bam' for r in rows]

def coverage(item):
    row,bam=item
    target=out/row['sample_id']/'coverage.tsv'
    if not target.exists() or target.stat().st_mtime < bam.stat().st_mtime:
        temporary=Path(str(target)+'.part')
        with temporary.open('w') as handle:
            subprocess.run(['samtools','coverage','-q','20','-Q','0',str(bam)],stdout=handle,check=True)
        temporary.replace(target)
    covered=weighted=0
    with target.open() as handle:
        for c in csv.DictReader(handle,delimiter='\t'):
            n=int(c['endpos'])-int(c['startpos'])+1
            covered+=int(c['covbases'])
            weighted+=n*float(c['meandepth'])
    return {'sample_id':row['sample_id'],'label':row['label'],'pairs':int(row['pairs']),
            'covered_bases':covered,'reference_bases':length,'coverage_percent':100*covered/length,
            'mean_depth':weighted/length}

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    coverages=list(pool.map(coverage,zip(rows,bams)))
with (out/'coverage.tsv').open('w') as handle:
    writer=csv.DictWriter(handle,fieldnames=coverages[0],delimiter='\t')
    writer.writeheader();writer.writerows(coverages)
(out/'coverage.json').write_text(json.dumps(coverages,indent=2)+'\n')
variants=[]
counts=Counter()
patterns=Counter()
positions=Counter()
with gzip.open(out/'merged.vcf.gz','rt') as handle:
    for line in handle:
        if line.startswith('#'):
            continue
        f=line.rstrip().split('\t')
        fields=f[8].split(':')
        calls=[dict(zip(fields,s.split(':'))) for s in f[9:]]
        present=[c['GT'] not in ('.','./.','.|.') for c in calls]
        sequence_alleles=set((f[3]+f[4]).upper()) <= set('ACGT')
        kind=('SNP' if len(f[3])==len(f[4])==1 else ('indel' if len(f[3])!=len(f[4]) else 'other')) if sequence_alleles else 'other'
        counts[kind]+=1
        patterns[''.join('1' if x else '0' for x in present)]+=1
        positions[f[0],int(f[1])]+=1
        variants.append({'chrom':f[0],'pos':int(f[1]),'ref':f[3].upper(),'alt':f[4].upper(),
                         'type':kind,'calls':calls,'retained_samples':sum(present),
                         'qual':float(f[5]) if f[5]!='.' else 0})
selected=[]
for kind in ('SNP','indel'):
    candidates=[v for v in variants if v['type']==kind and v['retained_samples']>=5 and v['qual']>=100
                and positions[v['chrom'],v['pos']]==1
                and sum(int(c.get('DP','0'))>=8 for c in v['calls'] if c.get('DP','.')!='.')>=5]
    candidates.sort(key=lambda v:(-v['retained_samples'],v['chrom'],v['pos']))
    for v in candidates[:300]:
        locus=f'{v["chrom"]}:{max(1,v["pos"]-40)}-{v["pos"]+40}'
        sequence=subprocess.check_output(['samtools','faidx',str(a.reference),locus],text=True)
        if 'N' in ''.join(sequence.splitlines()[1:]).upper():
            continue
        at=f'{v["chrom"]}:{v["pos"]}-{v["pos"]}'
        depth=subprocess.check_output(['samtools','depth','-a','-q','20','-Q','20','-r',at,*map(str,bams)],text=True).strip()
        if not depth:
            continue
        values=list(map(int,depth.split('\t')[2:]))
        if len(values)!=len(rows) or max(values)>100 or min(values)<4:
            continue
        raw=subprocess.check_output(['samtools','depth','-a','-r',at,*map(str,bams)],text=True).strip()
        raw_values=list(map(int,raw.split('\t')[2:])) if raw else []
        if len(raw_values)!=len(rows) or max(raw_values)>32:
            continue
        v['quality_filtered_depths']=values
        v['unfiltered_depths']=raw_values
        selected.append(v)
        break
if len(selected)!=2:
    raise ValueError('Could not select both a supported SNP and indel; inspect coverage and candidates')
(out/'igv_examples.json').write_text(json.dumps(selected,indent=2)+'\n')
summary={'sample_count':len(rows),'merged_records':len(variants),'variant_types':dict(counts),
         'shared_all_samples':patterns['1'*len(rows)],'patterns':dict(patterns),
         'coverage_definition':'samtools coverage -q 20 -Q 0; full reference denominator',
         'example_depth_definition':'samtools depth -q 20 -Q 20 (base and mapping quality >=20)',
         'reference_bases':length}
(out/'analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
# SVG is generated directly from measured values and needs no plotting package.
width=980; height=110+len(rows)*40
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
       '<rect width="100%" height="100%" fill="white"/>',
       '<g font-family="sans-serif" font-size="14" fill="#243746">',
       '<text x="20" y="28" font-size="20">Measured whole-reference depth and coverage</text>',
       '<text x="260" y="58">Mean depth (MQ ≥20)</text><text x="640" y="58">Reference covered</text>']
maxdepth=max(c['mean_depth'] for c in coverages)*1.15
for i,c in enumerate(coverages):
    y=76+i*40
    parts += [f'<text x="20" y="{y+18}">{escape(c["sample_id"])} {escape(c["label"])}</text>',
              f'<rect x="260" y="{y}" width="{300*c["mean_depth"]/maxdepth:.2f}" height="24" fill="#176e86"/>',
              f'<text x="570" y="{y+18}">{c["mean_depth"]:.2f}×</text>',
              f'<rect x="640" y="{y}" width="{240*c["coverage_percent"]/100:.2f}" height="24" fill="#37a28f"/>',
              f'<text x="890" y="{y+18}">{c["coverage_percent"]:.2f}%</text>']
parts+=['</g></svg>']
(out/'coverage.svg').write_text('\n'.join(parts)+'\n')
print(json.dumps(summary,indent=2))
