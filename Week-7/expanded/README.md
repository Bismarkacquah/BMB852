# Week 7: More reads and a closer look in IGV

After the first run produced no passing variants, I increased the input to
20 million read pairs from `ERR8982185`. The original subset was useful for
building the workflow, but it covered too little of the moss genome for a
meaningful comparison with the reference. This larger run provided enough
coverage to inspect both SNPs and indels in IGV.

The [main Week 7 report](../README.md) contains the sample information,
Makefile changes, statistics, and discussion. This page gives the detailed
coverage comparison and all seven IGV screenshots.

## Reads, alignment, and coverage

I used the first 20,000,000 paired records from the two ENA FASTQ files.
Trimming retained 19,977,564 pairs and 6,010,110,684 bases. The same adapter
sequences, Q20 end trimming, and 30-base minimum length were used as in Week 5.
BWA MEM aligned the reads to `GCA_000002425.2_Phypa_V3`, and Samtools sorted
and indexed the BAM. Primary mapping was 74.31%, with 71.72% properly paired.

| Measure | Original subset | Expanded subset |
|---|---:|---:|
| Trimmed pairs | 997 | 19,977,564 |
| Covered reference bases | 188,078 | 455,259,998 |
| Reference covered | 0.0399% | 96.4835% |
| Mean depth across the reference | 0.000418 | 8.4184 |
| Mean depth at covered positions | 1.0479 | 8.7252 |
| Maximum depth | 4 | 24,408 |

For this comparison, both depth summaries use `samtools depth -Q 20`:
minimum mapping quality 20, minimum base quality 0, and overlapping mates
counted separately. Uncovered bases are included in the genome-wide mean.
The summaries are saved in [depth-summary.json](results/depth-summary.json)
and [original-matched-depth.json](results/original-matched-depth.json).

The original SRA subset and this ENA subset have different first records.
They come from the same run, but the larger set is not an exact extension
of the smaller one. The [download manifest](provenance/download.json) records
the selected files and checksums. The downloader checks matching mate IDs
and FASTQ structure; its range-download checks are saved in
[download-validation.txt](provenance/download-validation.txt).

## Variant counts

I kept the same haploid calling model, mapping and base quality cutoffs of
20, and PASS thresholds of QUAL >= 20 and usable depth >= 3.

| VCF | Records | SNPs | Indels |
|---|---:|---:|---:|
| Raw candidates | 32,651 | 27,494 | 5,157 |
| Normalized candidates | 32,651 | 27,494 | 5,157 |
| PASS only | 24,042 | 19,576 | 4,466 |

The 8,609 excluded records did not meet one or both thresholds. SNPs account
for 81.42% of passing calls and indels for 18.58%. The complete counts are in
[summary.json](results/summary.json) and [pass.stats.txt](results/pass.stats.txt).
The [filtered VCF](results/ERR8982185.20M.filtered.vcf.gz) retains every
normalized candidate and its filter label; the
[PASS VCF](results/ERR8982185.20M.pass.vcf.gz) keeps only passing calls.

## IGV views

I loaded the reference, BAM, filtered VCF, and PASS VCF in IGV 2.19.8.
The upper tracks show the calls, followed by coverage and aligned reads.
Gray read segments match the reference, colored bases show mismatches,
and purple markers indicate insertions.

For the close-ups, I chose calls with usable depth near 20, QUAL >= 50,
MQ >= 50, at least eight alternate observations, and an alternate fraction
of at least 0.8. I also checked that unfiltered depth at each selected site
was no more than 100. These examples were chosen for inspection and do not
represent the distribution of every call in the VCF.

### Regional view: CM009327.1

This 10-kb view shows reads across most of the interval, along with changes
in depth and a local gap. Most positions have no variant marker because
their aligned bases agree with the reference. The larger input improved
coverage without making every covered position a variant.

![Expanded 10-kb regional coverage](screenshots/expanded_regional_overview.png)

### SNP 1: CM009327.1:5,823,606, A>T

This call has QUAL 225.417, DP 20, and AD 0,20. All 20 usable observations
support T. The red T bases form a consistent column beneath the VCF marker,
with reads starting and ending at different positions. This looks more
convincing than an isolated mismatch in a single read.

![A-to-T SNP and aligned reads](screenshots/expanded_pass_variant_1.png)

### SNP 2: CM009317.1:24,015,889, A>G

The orange G bases line up with the called position. QUAL is 225.417,
DP is 20, and AD is 0,20, again showing consistent alternate support.
Both SNP examples have MQ 60. The selected calls and their measurements
are saved in [igv-selected-variants.json](results/igv-selected-variants.json).

![A-to-G SNP and aligned reads](screenshots/expanded_pass_variant_2.png)

### Insertion: CM009327.1:9,842,294, A>AT

The purple markers show a one-base insertion at the same position in many
reads. QUAL is 228.361, DP is 20, and AD is 2,18, so 18 usable observations
support the insertion and two support the reference. The repeated bases
nearby make alignment inspection especially useful for this example.

![One-base insertion and aligned reads](screenshots/expanded_pass_variant_3.png)

## Revisiting the original examples

The earlier A>G candidate at `CM009322.1:3,189,512` now passes with DP 917
and AD 0,917. The T>A candidate at `CM009334.1:8,569,458` also passes, with
DP 970 and AD 3,967. These depths are much higher than the genome average,
so they need closer examination for repeats, mapping ambiguity, and duplicate
reads. High depth alone does not settle whether a call is reliable.

### Original SNP cluster with more reads

The wider view now contains a dense pileup beneath the VCF markers. It is
a clear visual contrast with the sparse original alignment, but this locus
is unusually deep and should not stand in for typical genome coverage.

![Expanded coverage at the original SNP cluster](screenshots/expanded_original_snp_cluster.png)

### Original SNP close-up

The orange G bases appear repeatedly beneath the original A>G call. This
provides much more usable support than the two observations in the first
run, while the unusually high depth remains a reason to check mapping.

![Expanded close-up at the original SNP](screenshots/expanded_original_snp_zoom.png)

### Original insertion region

Purple insertion markers remain visible in some reads, but the earlier
`CM009336.1:3,474,356 A>AAAT` call is absent from the expanded VCF in the
inspected interval. Nearby SNPs were called instead. The image therefore
shows an alignment feature that was not reported as that insertion by the
expanded workflow. The calls at the original loci are listed in
[original-loci-variants.tsv](results/original-loci-variants.tsv).

![Expanded reads at the original insertion region](screenshots/expanded_original_insertion.png)

The larger read set gave a much clearer picture of the sample, but some
features still need follow-up. Duplicates were not marked or removed, and
the maximum genome depth of 24,408 suggests that some regions behave very
differently from the average. I would prioritize the moderate-depth examples
for further checks, then examine strand support, mapping, and gene context.
Passing the filter and looking consistent in IGV are useful evidence;
independent validation would still be needed to confirm a biological change
or connect it to CRISPR editing.

## Reproduce these results

Follow the environment and reference setup in the [main report](../README.md),
then run these commands from `Week-7/expanded`:

```bash
make all THREADS=4 SORT_THREADS=2
make stats
make validate
make igv
# For Windows IGV when running the analysis in WSL:
make igv IGV_ROOT=C:/path/to/BMB852
```

In IGV, choose **Tools > Run Batch Script** and open
`Week-7/expanded/scripts/igv_local_batch.txt`. The script recreates the
views and saves the screenshots. Generated scripts and sessions contain
local paths and are excluded from Git. Large FASTQ and BAM files are also
kept local; the Makefile regenerates them.

BWA 0.7.19, Cutadapt 5.2, Samtools 1.22.1, and BCFtools 1.24 were used.
The [validation log](provenance/validation.log) confirms BAM integrity,
reference agreement for PASS alleles, and the saved file hashes. It also
records a nonfatal MQ header warning. Additional records include the
[mapping report](results/flagstat.txt), [chromosome coverage](results/coverage.tsv),
[tool versions](provenance/tool-versions.txt), and [checksums](provenance/inputs.sha256).
