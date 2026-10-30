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
(root/'provenance').mkdir(parents=True, exist_ok=True)
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
          '## Findings', '',
          f'The merged VCF contains **{analysis["merged_records"]:,} variant records**: **{analysis["variant_types"]["SNP"]:,} SNPs** and **{analysis["variant_types"]["indel"]:,} indels**. **{analysis["shared_all_samples"]:,} records** have retained calls in all ten samples.', '',
          '## Coverage and retained calls', '',
          '| Sample | Label | Retained records | Mean reference depth | Reference covered |',
          '|---|---|---:|---:|---:|']
for c,n in zip(coverage,counts):
    findings.append(f'| {c["sample_id"]} | {c["label"]} | {int(n["retained_variants"]):,} | {c["mean_depth"]:.2f}× | {c["coverage_percent"]:.2f}% |')
findings += ['', 'Coverage uses `samtools coverage -q 20 -Q 0`, divided by the entire reference length, including uncovered sequence.', '']
findings += """## Notes on interpreting the results

- A retained record is a variant that passed the workflow's filters. Per-sample totals count retained records; the merged total is the union of records across samples, so it is not the sum of the sample totals.
- Mean reference depth describes the average number of aligned reads across the reference. Coverage breadth describes the fraction of reference bases covered. Similar breadth can occur with different depths, and neither average guarantees reliable evidence at a particular position.
- A SNP changes one base. An indel represents an insertion or deletion relative to the reference. These differences are not automatically caused by genome editing.
- Calls shared by controls and treatment samples can reflect differences between the study material and the reference. Establishing treatment-specific changes requires comparable callable regions and further analysis.
- In this haploid analysis, GT `1` denotes an alternate allele call. A missing genotype (`.`) is unknown; it must not be counted as a confirmed reference allele.
- DP is the usable depth reported by the caller, and AD lists reads supporting each allele. Separately calculated BAM depth can differ because of read filtering and overlap handling.

## Notes on inspecting saved outputs

Start with `results/summary.tsv` for per-sample counts and `results/validation.json` for merge checks. The coverage table is in `results/coverage.tsv`; `results/merged.vcf.gz` contains the merged variant records.

The validation checks establish that the merge retained the expected allele union, sample order, and carried genotypes. They do not independently establish biological accuracy or editing specificity.

Local read review can help assess depth, read placement, and allele support. The individual screenshots are omitted from this submission to keep the findings concise.

## Interpretation limits

This is a selected, unbalanced subset of an editing-specificity study. Prefix sampling is deterministic rather than random. Moderate coverage can miss variants, and variant-only merging does not establish which alleles are absent. Common-site genotyping and comparable callable regions are needed before testing group differences. The original study conclusions are context, not conclusions independently established by this exercise.
""".strip().splitlines() + ['']
(root/'FINDINGS.md').write_text('\n'.join(findings))
hashes=[]
for path in [result/'merged.vcf.gz',*images.glob('*.png'),result/'coverage.svg']:
    hashes.append(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root).as_posix()}')
(root/'provenance/deep-deliverables.sha256').write_text('\n'.join(hashes)+'\n')
print('Published measured ten-sample deep-run report, figures, VCF, and checksums')
