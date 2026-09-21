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

The fixed 251 bp length in both mates is consistent with the metadata and shows
that this subset was not trimmed. Both mates pass the N-content, sequence
length, and duplication modules. However, the per-base quality failures and
the adapter-content failure in read 1 indicate that this raw subset should be
trimmed or filtered before downstream analysis.

For this dataset, the key questions are:

1. Do per-base quality scores remain high across the 251 positions?
2. Are GC-content and base-composition profiles consistent across the reads?
3. Is adapter content detected near the read ends?
4. Are duplication or overrepresented-sequence warnings present?
5. Do read 1 and read 2 show comparable quality?

The reports answer these questions as follows: per-base quality is not
acceptable across all positions; base composition and GC profiles need
investigation; adapter content is detected, especially in read 1; no
duplication warning was reported; and read 1 and read 2 are broadly similar
but not identical. Trimming improved the quality and adapter modules in both
mates, at the cost of discarding 10.8% of read pairs and producing variable
lengths. The persistent base-composition and GC warnings should be investigated
before downstream analysis.

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
