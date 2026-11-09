# Week 11: Evaluate gene expression coverages

I compared three Human Brain Reference (HBR) samples with three Universal Human Reference (UHR) samples using chromosome 22 RNA-seq coverage and transcript annotations in IGV. HBR is reference RNA from human brains; UHR is reference RNA pooled from ten cancer cell lines.

## Data and visualization

- [Assignment](https://www.biostarhandbook.com/courses/2026/appbio/rnaseq/rnaseq-assignment/)
- [Genome-based RNA-seq tutorial](https://www.biostarhandbook.com/courses/2026/appbio/rnaseq/rnaseq-genome/)
- [Tutorial data and sample descriptions](https://www.biostarhandbook.com/courses/2026/appbio/rnaseq/rnaseq-tutorial-data/)
- Data archive: `https://data.biostarhandbook.com/data/rnaseq-tutorial-2026.tar.gz`

I used the course's original [Makefile](Makefile) to index `fasta/chr22.genome.fa`, align all six single-end FASTQ files with HISAT2 (`--threads 4 --sensitive`), and generate sorted, indexed BAM files with samtools. Raw bigWig tracks were generated with `bamCoverage --binSize 1`, as in the tutorial. I also generated a second set with `--normalizeUsing CPM` to account for different mapped library sizes when estimating fold change.

In IGV 2.19.8, I loaded the supplied reference, all six coverage tracks, and `gtf/chr22.gtf`. **HBR replicates are blue; UHR replicates are orange.** Comparisons use a common linear y-axis range. Raw and normalized coverage are shown in separate sessions.

The answers are based on visual inspection in IGV. To check the numerical estimates, I read exact coverage values from the bigWig files at the visually selected loci. These checks are recorded in [coverage-values.tsv](coverage-values.tsv).

## 1. How do the sample types differ across a wide region?

Across **chr22:35,000,000–41,000,000**, HBR and UHR share many peak locations, but their relative peak heights differ. UHR has particularly prominent peaks around RPL3 and nearby loci, while HBR has stronger coverage at SYNGR1 when inspected more closely. The difference involves which genes and exons have strong coverage, rather than a uniform increase across the chromosome.

The difference remains visible after CPM normalization. Raw heights alone would be misleading because the input samples contain different numbers of reads. At this wide scale, IGV summarizes coverage into screen pixels, so the view is useful for patterns rather than exact per-base depth.

![CPM-normalized coverage across a six-million-base region; HBR blue and UHR orange](screenshots/10-wide-region-CPM.png)

## 2. How consistent are the replicates?

The replicates are qualitatively consistent within each sample type. Across the wide region and the RPL3, SYNGR1, and MB views, peaks generally occur at the same positions within a group. Their heights vary, so the replicates are not identical.

At the selected SYNGR1 terminal-exon interval, HBR mean coverage ranges from **274.6–313.9 CPM**, whereas UHR ranges from **8.1–9.7 CPM**. The variation within each group is much smaller than the separation between groups. This observation describes the inspected regions, not a genome-wide correlation measurement.

## 3. A gene with no detected expression

**OR11H1**, `ENSG00000130538.4`, at **chr22:15,528,158–15,529,139**, has no coverage across its annotated gene interval in any of the six samples. The exact maximum raw coverage within the gene is **0** for every sample.

One small UHR_2 signal is visible downstream of OR11H1, but it lies outside the annotated gene interval. I would describe OR11H1 as **not detectably expressed in these data**, rather than conclude that it can never be expressed.

![OR11H1 annotation with no coverage over the gene in any sample](screenshots/11-OR11H1.png)

## 4. A strongly expressed gene in all samples and its coverage

**RPL3**, `ENSG00000100316.15`, at **chr22:39,312,882–39,320,389**, has strong coverage over multiple exons in all six samples. Coverage drops between exons, consistent with spliced RNA-seq alignments.

The maximum raw per-base coverage within the annotated RPL3 interval is:

| Sample | Maximum raw coverage |
| --- | ---: |
| HBR_1 | 100 |
| HBR_2 | 97 |
| HBR_3 | 103 |
| UHR_1 | 564 |
| UHR_2 | 330 |
| UHR_3 | 453 |

These are peak depths, not gene-wide average coverage, transcript counts, or normalized expression values. The broad statement from the view is approximately **100-fold base coverage in HBR and several hundred-fold coverage in UHR** at the strongest positions.

![Strong RPL3 exon coverage in every sample; common raw scale of 0–600](screenshots/07-RPL3-unclipped.png)

## 5. Can the expressed transcripts be identified?

At **SYNGR1**, the HBR samples show substantial coverage over the long terminal exon at **chr22:39,381,696–39,385,588**. In the supplied GTF, this exon belongs to **SYNGR1-001**, transcript **ENST00000328933.9**. Coverage also occurs over its upstream exons, making this transcript a supported candidate.

Shorter annotated SYNGR1 transcripts end before this long terminal exon. They cannot, by themselves, explain the strong downstream coverage. However, shared upstream exons do not distinguish all isoforms, and coverage alone does not link every exon into a complete RNA molecule. I therefore cannot claim that SYNGR1-001 is the only expressed isoform or that all shorter isoforms are absent. Splice-junction evidence would strengthen a complete transcript assignment.

![SYNGR1 normalized coverage and expanded transcript annotations](screenshots/08-SYNGR1-CPM.png)

## 6. A differentially expressed gene/transcript and its fold change

**SYNGR1**, particularly the long terminal exon supporting SYNGR1-001, is clearly more strongly expressed in HBR than UHR.

For a reproducible comparison, I selected **chr22:39,382,500–39,383,500**, a 1,001-base interval inside that exon. The table reports average coverage across the same interval in every sample, using CPM-normalized tracks:

| Replicate | HBR mean coverage (CPM) | UHR mean coverage (CPM) |
| --- | ---: | ---: |
| 1 | 274.6 | 9.7 |
| 2 | 313.9 | 8.1 |
| 3 | 312.8 | 8.6 |
| Group mean | 300.5 | 8.8 |

**Estimated HBR/UHR fold change = 300.5 / 8.8 ≈ 34-fold.**

This quantifies the coverage difference in the selected exon interval, not an independently estimated abundance for the entire transcript. CPM uses mapped reads in these chromosome-22 BAMs; because this is a restricted tutorial dataset, the ratio is illustrative and is not a replacement for full-library normalization and differential-expression analysis.

## 7. Is it upregulated or downregulated?

Using **HBR relative to UHR** as the comparison, the SYNGR1 terminal-exon signal is **upregulated in HBR** by approximately 34-fold. Equivalently, it is lower in UHR. These reference samples are different RNA sources, so this describes a between-source expression difference rather than a demonstrated response to a treatment.

## 8. How certain is the difference, and why?

I am confident that the observed coverage difference is larger than a small random fluctuation in these tracks:

- Every HBR replicate is much higher than every UHR replicate.
- HBR values cluster around 275–314 CPM, while UHR values cluster around 8–10 CPM in the selected interval.
- The difference extends across a substantial exon region rather than appearing at one isolated base.
- It persists after library-size normalization.

This is strong visual evidence for a reproducible difference in this dataset. It does **not** establish a p-value or false-discovery rate. Sampling noise, mapping ambiguity, RNA composition, and the use of pooled reference RNA still limit interpretation. The three reference-sample replicates should not automatically be treated as independent human donors. Formal significance would require an appropriate count-based model and a confirmed replicate design.

## Local files

- `bam/`: six sorted alignment files and indexes.
- `bw/`: six raw bigWig coverage files.
- `bw-cpm/`: six CPM-normalized bigWig coverage files.
- [Raw IGV session](igv-session.xml) and [normalized IGV session](igv-cpm-session.xml).
- `screenshots/`: exported IGV views, including additional candidate loci inspected during assessment.
- [Coverage values](coverage-values.tsv): numerical checks for the selected genes and interval.

The large downloaded data, indexes, and local tool environments are excluded by `.gitignore`. IGV sessions use relative paths. To reopen them, regenerate the data in this folder using the tutorial, including both coverage sets, and keep the listed folder structure.
