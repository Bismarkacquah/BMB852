"""Publish measured deep-run outputs without overwriting the archived smoke test."""
import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path
from workflow import design

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--design',default='design.csv')
p.add_argument('--output',type=Path,default=Path('output'))
a=p.parse_args()
rows=design(a.design)
out=a.output
root=Path(__file__).resolve().parents[1]
result=root/'results'
images=result/'igv'
images.mkdir(parents=True,exist_ok=True)
analysis=json.loads((out/'analysis.json').read_text())
validation=json.loads((out/'validation.json').read_text())
assert validation['exact_union_verified'] and validation['genotypes_verified']
assert len(validation['samples'])==10
assert analysis['merged_records']==validation['merged_records'], 'Record counts disagree; inspect duplicate alleles'
def public_record(value):
    if isinstance(value,dict):
        return {k:public_record(v) for k,v in value.items() if k not in ('path','source_bam')}
    if isinstance(value,list):
        return [public_record(v) for v in value]
    return value
manifests={}
for row in rows:
    folder=out/row['sample_id']
    source=folder/'reused-bam.json'
    if not source.exists():
        source=folder/'reads.json'
    manifests[row['sample_id']]=public_record(json.loads(source.read_text()))
(root/'provenance/deep-read-manifests.json').write_text(json.dumps(manifests,indent=2)+'\n')
coverage=json.loads((out/'coverage.json').read_text())
examples=json.loads((out/'igv_examples.json').read_text())
for name in ('merged.vcf.gz','merged.vcf.gz.csi','merged.vcf.gz.tbi','summary.tsv','validation.json','versions.json',
             'parameters.json','coverage.tsv','coverage.json','analysis.json','coverage.svg','igv_examples.json'):
    shutil.copyfile(out/name,result/name)
for name in ('example_1.png','example_2.png','example_1.boxed.png','example_2.boxed.png','regional.png',
             'ten_samples.batch.txt','ten_samples.session.xml'):
    source=out/'igv'/name
    if name.endswith('.png'):
        assert source.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n' and source.stat().st_size>1000
    shutil.copyfile(source,images/name)
with (out/'summary.tsv').open() as handle:
    counts=list(csv.DictReader(handle,delimiter='\t'))
depths=[c['mean_depth'] for c in coverage]
breadths=[c['coverage_percent'] for c in coverage]
read_pairs={int(r['pairs']) for r in rows}
assert read_pairs=={20000000}
# Keep the concise, hand-maintained README when regenerating detailed results.
findings=['# Week 9 findings', '',
          'All results below use the ten 20-million-pair samples. The old smoke-test findings are not mixed into this analysis.', '',
          '## Coverage and retained calls', '',
          '| Sample | Label | Retained records | Mean reference depth | Reference covered |',
          '|---|---|---:|---:|---:|']
for c,n in zip(coverage,counts):
    findings.append(f'| {c["sample_id"]} | {c["label"]} | {int(n["retained_variants"]):,} | {c["mean_depth"]:.2f}× | {c["coverage_percent"]:.2f}% |')
findings += ['', 'Coverage uses `samtools coverage -q 20 -Q 0`, divided by the entire reference length, including uncovered sequence. Mean depth and coverage breadth describe different properties; neither guarantees adequate depth at every site. Call counts are affected by depth, alignment, and filtering as well as biology.', '',
             '## IGV read evidence', '',
             'All ten BAMs and the merged VCF are loaded against the same reference. Each BAM track is named by its run accession. The red rectangle follows the selected reference position through the genotype rows and read tracks. Pink/purple read backgrounds encode strand; colored bases and indel markers indicate sequence differences. Explanations appear below each image.', '']
for i,v in enumerate(examples,1):
    findings += [f'### Example {i}: {v["chrom"]}:{v["pos"]:,} {v["ref"]}>{v["alt"]}', '',
                 f'![Ten-sample {v["type"]} evidence](results/igv/example_{i}.boxed.png)', '',
                 f'This {v["type"]} has retained calls in **{v["retained_samples"]}/10 samples**. The rectangle identifies its exact position, rather than neighboring mismatch columns. Read support is summarized below; `.` means an unknown genotype in the variant-only merge.', '',
                 '| Sample | Label | GT | Usable DP | AD (REF,ALT) | Quality-filtered BAM depth |',
                 '|---|---|---|---:|---|---:|']
    for row,call,depth in zip(rows,v['calls'],v['quality_filtered_depths']):
        findings.append(f'| {row["sample_id"]} | {row["label"]} | `{call["GT"]}` | {call.get("DP",".")} | `{call.get("AD",".")}` | {depth} |')
    present_groups=sorted({row['group'] for row,c in zip(rows,v['calls']) if c['GT'] not in ('.','./.','.|.')})
    findings += ['', f'Retained calls occur in these study-label groups: **{", ".join(present_groups)}**. Presence across groups is consistent with a shared difference from the chosen reference, rather than evidence of an editing-specific change. Missing calls elsewhere cannot be interpreted as confirmed reference genotypes.', '',
                 f'Position depth without base/mapping-quality thresholds ranges from {min(v["unfiltered_depths"])} to {max(v["unfiltered_depths"])} reads across samples, using SAMtools depth with its default flag filters. Examples are limited to moderate read density so the ten-track view remains readable.', '',
                 'Usable DP/AD comes from the variant caller. The separate BAM depth uses base quality ≥20 and mapping quality ≥20; overlap handling and filtering can make it differ from caller DP. These are read-support observations, not experimental confirmation or functional-effect predictions.', '',
                 f'[Original IGV screenshot](results/igv/example_{i}.png). The rectangle is a presentation overlay; read data are unchanged.', '']
findings += ['## Regional context', '', '![Ten-sample regional coverage](results/igv/regional.png)', '',
             'This 5-kb window surrounds the SNP example. Inspect coverage continuity and local read placement before interpreting a variant. Tracks can autoscale independently, so compare their numeric scales rather than apparent bar heights alone.', '',
             '## Interpretation limits', '',
             'This is a selected, unbalanced subset of an editing-specificity study. Prefix sampling is deterministic rather than random. Moderate coverage can miss variants, and variant-only merging does not establish which alleles are absent. Common-site genotyping and comparable callable regions are needed before testing group differences. The original study conclusions are context, not conclusions independently established by this exercise.', '',
             'The saved IGV batch/session contains the execution machine’s paths. Run `make report` to regenerate paths for your checkout. Reopen the original images and your local session to inspect the evidence independently.', '']
(root/'FINDINGS.md').write_text('\n'.join(findings))
hashes=[]
for path in [result/'merged.vcf.gz',*images.glob('*.png'),result/'coverage.svg']:
    hashes.append(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root).as_posix()}')
(root/'provenance/deep-deliverables.sha256').write_text('\n'.join(hashes)+'\n')
print('Published measured ten-sample deep-run report, figures, VCF, and checksums')
