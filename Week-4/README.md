# Week 4: FASTQ quality control for *Drosophila melanogaster*

## Objective

This assignment uses a controlled paired-end whole-genome sequencing subset
from *Drosophila melanogaster*. The reads are downloaded from SRA, summarized
with SeqKit, trimmed with Cutadapt, and compared with FastQC before and after
trimming. The reference genome is the same *Drosophila* assembly used in Week 2:
`GCF_000001215.4_Release_6_plus_ISO1_MT`.

## Selected experiment

The selected run is [ERR12643030](https://www.ebi.ac.uk/ena/browser/view/ERR12643030).
ENA identifies it as:

- Organism: *Drosophila melanogaster*
- Taxonomy ID: `7227`
- Study: `PRJEB72380`
- Experiment: `ERX12017357`
- Platform: Illumina NextSeq 2000
- Strategy: `WGS`
- Source: `GENOMIC`
- Layout: paired-end
- Reported reads: 21,937,570
- Reported bases: 2,435,070,270

Only the first 1,000 spots were used for this reproducible teaching analysis.
The metadata is saved in `results/ena_ERR12643030.tsv`.

## Workflow

From the `Week-4` directory:

```powershell
New-Item -ItemType Directory -Path data/raw -Force
fastq-dump --split-files --gzip --maxSpotId 1000 --outdir data/raw ERR12643030
seqkit stats data/raw/ERR12643030_1.fastq.gz data/raw/ERR12643030_2.fastq.gz
fastqc --outdir results/qc/raw data/raw/ERR12643030_1.fastq.gz data/raw/ERR12643030_2.fastq.gz
cutadapt -j 0 -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA `
  -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT -q 20,20 -m 30 `
  -o data/trimmed/ERR12643030_1.trimmed.fastq.gz `
  -p data/trimmed/ERR12643030_2.trimmed.fastq.gz `
  data/raw/ERR12643030_1.fastq.gz data/raw/ERR12643030_2.fastq.gz
fastqc --outdir results/qc/trimmed data/trimmed/ERR12643030_1.trimmed.fastq.gz data/trimmed/ERR12643030_2.trimmed.fastq.gz
```

The [Makefile](Makefile) uses `ERR12643030` as its default accession and `1000`
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

The raw subset contains 1,000 reads in each mate file. Both mates are 111 bp:

| File | Reads | Total bases | Minimum | Average | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ERR12643030_1.fastq.gz` | 1,000 | 111,000 | 111 | 111 | 111 |
| `ERR12643030_2.fastq.gz` | 1,000 | 111,000 | 111 | 111 | 111 |

After Cutadapt, all 1,000 pairs were retained:

| File | Reads | Total bases | Minimum | Average | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ERR12643030_1.trimmed.fastq.gz` | 1,000 | 110,770 | 95 | 110.8 | 111 |
| `ERR12643030_2.trimmed.fastq.gz` | 1,000 | 110,718 | 99 | 110.7 | 111 |

Cutadapt detected adapters in 19 R1 reads (1.9%) and 9 R2 reads (0.9%). No
read pair was removed for being too short, so pairing was preserved.

## FastQC reports

| | Read 1 | Read 2 |
| --- | --- | --- |
| Raw | [FastQC report](results/qc/raw/ERR12643030_1_fastqc.html) | [FastQC report](results/qc/raw/ERR12643030_2_fastqc.html) |
| Trimmed | [FastQC report](results/qc/trimmed/ERR12643030_1.trimmed_fastqc.html) | [FastQC report](results/qc/trimmed/ERR12643030_2.trimmed_fastqc.html) |

The full-size PNG graphs are under `results/qc/figures/err12643030/`. They show
raw and trimmed comparisons for per-base quality, per-sequence quality, base
composition, GC content, sequence length, adapter content, and N content.

### Read 1 figures

| Module | Raw | Trimmed |
| --- | --- | --- |
| Per-base quality | [raw](results/qc/figures/err12643030/raw/R1/per_base_quality.png) | [trimmed](results/qc/figures/err12643030/trimmed/R1/per_base_quality.png) |
| Per-sequence quality | [raw](results/qc/figures/err12643030/raw/R1/per_sequence_quality.png) | [trimmed](results/qc/figures/err12643030/trimmed/R1/per_sequence_quality.png) |
| Base composition | [raw](results/qc/figures/err12643030/raw/R1/per_base_sequence_content.png) | [trimmed](results/qc/figures/err12643030/trimmed/R1/per_base_sequence_content.png) |
| GC content | [raw](results/qc/figures/err12643030/raw/R1/per_sequence_gc_content.png) | [trimmed](results/qc/figures/err12643030/trimmed/R1/per_sequence_gc_content.png) |
| Sequence length | [raw](results/qc/figures/err12643030/raw/R1/sequence_length_distribution.png) | [trimmed](results/qc/figures/err12643030/trimmed/R1/sequence_length_distribution.png) |
| Adapter content | [raw](results/qc/figures/err12643030/raw/R1/adapter_content.png) | [trimmed](results/qc/figures/err12643030/trimmed/R1/adapter_content.png) |

### Read 2 figures

| Module | Raw | Trimmed |
| --- | --- | --- |
| Per-base quality | [raw](results/qc/figures/err12643030/raw/R2/per_base_quality.png) | [trimmed](results/qc/figures/err12643030/trimmed/R2/per_base_quality.png) |
| Per-sequence quality | [raw](results/qc/figures/err12643030/raw/R2/per_sequence_quality.png) | [trimmed](results/qc/figures/err12643030/trimmed/R2/per_sequence_quality.png) |
| Base composition | [raw](results/qc/figures/err12643030/raw/R2/per_base_sequence_content.png) | [trimmed](results/qc/figures/err12643030/trimmed/R2/per_base_sequence_content.png) |
| GC content | [raw](results/qc/figures/err12643030/raw/R2/per_sequence_gc_content.png) | [trimmed](results/qc/figures/err12643030/trimmed/R2/per_sequence_gc_content.png) |
| Sequence length | [raw](results/qc/figures/err12643030/raw/R2/sequence_length_distribution.png) | [trimmed](results/qc/figures/err12643030/trimmed/R2/sequence_length_distribution.png) |
| Adapter content | [raw](results/qc/figures/err12643030/raw/R2/adapter_content.png) | [trimmed](results/qc/figures/err12643030/trimmed/R2/adapter_content.png) |

## Interpretation

The raw reads match the selected Drosophila WGS experiment: both mates contain
1,000 reads of 111 bp. Adapter contamination was low, and trimming retained
every pair. The trimmed files lost only 230 bases from R1 and 282 bases from R2
in total, so this subset was already in good technical condition.

The raw and trimmed FastQC reports should be read together. The main expected
change is a small improvement at the read ends after quality and adapter
trimming, while the fixed raw length becomes slightly variable in the trimmed
files. Since these are WGS reads from *Drosophila melanogaster*, the Week 2
assembly and annotation are appropriate references for later mapping or genome
coverage analysis.

## Reproducibility checklist

```powershell
Test-Path data/raw/ERR12643030_1.fastq.gz
Test-Path data/raw/ERR12643030_2.fastq.gz
Test-Path data/trimmed/ERR12643030_1.trimmed.fastq.gz
Test-Path data/trimmed/ERR12643030_2.trimmed.fastq.gz
Test-Path results/qc/raw/ERR12643030_1_fastqc.html
Test-Path results/qc/raw/ERR12643030_2_fastqc.html
Test-Path results/qc/trimmed/ERR12643030_1.trimmed_fastqc.html
Test-Path results/qc/trimmed/ERR12643030_2.trimmed_fastqc.html
```

Only 1,000 spots were analyzed. The full ENA run is much larger, so conclusions
about genome-wide coverage should not be generalized from this subset alone.
