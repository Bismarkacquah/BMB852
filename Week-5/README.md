# Assignment 5: BAM alignment of *Physcomitrium patens*

## Organism

The organism is the moss *Physcomitrium patens*. Week 5 reuses the reference
assembly from Week 2 and the trimmed paired-end reads from Week 4.

- Assembly: `GCA_000002425.2_Phypa_V3`
- Genome: `../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.fna`
- Annotation: `../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.gff`
- Reads: `../Week-4/data/trimmed/ERR8982185_1.trimmed.fastq.gz` and `_2.trimmed.fastq.gz`

The reference, annotation, and reads all come from *P. patens*.

## Coverage target

The genome is approximately 471,852,792 bp. Each trimmed read pair contributes
about 292,665 bases. The estimated number of read pairs needed for 10x coverage
is:

```text
10 x 471,852,792 / 292,665 = approximately 16,122 read pairs
```

The available teaching subset contains 997 trimmed pairs, so this BAM is a
workflow demonstration rather than a 10x genome-wide analysis.

## Folder layout

The Week-5 directory is organized like this:

```text
Week-5/
├── bam/          BAM, BAI, and flagstat outputs; generated locally
├── coverage/     coverage and depth tables; generated locally
├── screenshots/  IGV screenshots
├── scripts/      IGV batch scripts
├── Makefile      reproducible workflow
└── README.md     assignment report
```

The large BAM and coverage files are ignored by Git. They can be recreated with
the Makefile.

## Makefile

Run from the `Week-5` directory:

```bash
make check-tools
make check-inputs
make estimate
make all THREADS=2
```

The workflow code is in [Makefile](Makefile).

### What each part does

- `REFERENCE` points to the Week-2 moss FASTA.
- `ANNOTATION` points to the Week-2 GFF3 annotation.
- `READ1` and `READ2` point to the Week-4 trimmed paired reads.
- `BAM_DIR` and `COVERAGE_DIR` organize generated outputs.
- `BAM`, `STATS`, `DEPTH`, and `COVERAGE` name output files.
- `THREADS ?= 2` sets two threads unless another value is supplied.
- `BWA` and `SAMTOOLS` allow the tool names to be overridden.
- `check-tools` verifies that BWA, Samtools, and Make are installed.
- `check-inputs` verifies the reference, annotation, and reads exist.
- `estimate` prints the read-pair calculation for 10x coverage.
- `index` builds the BWA reference index.
- `align` maps reads with BWA and pipes the SAM output to Samtools sort.
- `sort` checks that the sorted BAM exists.
- `index-bam` creates the `.bai` index required by IGV.
- `stats` writes the Samtools flagstat report.
- `coverage` writes one summary row per reference sequence.
- `depth` writes one row per reference position.
- `all` runs the statistics, coverage, and depth targets.
- `dirs` creates the BAM, coverage, screenshots, and scripts folders.
- `clean` removes generated BAM and coverage folders.

The central alignment command is:

```bash
bwa mem -t 2 \
  ../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.fna \
  ../Week-4/data/trimmed/ERR8982185_1.trimmed.fastq.gz \
  ../Week-4/data/trimmed/ERR8982185_2.trimmed.fastq.gz \
  | samtools sort -@ 2 -o bam/ERR8982185.sorted.bam
```

The pipe sends aligner output directly to sorting and avoids a large temporary
SAM file.

## Run outputs

After `make all THREADS=2`, the local output files are:

```text
bam/ERR8982185.sorted.bam
bam/ERR8982185.sorted.bam.bai
bam/ERR8982185.flagstat.txt
coverage/ERR8982185.coverage.tsv
coverage/ERR8982185.depth.tsv
```

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
paired percentage was 72.72%.

## Coverage results

Coverage was calculated with:

```bash
samtools coverage bam/ERR8982185.sorted.bam \
  > coverage/ERR8982185.coverage.tsv
samtools depth -aa bam/ERR8982185.sorted.bam \
  > coverage/ERR8982185.depth.tsv
```

The genome-wide covered fraction was approximately **0.043%**, with a
length-weighted mean depth of approximately **0.00045x**. Coverage is therefore
very uneven because the 997-pair subset is far below the approximately 16,122
pairs estimated for 10x coverage.

## IGV visualization

Load these files in IGV:

1. Genome: `../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.fna`
2. BAM: `bam/ERR8982185.sorted.bam`
3. Annotation: `../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.gff`

### Figure 1: mapped-read view

Coordinate: `CM009316.1:617,500-619,000`

![Mapped BAM reads](screenshots/week5_mapped_read_detail.png)

Gray blocks are aligned reads. Colored bases show differences from the reference.

### Figure 2: annotated gene locus

Coordinate: `CM009316.1:8,931-13,135`

![BAM at PHYPA_000001](screenshots/week5_PHYPA_000001_bam.png)

This view compares the BAM reads with the `PHYPA_000001` annotation.

### Figure 3: dense genome region

Coordinate: `CM009317.1:10,924,622-11,924,622`

![BAM at dense region](screenshots/week5_dense_region_bam.png)

This region contains 126 annotated genes, but the small read subset does not
provide uniform coverage.

## Summary

The reads were aligned to the matching *P. patens* reference and produced a
sorted, indexed BAM. The alignment rate was 75.93%, and 72.72% of reads were
properly paired. The subset is too small for 10x genome-wide coverage, so the
observed coverage is sparse and uneven. The BAM and IGV views show where reads
mapped and where their sequences differ from the reference.
