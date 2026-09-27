# Assignment 5: BAM alignment of *Physcomitrium patens*

## Organism

The organism is the moss *Physcomitrium patens*. Week 5 uses the same reference
assembly and trimmed paired-end reads established in Weeks 2 and 4.

- Assembly: `GCA_000002425.2_Phypa_V3`
- Genome: `../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.fna`
- Annotation: `../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.gff`
- Reads: `../Week-4/data/trimmed/ERR8982185_1.trimmed.fastq.gz` and `_2.trimmed.fastq.gz`

The reference, annotation, and reads all come from *P. patens*, so the alignment
is biologically appropriate.

## Coverage target

The genome is approximately 471,852,792 bp. Each trimmed read pair contributes
about 292,665 bases. The estimated number of read pairs needed for 10x coverage
is:

```text
10 x 471,852,792 / 292,665 = approximately 16,122 read pairs
```

The available teaching subset contains 997 trimmed pairs, so this BAM is a
workflow demonstration rather than a 10x genome-wide analysis.

## Makefile

Run from the `Week-5` directory:

```bash
make check-tools
make check-inputs
make estimate
make all THREADS=2
```

The Makefile performs these steps:

1. Build a BWA reference index.
2. Align paired FASTQ reads with `bwa mem`.
3. Sort the alignments with `samtools sort`.
4. Index the BAM with `samtools index`.
5. Write `samtools flagstat` statistics.
6. Write per-contig coverage with `samtools coverage`.
7. Write per-position depth with `samtools depth -aa`.

The main code is in [Makefile](Makefile). The IGV batch commands are in
`scripts/`.

## Run confirmation

The completed local outputs are organized as:

```text
bam/ERR8982185.sorted.bam
bam/ERR8982185.sorted.bam.bai
bam/ERR8982185.flagstat.txt
coverage/ERR8982185.coverage.tsv
coverage/ERR8982185.depth.tsv
```

The large BAM and coverage files remain local and are ignored by Git. The
reproducible Makefile, README, scripts, and screenshots are published.

## BAM statistics

The `samtools flagstat` report gave:

```text
1998 reads in total
1517 reads mapped (75.93%)
1450 reads properly paired (72.72%)
33 singleton reads (1.65%)
0 duplicate reads
4 supplementary alignments
```

About 75.93% of the reads mapped to the matching moss reference. The properly
paired percentage was 72.72%. The mapping rate should be interpreted cautiously
because only 997 pairs were analyzed.

## Coverage results

Coverage was calculated with:

```bash
samtools coverage bam/ERR8982185.sorted.bam > coverage/ERR8982185.coverage.tsv
samtools depth -aa bam/ERR8982185.sorted.bam > coverage/ERR8982185.depth.tsv
```

The genome-wide covered fraction was approximately **0.043%**, with a
length-weighted mean depth of approximately **0.00045x**. Coverage is therefore
very uneven: some small regions contain reads, while most of the 471.9 Mb
reference has no reads in this teaching subset. A larger dataset near 16,122
pairs is needed for a meaningful 10x genome-wide assessment.

## IGV visualization

Load these files in IGV:

1. Genome: `../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.fna`
2. BAM: `bam/ERR8982185.sorted.bam`
3. Annotation: `../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.gff`

### BAM alignment view

Coordinate: `CM009316.1:617,500-619,000`

![Mapped BAM reads](screenshots/week5_mapped_read_detail.png)

**Figure 1.** Mapped paired reads and sequence differences in IGV. Gray blocks
are aligned reads; colored bases indicate differences from the reference.

### Gene-locus view

Coordinate: `CM009316.1:8,931-13,135`

![BAM at PHYPA_000001](screenshots/week5_PHYPA_000001_bam.png)

**Figure 2.** BAM and annotation at the `PHYPA_000001` locus from Week 2.

### Dense-region view

Coordinate: `CM009317.1:10,924,622-11,924,622`

![BAM at dense region](screenshots/week5_dense_region_bam.png)

**Figure 3.** BAM view at the dense one-megabase moss region. The annotation is
dense, but the small subset does not provide uniform read coverage.

## Summary

The reads were aligned to the matching *P. patens* reference and produced a
sorted, indexed BAM. The alignment rate was 75.93%, with 72.72% properly paired.
The low coverage is expected because only 997 pairs were used against a 471.9
Mb genome. IGV confirms that reads are present at supported coordinates and
shows sequence differences relative to the reference. The final 10x analysis
requires approximately 16,122 paired reads.
