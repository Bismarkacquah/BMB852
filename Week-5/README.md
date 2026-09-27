# Assignment 5: Generate a BAM file for *Physcomitrium patens*

## Organism

This assignment uses the same *Physcomitrium patens* genome and sequencing
reads established in Weeks 2 and 4.

- Assembly: `GCA_000002425.2_Phypa_V3`
- Genome: `../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.fna`
- Annotation: `../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.gff`
- Read 1: `../Week-4/data/trimmed/ERR8982185_1.trimmed.fastq.gz`
- Read 2: `../Week-4/data/trimmed/ERR8982185_2.trimmed.fastq.gz`

The reads are paired-end Illumina WGS data from *P. patens*. The reference and
reads are reused directly rather than copied into Week 5.

This is an appropriate pairing because the genome, annotation, and sequencing
reads all come from the same organism and assembly.

## Coverage planning

The genome is approximately 471,852,792 bp. Each trimmed read pair contributes
about 292,665 bases. To estimate the number of pairs needed for 10x coverage:

```text
10 x 471,852,792 / 292,665 = approximately 16,122 read pairs
```

The current Week-4 teaching subset contains 997 trimmed pairs, so it is much
smaller than the estimated 10x requirement. The BAM produced here is therefore
a workflow demonstration, not a complete genome-wide coverage experiment.

## Makefile

The Makefile automates the alignment process:

```bash
make check-tools
make check-inputs
make estimate
make all THREADS=2
```

The complete workflow is in [Makefile](Makefile). It defines the reference,
annotation, paired FASTQ files, BAM name, statistics file, and coverage files
before running the dependent alignment steps.

The important commands executed by the Makefile are:

```bash
bwa index ../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.fna

bwa mem -t 2 \
  ../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.fna \
  ../Week-4/data/trimmed/ERR8982185_1.trimmed.fastq.gz \
  ../Week-4/data/trimmed/ERR8982185_2.trimmed.fastq.gz \
  | samtools sort -@ 2 \
  -o results/alignments/ERR8982185.sorted.bam

samtools index results/alignments/ERR8982185.sorted.bam
samtools flagstat results/alignments/ERR8982185.sorted.bam \
  > results/alignments/ERR8982185.flagstat.txt

samtools depth -aa results/alignments/ERR8982185.sorted.bam \
  > results/coverage/ERR8982185.depth.tsv
```

`bwa index` prepares the reference for fast alignment. `bwa mem` aligns the
paired reads. `samtools sort` creates a coordinate-sorted BAM, `samtools index`
creates the `.bai` index required by IGV, `flagstat` summarizes alignment
status, and `depth` reports coverage at each reference position.

## Run the Makefile

The completed workflow generated these local files locally:

```text
results/alignments/ERR8982185.sorted.bam
results/alignments/ERR8982185.sorted.bam.bai
results/alignments/ERR8982185.flagstat.txt
results/coverage/ERR8982185.depth.tsv
results/coverage/ERR8982185.coverage.tsv
```

The BAM and depth table are intentionally kept local because they are generated
binary/large outputs. The Makefile, README, commands, and IGV screenshot are
published in the repository.

## BAM file statistics

The `samtools flagstat` output reported:

```text
1998 reads in total
1517 reads mapped (75.93%)
1450 reads properly paired (72.72%)
33 singleton reads (1.65%)
0 duplicate reads
4 supplementary alignments
```

Approximately 75.93% of the reads aligned to the matching moss reference. The
properly paired percentage was 72.72%. The mapping rate is reasonable for a
small teaching subset, but it should not be interpreted as a complete estimate
of the full experiment because only 997 pairs were processed.

## Coverage results

The per-contig coverage summary is generated with:

```bash
samtools coverage results/alignments/ERR8982185.sorted.bam \
  > results/coverage/ERR8982185.coverage.tsv
```

The per-contig `samtools coverage` summary showed that the genome-wide coverage
was extremely sparse for this small subset. The estimated covered fraction was
approximately **0.043%**, with a length-weighted mean depth of approximately
**0.00045x** across the full 471.9 Mb reference.

Coverage is therefore not uniform. Some small regions contain aligned reads,
while most of the reference has zero coverage. This is expected because the
assignment subset is far below the approximately 16,122 pairs needed for 10x
coverage.

## IGV visualization

IGV was opened with the matching moss FASTA, the Week-5 sorted BAM, and the
Week-2 annotation. The BAM index allows IGV to navigate to specific regions.

### Mapped-read view

Coordinate:

```text
CM009316.1:617,500-619,000
```

This coordinate was selected because the BAM contains mapped reads there.
Gray read blocks show alignments, while colored bases show differences between
reads and the reference. Repeated differences across many reads may represent
real variation; isolated differences may be sequencing errors or alignment
artifacts.

![Mapped BAM reads in IGV](results/igv/week5_mapped_read_detail.png)

**Figure 1.** Week-5 BAM alignment view at a region containing mapped paired
reads.

### Annotation-locus view

Coordinate:

```text
CM009316.1:8,931-13,135
```

This is the `PHYPA_000001` example locus used in Week 2. The annotation is
useful for comparing reads with gene structure, although the small subset did
not produce strong coverage at this locus.

![BAM at PHYPA_000001](results/igv/week5_PHYPA_000001_bam.png)

**Figure 2.** BAM and moss annotation view at the `PHYPA_000001` locus.

### Dense-region view

Coordinate:

```text
CM009317.1:10,924,622-11,924,622
```

This is the dense one-megabase annotation region from Week 2. It contains 126
annotated genes, but the small Week-5 subset does not provide uniform read
coverage across the interval.

![BAM at dense annotation region](results/igv/week5_dense_region_bam.png)

**Figure 3.** BAM view at the dense moss annotation region.

## Summary

- The matching moss genome and Week-4 reads were used consistently.
- The BAM is sorted and indexed for IGV.
- 75.93% of reads mapped and 72.72% were properly paired.
- The subset is far too small to provide 10x genome-wide coverage.
- Coverage is highly uneven, with only about 0.043% of the reference covered.
- IGV shows mapped reads and sequence differences at supported coordinates.
- A larger read subset is required for meaningful genome-wide coverage analysis.

Overall, the reads align to the matching moss genome, but this small subset is
not large enough for uniform genome-wide coverage. The BAM and IGV views show
where the reads aligned and where sequence differences occur. The final
10x-oriented analysis should use approximately 16,122 paired reads rather than
the 997-pair teaching subset used here.
