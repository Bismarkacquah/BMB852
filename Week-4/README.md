# Week 4: FASTQ quality control for *Physcomitrium patens*

## Objective

This assignment uses a controlled paired-end whole-genome sequencing subset
from *Physcomitrium patens* (a moss). The reads are downloaded from SRA,
summarized with SeqKit, trimmed with Cutadapt, and compared with FastQC before
and after trimming. The run was selected because it is an uncommon organism
with paired-end Illumina WGS data and approximately 150 bp reads.

## Selected experiment

The selected run is [ERR8982185](https://www.ebi.ac.uk/ena/browser/view/ERR8982185).
ENA identifies it as:

- Organism: *Physcomitrium patens*
- Taxonomy ID: `3218`
- Study: `PRJEB51295`
- Sample: `SAMEA13207856`
- Experiment: `ERX8525940`
- Platform: Illumina NovaSeq 6000
- Strategy: `WGS`
- Source: `GENOMIC`
- Layout: paired-end
- Reported reads: 115,685,656
- Reported bases: 17,415,839,111

Only the first 1,000 spots were used for this reproducible teaching analysis.
The metadata is saved in `results/ena_ERR8982185.tsv`.

## Workflow

From the `Week-4` directory:

```powershell
New-Item -ItemType Directory -Path data/raw -Force
fastq-dump --split-files --gzip --maxSpotId 1000 --outdir data/raw ERR8982185
seqkit stats data/raw/ERR8982185_1.fastq.gz data/raw/ERR8982185_2.fastq.gz
fastqc data/raw/ERR8982185_1.fastq.gz data/raw/ERR8982185_2.fastq.gz
cutadapt -j 0 -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA `
  -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT -q 20,20 -m 30 `
  -o data/trimmed/ERR8982185_1.trimmed.fastq.gz `
  -p data/trimmed/ERR8982185_2.trimmed.fastq.gz `
  data/raw/ERR8982185_1.fastq.gz data/raw/ERR8982185_2.fastq.gz
fastqc data/trimmed/ERR8982185_1.trimmed.fastq.gz `
  data/trimmed/ERR8982185_2.trimmed.fastq.gz
```

The [Makefile](Makefile) uses `ERR8982185` as its default accession and `1000`
as its default subset size. On Linux or WSL, the workflow stages are:

```bash
make metadata
make download
make stats
make qc-raw
make trim
make stats-trimmed
make qc-trimmed
```

## Read statistics

The raw subset contains 1,000 reads in each mate file. The reads are about
151 bp, with a small number of shorter records already present in the source
run:

| File | Reads | Total bases | Minimum | Average | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ERR8982185_1.fastq.gz` | 1,000 | 146,679 | 52 | 146.7 | 151 |
| `ERR8982185_2.fastq.gz` | 1,000 | 145,986 | 32 | 146.0 | 151 |

After Cutadapt:

| File | Reads | Total bases | Minimum | Average | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ERR8982185_1.trimmed.fastq.gz` | 997 | 146,115 | 50 | 146.6 | 151 |
| `ERR8982185_2.trimmed.fastq.gz` | 997 | 145,439 | 32 | 145.9 | 151 |

Cutadapt detected adapters in 34 R1 reads (3.4%) and 33 R2 reads (3.3%). Three
read pairs were removed for being shorter than 30 bp after quality trimming.
The raw reads remain unchanged, and pairing is preserved in the trimmed files.

## FastQC reports

| | Read 1 | Read 2 |
| --- | --- | --- |
| Raw | [FastQC report](results/qc/raw/ERR8982185_1_fastqc.html) | [FastQC report](results/qc/raw/ERR8982185_2_fastqc.html) |
| Trimmed | [FastQC report](results/qc/trimmed/ERR8982185_1.trimmed_fastqc.html) | [FastQC report](results/qc/trimmed/ERR8982185_2.trimmed_fastqc.html) |

The complete gallery is shown below. Each graph links to its full-resolution
PNG under `results/qc/figures/err8982185/`.

### Read 1 figures

| Module | Raw R1 | Trimmed R1 |
| --- | --- | --- |
| Per-base quality | [<img src="results/qc/figures/err8982185/raw/R1/per_base_quality.png" width="100%">](results/qc/figures/err8982185/raw/R1/per_base_quality.png) | [<img src="results/qc/figures/err8982185/trimmed/R1/per_base_quality.png" width="100%">](results/qc/figures/err8982185/trimmed/R1/per_base_quality.png) |
| Per-sequence quality | [<img src="results/qc/figures/err8982185/raw/R1/per_sequence_quality.png" width="100%">](results/qc/figures/err8982185/raw/R1/per_sequence_quality.png) | [<img src="results/qc/figures/err8982185/trimmed/R1/per_sequence_quality.png" width="100%">](results/qc/figures/err8982185/trimmed/R1/per_sequence_quality.png) |
| Base composition | [<img src="results/qc/figures/err8982185/raw/R1/per_base_sequence_content.png" width="100%">](results/qc/figures/err8982185/raw/R1/per_base_sequence_content.png) | [<img src="results/qc/figures/err8982185/trimmed/R1/per_base_sequence_content.png" width="100%">](results/qc/figures/err8982185/trimmed/R1/per_base_sequence_content.png) |
| GC content | [<img src="results/qc/figures/err8982185/raw/R1/per_sequence_gc_content.png" width="100%">](results/qc/figures/err8982185/raw/R1/per_sequence_gc_content.png) | [<img src="results/qc/figures/err8982185/trimmed/R1/per_sequence_gc_content.png" width="100%">](results/qc/figures/err8982185/trimmed/R1/per_sequence_gc_content.png) |
| Sequence length | [<img src="results/qc/figures/err8982185/raw/R1/sequence_length_distribution.png" width="100%">](results/qc/figures/err8982185/raw/R1/sequence_length_distribution.png) | [<img src="results/qc/figures/err8982185/trimmed/R1/sequence_length_distribution.png" width="100%">](results/qc/figures/err8982185/trimmed/R1/sequence_length_distribution.png) |
| Adapter content | [<img src="results/qc/figures/err8982185/raw/R1/adapter_content.png" width="100%">](results/qc/figures/err8982185/raw/R1/adapter_content.png) | [<img src="results/qc/figures/err8982185/trimmed/R1/adapter_content.png" width="100%">](results/qc/figures/err8982185/trimmed/R1/adapter_content.png) |
| N content | [<img src="results/qc/figures/err8982185/raw/R1/per_base_n_content.png" width="100%">](results/qc/figures/err8982185/raw/R1/per_base_n_content.png) | [<img src="results/qc/figures/err8982185/trimmed/R1/per_base_n_content.png" width="100%">](results/qc/figures/err8982185/trimmed/R1/per_base_n_content.png) |
| Duplication | [<img src="results/qc/figures/err8982185/raw/R1/duplication_levels.png" width="100%">](results/qc/figures/err8982185/raw/R1/duplication_levels.png) | [<img src="results/qc/figures/err8982185/trimmed/R1/duplication_levels.png" width="100%">](results/qc/figures/err8982185/trimmed/R1/duplication_levels.png) |

### Read 2 figures

| Module | Raw R2 | Trimmed R2 |
| --- | --- | --- |
| Per-base quality | [<img src="results/qc/figures/err8982185/raw/R2/per_base_quality.png" width="100%">](results/qc/figures/err8982185/raw/R2/per_base_quality.png) | [<img src="results/qc/figures/err8982185/trimmed/R2/per_base_quality.png" width="100%">](results/qc/figures/err8982185/trimmed/R2/per_base_quality.png) |
| Per-sequence quality | [<img src="results/qc/figures/err8982185/raw/R2/per_sequence_quality.png" width="100%">](results/qc/figures/err8982185/raw/R2/per_sequence_quality.png) | [<img src="results/qc/figures/err8982185/trimmed/R2/per_sequence_quality.png" width="100%">](results/qc/figures/err8982185/trimmed/R2/per_sequence_quality.png) |
| Base composition | [<img src="results/qc/figures/err8982185/raw/R2/per_base_sequence_content.png" width="100%">](results/qc/figures/err8982185/raw/R2/per_base_sequence_content.png) | [<img src="results/qc/figures/err8982185/trimmed/R2/per_base_sequence_content.png" width="100%">](results/qc/figures/err8982185/trimmed/R2/per_base_sequence_content.png) |
| GC content | [<img src="results/qc/figures/err8982185/raw/R2/per_sequence_gc_content.png" width="100%">](results/qc/figures/err8982185/raw/R2/per_sequence_gc_content.png) | [<img src="results/qc/figures/err8982185/trimmed/R2/per_sequence_gc_content.png" width="100%">](results/qc/figures/err8982185/trimmed/R2/per_sequence_gc_content.png) |
| Sequence length | [<img src="results/qc/figures/err8982185/raw/R2/sequence_length_distribution.png" width="100%">](results/qc/figures/err8982185/raw/R2/sequence_length_distribution.png) | [<img src="results/qc/figures/err8982185/trimmed/R2/sequence_length_distribution.png" width="100%">](results/qc/figures/err8982185/trimmed/R2/sequence_length_distribution.png) |
| Adapter content | [<img src="results/qc/figures/err8982185/raw/R2/adapter_content.png" width="100%">](results/qc/figures/err8982185/raw/R2/adapter_content.png) | [<img src="results/qc/figures/err8982185/trimmed/R2/adapter_content.png" width="100%">](results/qc/figures/err8982185/trimmed/R2/adapter_content.png) |
| N content | [<img src="results/qc/figures/err8982185/raw/R2/per_base_n_content.png" width="100%">](results/qc/figures/err8982185/raw/R2/per_base_n_content.png) | [<img src="results/qc/figures/err8982185/trimmed/R2/per_base_n_content.png" width="100%">](results/qc/figures/err8982185/trimmed/R2/per_base_n_content.png) |
| Duplication | [<img src="results/qc/figures/err8982185/raw/R2/duplication_levels.png" width="100%">](results/qc/figures/err8982185/raw/R2/duplication_levels.png) | [<img src="results/qc/figures/err8982185/trimmed/R2/duplication_levels.png" width="100%">](results/qc/figures/err8982185/trimmed/R2/duplication_levels.png) |

## Interpretation

This run is a good fit for the assignment because it provides nearly 150 bp
paired-end reads from an uncommon plant species. The raw files contain some
shorter records, but most reads reach 151 bp. Cutadapt removed a small number
of adapter-containing or low-quality ends and retained 997 of the 1,000 pairs.

The raw and trimmed FastQC reports should be read together. The main expected
change is improved read-end quality and lower adapter content after trimming.
The remaining composition, GC, duplication, and tile results should be checked
before mapping. The old Drosophila reference from Week 2 must not be used for
this dataset. Any future mapping or coverage analysis requires a matching
*Physcomitrium patens* reference assembly and annotation.

## Reproducibility checklist

```powershell
Test-Path data/raw/ERR8982185_1.fastq.gz
Test-Path data/raw/ERR8982185_2.fastq.gz
Test-Path data/trimmed/ERR8982185_1.trimmed.fastq.gz
Test-Path data/trimmed/ERR8982185_2.trimmed.fastq.gz
Test-Path results/ena_ERR8982185.tsv
Test-Path results/qc/raw/ERR8982185_1_fastqc.html
Test-Path results/qc/raw/ERR8982185_2_fastqc.html
Test-Path results/qc/trimmed/ERR8982185_1.trimmed_fastqc.html
Test-Path results/qc/trimmed/ERR8982185_2.trimmed_fastqc.html
```

Only 1,000 spots were analyzed. The full ENA run is much larger, so conclusions
about genome-wide coverage should not be generalized from this subset alone.
