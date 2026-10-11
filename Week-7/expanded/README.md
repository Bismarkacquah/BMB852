# Expanded Week 7 analysis: 20 million read pairs

This follow-up uses a substantially larger subset of the same public moss
sequencing run, `ERR8982185`, to improve coverage and add informative IGV
screenshots. The original Week 5 BAM and the original Week 7 results remain
available in their existing locations.

## Data and methods

- Organism: *Physcomitrium patens*; sample `SAMEA13207856` (CRIS1#1 protonema).
- Reference: the same `GCA_000002425.2_Phypa_V3` assembly, 471,852,792 bases.
- Input selection: the first **20,000,000 paired records** of the two public
  ENA FASTQ files. This is 20,000 times the original requested pair count.
- Source: [ENA run ERR8982185](https://www.ebi.ac.uk/ena/browser/view/ERR8982185).
  Public file locations, sizes, and full-file MD5 values are saved in
  [the ENA metadata](../provenance/ena-expanded.tsv).

The ENA FASTQ prefix is **not identical to the earlier SRA-extracted prefix**:
the first read lengths differ. The expanded data are therefore a separate
subset of the same accession, not a byte-for-byte extension of the original
1,000-spot subset. Comparisons show the effect of using more data from the
same run; they do not track exactly nested read sets.

[download_subset.py](../scripts/download_subset.py) retrieves ordered HTTP byte
ranges and decompresses them in order, stopping after the selected records.
It checks HTTP range coordinates and lengths, four-line FASTQ structure,
sequence/quality lengths, and agreement of the mate identifier hashes. A
100,000-pair test passed; the first 10 MiB of the ranged stream also matched
an independent direct download across a chunk boundary. See
[download-validation.txt](provenance/download-validation.txt).
The published full-file MD5 values do not verify this truncated subset;
local SHA-256 hashes identify the actual subset files used here.

Reads are trimmed with the same adapter sequences, Q20 end trimming, and
30-base minimum length as Week 5. BWA MEM aligns the pairs with an Illumina
read group and sample name `ERR8982185`. Samtools sorts and indexes the BAM.
The run uses four BWA threads and two sort threads with 256 MiB per sort
thread to limit memory use. Duplicate reads are not marked or removed, so
coverage and caller support are not counts of independent DNA molecules.

Variant calling retains the original haploid model and thresholds:
BCFtools `mpileup -q 20 -Q 20 -d 1000`, multiallelic variant calling,
reference normalization, and filtering at `QUAL >= 20` and `FORMAT/DP >= 3`.
PASS means these thresholds were met; it does not independently establish
that a call is a true mutation or a CRISPR edit.

Genome-wide depth is calculated with `samtools depth -Q 20` (minimum mapping
quality 20, minimum base quality 0, overlapping mates counted separately).
Uncovered reference bases are included in the denominator. This depth is
different from the caller's usable sample depth after base-quality, BAQ,
and overlapping-mate adjustments. The original saved Week 5 depth used no
minimum mapping-quality threshold; a new baseline summary applies the same
mapping-quality threshold as the expanded analysis for the comparison here.

## Reproduce

Use the Week 7 environment and complete `make setup` in Week 7 if the reference
is missing. The existing BWA indexes from Week 5 are reused; create them with
`make -C ../../Week-5 reference index` if necessary.

```bash
cd BMB852/Week-7/expanded
conda activate week7-moss
make all THREADS=4 SORT_THREADS=2
make validate

# Generate native Linux/macOS paths for IGV:
make igv
# Or generate paths for Windows IGV from WSL:
make igv IGV_ROOT=C:/path/to/BMB852
```

In IGV, select **Tools > Run Batch Script** and open
`expanded/scripts/igv_local_batch.txt`. The script loads the reference,
expanded candidate and PASS VCFs, and expanded BAM; it captures the original
loci and selected well-supported PASS variants. Generated local sessions
and batch files contain machine-specific paths and are ignored by Git.

The FASTQ files and BAM are too large for ordinary GitHub storage and are
ignored by Git. The workflow regenerates them. Download and alignment take
substantially longer than the original 1,000-pair exercise and require
several GB of disk space. Subsequent Make runs reuse completed targets.

## Measured results and IGV screenshots

The expanded download contained 20,000,000 synchronized pairs. Trimming
retained **19,977,564 pairs** and **6,010,110,684 bases**. Of the primary
reads, **74.31% mapped** and **71.72% were properly paired**. The sorted BAM
passed `samtools quickcheck` and was indexed successfully.

| Measure | Original subset | Expanded subset |
|---|---:|---:|
| Trimmed pairs | 997 | 19,977,564 |
| Covered reference bases, MAPQ >= 20 | 188,078 | 455,259,998 |
| Reference covered | 0.0399% | 96.4835% |
| Mean depth across the reference | 0.000418 | 8.4184 |
| Mean depth at covered positions | 1.0479 | 8.7252 |
| Maximum depth | 4 | 24,408 |

The maximum depth is an extreme pileup, not representative genome coverage.
Repeats, ambiguous mapping, and unmarked duplicates can affect depth and
variant evidence. Screenshot selection therefore favors moderate-depth
calls with high mapping quality and strong alternate-allele support.

The calculations are saved in [depth-summary.json](results/depth-summary.json)
and [original-matched-depth.json](results/original-matched-depth.json).
The [mapping report](results/flagstat.txt),
[chromosome coverage report](results/coverage.tsv), and
[download manifest](provenance/download.json) provide additional checks.
The original subset's larger saved Week 5 coverage percentage used different
mapping-quality settings; the table above uses a matched threshold.

This run used BWA 0.7.19, Cutadapt 5.2, Samtools 1.22.1, and BCFtools 1.24.
The exact [tool versions](provenance/tool-versions.txt) are recorded. The
provided environment specification is a reproduction recipe; this execution
reused the installed Week 5 tools and the existing BCFtools environment.

### Variant results

| VCF | Records | SNPs | Indels |
|---|---:|---:|---:|
| Raw candidates | 32,651 | 27,494 | 5,157 |
| Normalized, with filter labels | 32,651 | 27,494 | 5,157 |
| PASS only | 24,042 | 19,576 | 4,466 |

There are 8,609 records failing the QUAL/depth thresholds. The original
1,000-pair exercise had 134 candidates and zero passing calls. More coverage
therefore produces many calls that meet the same minimum evidence criteria.
These are reference differences identified by this workflow, not validated
mutations or demonstrated CRISPR edits.

Download the [filtered VCF](results/ERR8982185.20M.filtered.vcf.gz) or
[PASS VCF](results/ERR8982185.20M.pass.vcf.gz), with its adjacent `.tbi` index,
for viewing. See [summary.json](results/summary.json) and
[PASS statistics](results/pass.stats.txt) for the complete counts.

`make validate` checks BAM integrity, reference agreement of all 24,042
PASS alleles, and SHA-256 hashes of the BAM, both trimmed mate files, and
both final VCFs. See [validation.log](provenance/validation.log).
BCFtools emits the same nonfatal `MQ should be declared as Type=Float`
header warning as the original analysis; reference and parsing checks pass.

### IGV screenshots

These seven images were captured directly from IGV 2.19.8 and visually
checked. The tracks show the filtered candidate VCF, PASS VCF, BAM coverage,
and read alignments. Gray reads largely match the reference; colored bases
mark mismatches, and purple insertion markers indicate inserted bases.
Caller DP differs from visible pileup depth because the caller applies
quality and overlapping-mate adjustments.

The three selected PASS examples have MAPQ annotation 60, caller depth 20,
and unfiltered `samtools depth` values of 20–22 at the variant position.
Selection favors depth near 20, QUAL >= 50, MQ >= 50, alternate support >= 8,
alternate fraction >= 0.8, and unfiltered pileup depth <= 100. This avoids
using extreme repeat pileups as the main examples. These are selected
illustrations, not an unbiased sample of all variants.

**Regional overview: 10 kb on CM009327.1.** Read coverage is visible across
most of the region, with variation in depth and a local gap. Variant marks
occur at individual called sites; a large number of reads does not imply a
large number of variants.

![Expanded 10-kb regional coverage](screenshots/expanded_regional_overview.png)

**SNP 1: CM009327.1:5,823,606, A>T.** PASS, QUAL 225.417, DP 20, AD 0,20.

![Supported A to T SNP](screenshots/expanded_pass_variant_1.png)

**SNP 2: CM009317.1:24,015,889, A>G.** PASS, QUAL 225.417, DP 20, AD 0,20.

![Supported A to G SNP](screenshots/expanded_pass_variant_2.png)

**Insertion: CM009327.1:9,842,294, A>AT.** PASS, QUAL 228.361, DP 20,
AD 2,18. The purple markers show the one-base insertion.

![Supported one-base insertion](screenshots/expanded_pass_variant_3.png)

The selected coordinates and measurements are saved in
[igv-selected-variants.json](results/igv-selected-variants.json). Recreate
the views using [prepare_expanded_igv.py](../scripts/prepare_expanded_igv.py)
and the Makefile's `igv` target.

### Comparison with the original loci

The original CM009322.1:3,189,512 A>G candidate now passes with caller DP 917
and AD 0,917. The earlier CM009334.1:8,569,458 T>A candidate also passes,
with DP 970 and AD 3,967. These are unusually deep loci and should not be
used to represent the genome-wide mean depth of 8.42.

**Original SNP cluster, expanded data:**

![Expanded coverage at the original SNP cluster](screenshots/expanded_original_snp_cluster.png)

**Original SNP close-up, expanded data:**

![Expanded close-up at the original SNP](screenshots/expanded_original_snp_zoom.png)

**Original insertion region, expanded data:**

![Expanded reads at the original insertion region](screenshots/expanded_original_insertion.png)

The expanded VCF contains nearby SNPs but does not contain the earlier
CM009336.1:3,474,356 A>AAAT insertion in the inspected interval. Insertion
markers remain visible in some alignments; their presence alone does not
mean the caller reports that allele. The comparison is recorded in
[original-loci-variants.tsv](results/original-loci-variants.tsv).

Greater read depth improves available evidence but does not resolve mapping
ambiguity or establish independent molecular support. The subset comparison
and the displayed loci are descriptive; validation and functional analysis
would be needed for biological conclusions.
