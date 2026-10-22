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
summary=[
    '# Week 9 assignment', '',
    '## Project and design', '',
    '[PRJEB51295](https://www.ebi.ac.uk/ena/browser/view/PRJEB51295) investigates genome-wide specificity of CRISPR-Cas9 and TALEN editing in *Physcomitrium patens*. The archive contains 14 runs. This analysis selects ten: two controls, four CRIS-labelled samples, two PEG samples, one PEG-DNA sample, and one TAL-labelled sample. These are an unbalanced subset, not a complete replication of the original study.', '',
    'The [design.csv](design.csv) records sample labels, BioSamples, paired FASTQ URLs and sizes, read-pair counts, and ploidy. All samples use the same Week 7 reference, **GCA_000002425.2 (Phypa V3)**, and **20 million read pairs each**. Haploid calling is an explicit assumption.', '',
    '## Reproduce', '',
    'Use Linux/WSL with the existing bioinfo environment active. Additional prerequisites are **cutadapt 5.2**, **IGV 2.19.8 with Java 21 and a working display**, and **matplotlib 3.10.8** for boxed screenshots. Install prerequisites yourself; the workflow installs no software. Allow roughly 150 GB of free space and hours of processing for a fresh ten-sample run.', '',
    '```bash\ngit clone https://github.com/Bismarkacquah/BMB852.git\ncd BMB852/Week-9\nmake check\nmake samples\nmake -j2 batch THREADS=3\n```', '',
    'All ten samples, **ERR8982183 through ERR8982192**, are already in `design.csv` at 20 million read pairs each. No manual sample selection or earlier-week files are needed. Plain `make` also runs and merges all ten. Use `make sample SAMPLE=ERR8982185 THREADS=3` for the original Week 7 sample, or `make help` for available commands.', '',
    'Optional figure regeneration after the batch finishes:', '',
    '```bash\nexport IGV_DIR=/absolute/path/to/IGV_Linux_2.19.8\nmake report THREADS=3 PLOT_PYTHON=python3\n```', '',
    '`sample` calls variants for one design row; `batch` processes every row and merges the VCFs. `report` measures coverage, regenerates IGV screenshots, and writes this report using paths from your checkout. Set `PLOT_PYTHON` to an existing interpreter with matplotlib. Two samples can run concurrently; use `make batch THREADS=3` for serial sample processing.', '',
    'The workflow downloads and checks the reference, indexes it, verifies synchronized read subsets, trims adapters/low-quality ends, aligns reads, calls and normalizes variants, and retains QUAL ≥20 and DP ≥3. Logs and manifests are under `output/SAMPLE/`. The merged VCF is `output/merged.vcf.gz`; validation is `output/validation.json`. Repeating the commands reuses completed targets. Edit the CSV or use `DESIGN=other.csv OUT=other_output` to change the input design.', '',
    '## Findings', '',
    f'- **{analysis["merged_records"]:,} merged allele records** across ten samples: {analysis["variant_types"].get("SNP",0):,} SNPs and {analysis["variant_types"].get("indel",0):,} indels. Other record types: {analysis["variant_types"].get("other",0):,}.',
    f'- Measured mean reference depths range from **{min(depths):.2f}× to {max(depths):.2f}×**, with **{min(breadths):.2f}–{max(breadths):.2f}%** of the full reference covered at mapping quality ≥20. This supports variant detection while leaving local low-depth uncertainty.',
    f'- **{analysis["shared_all_samples"]:,} records** have retained calls in all ten samples. Missing calls remain unknown. Neither shared variants nor unequal call counts establish editing-induced mutations.', '',
    '![Measured coverage](results/coverage.svg)', '',
    '## IGV analysis of the merged VCF', '',
    'The top track is the merged ten-sample VCF; the ten BAM tracks below show the supporting reads. Red rectangles mark the loci discussed here. Open the images at full size to read the run labels.', '',
    f'### Shared SNP: {examples[0]["chrom"]}:{examples[0]["pos"]:,} {examples[0]["ref"]}>{examples[0]["alt"]}', '',
    '![Merged VCF and all ten samples at the SNP](results/igv/example_1.boxed.png)', '',
    'All ten samples have a retained alternate call at this SNP, including both controls. The aligned reads support the same change across study groups. This is consistent with a shared difference from the reference; it does not establish an editing-induced mutation.', '',
    f'### Shared deletion: {examples[1]["chrom"]}:{examples[1]["pos"]:,} {examples[1]["ref"]}>{examples[1]["alt"]}', '',
    '![Merged VCF and all ten samples at the deletion](results/igv/example_2.boxed.png)', '',
    'The AT>A allele represents deletion of the T immediately after the retained A anchor. All ten samples carry a retained alternate call. The boxed read gaps support the deletion, although some reads retain reference support. The complete per-sample GT, DP, and AD values are in [the read-support tables](FINDINGS.md#example-2-abeu02000041125818-ata).', '',
    '[Regional IGV view](results/igv/regional.png) shows the surrounding coverage, including shared gaps. Missing calls and uncovered positions remain unknown. See [the detailed IGV analysis](FINDINGS.md#igv-read-evidence) for all ten samples and interpretation limits.', '',
    'See [IGV findings and read-support tables](FINDINGS.md), [per-sample counts](results/summary.tsv), [merged VCF](results/merged.vcf.gz), and [validation](results/validation.json). The [10,000-pair smoke test](results/smoke/) is archived separately and is not the biological analysis. `make smoke` checks the short computational path only.', '',
    'Study metadata and reuse records are in [provenance](provenance/README.md). The selected subset and moderate coverage do not support reproducing the original study’s off-target conclusions without common-site genotyping, callable-site filtering, and appropriate controls.', '']
(root/'README.md').write_text('\n'.join(summary))
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
