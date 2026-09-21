# Week 4: FASTQ quality control for SRR519926

## Objective

This assignment downloads a controlled paired-end FASTQ subset from SRA,
summarizes the reads, and evaluates their quality with FastQC. It replaces the
previous Lamin dataset in Week 4 only; the Week 2 annotation work is unchanged.

The selected experiment is ENA/SRA run **SRR519926**. ENA identifies it as an
Illumina MiSeq paired-end whole-genome sequencing run. The complete run has
400,596 reads and 201,099,192 bases. This assignment analyzes the first 1,000
spots so the workflow remains quick and reproducible.

## Assignment requirements covered

1. **Assess experimental evidence:** ENA/SRA metadata, platform, layout, and
   sequencing strategy are documented below.
2. **Download a FASTQ subset:** the first 1,000 spots are downloaded with
   `fastq-dump` and split into R1 and R2 files.
3. **Organize data:** reads and FastQC reports are stored under `fastq/`.
4. **Summarize reads:** SeqKit reports read counts, lengths, and base counts.
5. **Trim the reads:** Cutadapt removes Illumina adapters and quality-trims
   both mates while preserving pairing.
6. **Run QC:** FastQC generates reports for both raw and trimmed mates.
7. **Compare results:** the before-and-after findings are documented below.

## Evidence from ENA and SRA

The [ENA run report](https://www.ebi.ac.uk/ena/browser/view/SRR519926) records:

- Run: `SRR519926`
- Study: `PRJNA40075`
- Experiment: `SRX158902`
- Sample: `SAMN00839313`
- Library: `Solexa-80888`
- Platform: Illumina MiSeq
- Strategy: `WGS`
- Source: `GENOMIC`
- Layout: paired-end
- Reported data: 400,596 reads and 201,099,192 bases

The complete run is larger than the controlled teaching subset used here. The
metadata retrieved for this analysis is saved as
`results/ena_SRR519926.tsv`.

## Commands used

From the `Week-4` directory:

```powershell
New-Item -ItemType Directory -Path fastq -Force
fastq-dump -X 1000 -F --outdir fastq --split-files SRR519926
seqkit stats fastq/SRR519926_1.fastq fastq/SRR519926_2.fastq
fastqc fastq/SRR519926_1.fastq fastq/SRR519926_2.fastq
cutadapt -j 0 -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA \
   -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT -q 20,20 -m 30 \
   -o fastq/trimmed/SRR519926_1.trimmed.fastq \
   -p fastq/trimmed/SRR519926_2.trimmed.fastq \
   fastq/SRR519926_1.fastq fastq/SRR519926_2.fastq
fastqc fastq/trimmed/SRR519926_1.trimmed.fastq \
   fastq/trimmed/SRR519926_2.trimmed.fastq
```

The workflow is also represented by the accession-driven [Makefile](Makefile).
Its default accession is now `SRR519926` and its default subset size is `1000`.
On Linux or WSL, the complete workflow can be run with:

```bash
make metadata
make download
make stats
make qc-raw
```

## Read statistics

SeqKit produced the following result:

| File | Reads | Total bases | Minimum length | Average length | Maximum length |
| --- | ---: | ---: | ---: | ---: | ---: |
| `SRR519926_1.fastq` | 1,000 | 251,000 | 251 | 251 | 251 |
| `SRR519926_2.fastq` | 1,000 | 251,000 | 251 | 251 | 251 |

Both mates contain the same number of reads and have a fixed length of 251 bp.
This confirms that the downloaded subset is paired-end and that the two mate
files remain synchronized.

After Cutadapt:

| File | Reads | Total bases | Minimum length | Average length | Maximum length |
| --- | ---: | ---: | ---: | ---: | ---: |
| `SRR519926_1.trimmed.fastq` | 892 | 163,239 | 33 | 183.0 | 251 |
| `SRR519926_2.trimmed.fastq` | 892 | 105,134 | 31 | 117.9 | 207 |

Cutadapt retained 892 of 1,000 read pairs (89.2%). It detected adapters in
115 R1 reads (11.5%) and 57 R2 reads (5.7%). The 108 removed pairs were shorter
than 30 bp after quality trimming. The raw files remain unchanged.

## FastQC results

FastQC generated these reports:

| | Read 1 | Read 2 |
| --- | --- | --- |
| Raw | [FastQC report](results/qc/raw/SRR519926_1_fastqc.html) | [FastQC report](results/qc/raw/SRR519926_2_fastqc.html) |
| Trimmed | [FastQC report](results/qc/trimmed/SRR519926_1.trimmed_fastqc.html) | [FastQC report](results/qc/trimmed/SRR519926_2.trimmed_fastqc.html) |

### FastQC image gallery

Each image is shown at roughly half the README width and links to the full
resolution PNG. The larger tables compare raw and trimmed reads separately for
R1 and R2.

#### Read 1

| Module | Raw R1 | Trimmed R1 |
| --- | --- | --- |
| Per-base quality | [<img src="results/qc/figures/srr519926/raw/R1/per_base_quality.png" width="100%">](results/qc/figures/srr519926/raw/R1/per_base_quality.png) | [<img src="results/qc/figures/srr519926/trimmed/R1/per_base_quality.png" width="100%">](results/qc/figures/srr519926/trimmed/R1/per_base_quality.png) |
| Per-sequence quality | [<img src="results/qc/figures/srr519926/raw/R1/per_sequence_quality.png" width="100%">](results/qc/figures/srr519926/raw/R1/per_sequence_quality.png) | [<img src="results/qc/figures/srr519926/trimmed/R1/per_sequence_quality.png" width="100%">](results/qc/figures/srr519926/trimmed/R1/per_sequence_quality.png) |
| Per-base sequence content | [<img src="results/qc/figures/srr519926/raw/R1/per_base_sequence_content.png" width="100%">](results/qc/figures/srr519926/raw/R1/per_base_sequence_content.png) | [<img src="results/qc/figures/srr519926/trimmed/R1/per_base_sequence_content.png" width="100%">](results/qc/figures/srr519926/trimmed/R1/per_base_sequence_content.png) |
| GC content | [<img src="results/qc/figures/srr519926/raw/R1/per_sequence_gc_content.png" width="100%">](results/qc/figures/srr519926/raw/R1/per_sequence_gc_content.png) | [<img src="results/qc/figures/srr519926/trimmed/R1/per_sequence_gc_content.png" width="100%">](results/qc/figures/srr519926/trimmed/R1/per_sequence_gc_content.png) |
| Sequence length | [<img src="results/qc/figures/srr519926/raw/R1/sequence_length_distribution.png" width="100%">](results/qc/figures/srr519926/raw/R1/sequence_length_distribution.png) | [<img src="results/qc/figures/srr519926/trimmed/R1/sequence_length_distribution.png" width="100%">](results/qc/figures/srr519926/trimmed/R1/sequence_length_distribution.png) |
| Adapter content | [<img src="results/qc/figures/srr519926/raw/R1/adapter_content.png" width="100%">](results/qc/figures/srr519926/raw/R1/adapter_content.png) | [<img src="results/qc/figures/srr519926/trimmed/R1/adapter_content.png" width="100%">](results/qc/figures/srr519926/trimmed/R1/adapter_content.png) |
| N content | [<img src="results/qc/figures/srr519926/raw/R1/per_base_n_content.png" width="100%">](results/qc/figures/srr519926/raw/R1/per_base_n_content.png) | [<img src="results/qc/figures/srr519926/trimmed/R1/per_base_n_content.png" width="100%">](results/qc/figures/srr519926/trimmed/R1/per_base_n_content.png) |
| Duplication | [<img src="results/qc/figures/srr519926/raw/R1/duplication_levels.png" width="100%">](results/qc/figures/srr519926/raw/R1/duplication_levels.png) | [<img src="results/qc/figures/srr519926/trimmed/R1/duplication_levels.png" width="100%">](results/qc/figures/srr519926/trimmed/R1/duplication_levels.png) |

#### Read 2

| Module | Raw R2 | Trimmed R2 |
| --- | --- | --- |
| Per-base quality | [<img src="results/qc/figures/srr519926/raw/R2/per_base_quality.png" width="100%">](results/qc/figures/srr519926/raw/R2/per_base_quality.png) | [<img src="results/qc/figures/srr519926/trimmed/R2/per_base_quality.png" width="100%">](results/qc/figures/srr519926/trimmed/R2/per_base_quality.png) |
| Per-sequence quality | [<img src="results/qc/figures/srr519926/raw/R2/per_sequence_quality.png" width="100%">](results/qc/figures/srr519926/raw/R2/per_sequence_quality.png) | [<img src="results/qc/figures/srr519926/trimmed/R2/per_sequence_quality.png" width="100%">](results/qc/figures/srr519926/trimmed/R2/per_sequence_quality.png) |
| Per-base sequence content | [<img src="results/qc/figures/srr519926/raw/R2/per_base_sequence_content.png" width="100%">](results/qc/figures/srr519926/raw/R2/per_base_sequence_content.png) | [<img src="results/qc/figures/srr519926/trimmed/R2/per_base_sequence_content.png" width="100%">](results/qc/figures/srr519926/trimmed/R2/per_base_sequence_content.png) |
| GC content | [<img src="results/qc/figures/srr519926/raw/R2/per_sequence_gc_content.png" width="100%">](results/qc/figures/srr519926/raw/R2/per_sequence_gc_content.png) | [<img src="results/qc/figures/srr519926/trimmed/R2/per_sequence_gc_content.png" width="100%">](results/qc/figures/srr519926/trimmed/R2/per_sequence_gc_content.png) |
| Sequence length | [<img src="results/qc/figures/srr519926/raw/R2/sequence_length_distribution.png" width="100%">](results/qc/figures/srr519926/raw/R2/sequence_length_distribution.png) | [<img src="results/qc/figures/srr519926/trimmed/R2/sequence_length_distribution.png" width="100%">](results/qc/figures/srr519926/trimmed/R2/sequence_length_distribution.png) |
| Adapter content | [<img src="results/qc/figures/srr519926/raw/R2/adapter_content.png" width="100%">](results/qc/figures/srr519926/raw/R2/adapter_content.png) | [<img src="results/qc/figures/srr519926/trimmed/R2/adapter_content.png" width="100%">](results/qc/figures/srr519926/trimmed/R2/adapter_content.png) |
| N content | [<img src="results/qc/figures/srr519926/raw/R2/per_base_n_content.png" width="100%">](results/qc/figures/srr519926/raw/R2/per_base_n_content.png) | [<img src="results/qc/figures/srr519926/trimmed/R2/per_base_n_content.png" width="100%">](results/qc/figures/srr519926/trimmed/R2/per_base_n_content.png) |
| Duplication | [<img src="results/qc/figures/srr519926/raw/R2/duplication_levels.png" width="100%">](results/qc/figures/srr519926/raw/R2/duplication_levels.png) | [<img src="results/qc/figures/srr519926/trimmed/R2/duplication_levels.png" width="100%">](results/qc/figures/srr519926/trimmed/R2/duplication_levels.png) |

The reports inspect per-base quality, per-sequence quality, per-base sequence
content, GC content, sequence length, duplication, adapter content, and N
content. Read 1 and read 2 should be assessed separately because paired reads
can have different quality profiles.

The report is based on only 1,000 spots. It is therefore appropriate for a
workflow demonstration and initial QC inspection, but it should not be treated
as a complete characterization of the full SRR519926 run.

The trimmed reports show PASS for per-base quality, per-sequence quality,
adapter content, N content, and duplication in both mates. Per-base sequence
content remains a FAIL, while GC content and overrepresented sequences remain
warnings. Sequence length is now a warning because quality and adapter
trimming created variable-length reads; this is expected after trimming.

FastQC reported the following module outcomes:

| Module | Read 1 | Read 2 |
| --- | --- | --- |
| Basic statistics | PASS | PASS |
| Per-base sequence quality | FAIL | FAIL |
| Per-sequence quality scores | WARN | FAIL |
| Per-base sequence content | WARN | WARN |
| Per-sequence GC content | FAIL | WARN |
| Per-base N content | PASS | PASS |
| Sequence length distribution | PASS | PASS |
| Sequence duplication levels | PASS | PASS |
| Overrepresented sequences | WARN | WARN |
| Adapter content | FAIL | WARN |

## Interpretation

Both read files contain 251 bp reads, which matches the information reported for
this MiSeq run. The raw data passed the N-content, length, and duplication
checks, but the quality plots and adapter results show that the reads need some
cleaning before they are used for further analysis.

The main points I checked were:

1. Whether quality stayed high across the full read length.
2. Whether the GC and base-composition plots looked consistent.
3. Whether adapter sequence appeared near the read ends.
4. Whether there were duplication or overrepresented-sequence problems.
5. Whether R1 and R2 had similar quality profiles.

The raw reports showed problems with per-base quality and adapter content,
especially in R1. The two mates were broadly similar, although their quality
profiles were not identical. Duplication was not flagged, but the GC,
base-composition, and overrepresented-sequence results still deserve a closer
look.

After trimming, 892 of the 1,000 pairs remained. Quality and adapter checks
then passed for both mates. The trade-off is that the reads now have different
lengths, which is expected after removing adapters and low-quality ends. The
remaining composition and GC warnings should still be considered before
downstream analysis.

## Reproducibility checklist

From `Week-4`, verify that these files are non-empty:

```powershell
Test-Path fastq/SRR519926_1.fastq
Test-Path fastq/SRR519926_2.fastq
Test-Path fastq/SRR519926_1_fastqc.html
Test-Path fastq/SRR519926_2_fastqc.html
Test-Path fastq/trimmed/SRR519926_1.trimmed.fastq
Test-Path fastq/trimmed/SRR519926_2.trimmed.fastq
Test-Path results/qc/raw/SRR519926_1_fastqc.html
Test-Path results/qc/raw/SRR519926_2_fastqc.html
Test-Path results/qc/trimmed/SRR519926_1.trimmed_fastqc.html
Test-Path results/qc/trimmed/SRR519926_2.trimmed_fastqc.html
```

The workflow deliberately uses a subset. Processing all 400,596 reads is
possible by increasing the `-X` value or setting `N` when using the Makefile,
but the resulting QC conclusions should still be reported with the number of
reads analyzed.

## Scope and limitations

This Week-4 analysis concerns SRR519926 and does not modify the Week 2
annotation. The downloaded reads are genomic paired-end data, and FastQC
evaluates technical read quality rather than gene expression, gene function,
or biological effect.
