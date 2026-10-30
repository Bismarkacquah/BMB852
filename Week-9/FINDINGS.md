# Week 9 findings

All results below use ten samples with 20 million read pairs each.

## Findings

The merged VCF contains **47,442 variant records**: **38,682 SNPs** and **8,760 indels**. **7,833 records** have retained calls in all ten samples. The per-sample summary and interpretation notes are below.

## Coverage and retained calls

| Sample | Label | Retained records | Mean reference depth | Reference covered |
|---|---|---:|---:|---:|
| ERR8982183 | Control#1 | 21,396 | 8.03× | 96.19% |
| ERR8982184 | Control#2 | 22,438 | 8.23× | 96.28% |
| ERR8982185 | CRIS1#1 | 24,042 | 8.42× | 96.48% |
| ERR8982186 | CRIS1#2 | 24,009 | 8.57× | 96.24% |
| ERR8982187 | CRIS2#1 | 23,655 | 8.07× | 96.38% |
| ERR8982188 | CRIS2#2 | 23,461 | 8.33× | 96.25% |
| ERR8982189 | PEG#1 | 21,061 | 7.82× | 95.89% |
| ERR8982190 | PEG#2 | 22,660 | 8.44× | 96.56% |
| ERR8982191 | PEG-DNA#1 | 22,691 | 8.73× | 96.42% |
| ERR8982192 | TAL#1 | 23,364 | 8.39× | 96.20% |

Coverage uses `samtools coverage -q 20 -Q 0`, divided by the entire reference length, including uncovered sequence. Mean depth and coverage breadth describe different properties; neither guarantees adequate depth at every site. Call counts are affected by depth, alignment, and filtering as well as biology.

## Notes on interpreting the results

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

## Regional coverage

![Regional coverage across all ten samples](results/igv/regional.png)

This 5-kb window shows local coverage across all ten samples. Check coverage continuity and read placement before interpreting a variant. Tracks can autoscale independently, so compare their numeric scales rather than apparent bar heights. Coverage gaps cannot be treated as confirmed reference-matching regions.

## Interpretation limits

This is a selected, unbalanced subset of an editing-specificity study. Prefix sampling is deterministic rather than random. Moderate coverage can miss variants, and variant-only merging does not establish which alleles are absent. Common-site genotyping and comparable callable regions are needed before testing group differences. The original study conclusions are context, not conclusions independently established by this exercise.
