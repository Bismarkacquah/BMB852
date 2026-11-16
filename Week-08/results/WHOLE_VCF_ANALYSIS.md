# Whole merged VCF: visualization and interpretation

All **39,458 allele records**, all **five sample columns**, and all **214 contigs with calls** were read directly from the final annotated VCF. No records were downsampled for these plots.

![All merged records across reference contigs](../png/08_all_merged_variants.png)

Each dot is a merged allele record. Overlapping dots can hide one another; dot density is descriptive, not a test of mutation enrichment. Reference positions restart for each contig. The four panels have different horizontal scales to keep short contigs visible; compare their numeric axes rather than apparent spacing. Colors use the most severe annotation per record.

![All retained-call patterns and similarities](../png/09_all_call_patterns.png)

## Findings

- **11,010 / 39,458 (27.9%)** records have retained alternate calls in all five samples. These shared calls are consistent with differences from the chosen reference; they do not identify an editing-specific change.
- **11,676 (29.6%)** records appear in only one retained callset. Other sample entries are unknown, so these are not confirmed sample-specific mutations.
- The displayed HIGH frameshift, MODERATE missense, and LOW synonymous examples in the [IGV report](../README.md#5-five-sample-igv-visualization) each have alternate calls in both controls and all three CRIS samples. They illustrate transcript consequences, rather than distinguish treatment groups.
- Most severe impacts are 143 HIGH, 1,001 MODERATE, 708 LOW, and 37,606 MODIFIER. MODIFIER is an annotation category, not proof of no biological effect. Among HIGH records, 142 include protein-coding transcripts and one includes a pseudogene transcript.
- Mean reference depths are approximately 8×. Independent filtering at this depth can produce missing calls and differences in overlap even when samples share an underlying allele.

- The highest pairwise retained-call overlap is CRIS1#1 versus CRIS1#2 (Jaccard 0.609). The three CRIS sample pairs range from 0.595 to 0.609, while the two controls have 0.539. This descriptive pattern does not establish an editing effect; shared background, library properties, and callability can also influence overlap.

## What the similarity means

Jaccard similarity is the number of shared retained allele records divided by the number retained in either sample. It measures callset overlap, not genome-wide genetic identity. It excludes sites absent from both callsets and is sensitive to depth and filtering.

## Next analytical step

Before claiming CRIS-specific variants, genotype the union sites in every BAM using a shared calling procedure, then compare samples only at sites meeting consistent coverage, mapping-quality, base-quality, and genotype-confidence criteria. A missing variant-only call cannot be converted to a reference genotype. Inspect prioritized loci in all five BAMs and confirm functional or causal interpretations with additional evidence.

## Reproduce

Run from `Week-8` after the merged annotated VCF is available:

```bash
python scripts/visualize_merged.py
```

The environment needs matplotlib and numpy (included in `environment.yml`). On this workstation use `tools/plotenv/bin/python` for plotting. The script checks sample order, total records, and every call-pattern count against the validated merge summary.

Outputs: [machine-readable summary](whole_vcf_summary.json), [contig counts and reference-length-normalized density](contig_variant_counts.tsv), and the two figures above. Counts per Mb use the full contig length, not the callable sequence length.
