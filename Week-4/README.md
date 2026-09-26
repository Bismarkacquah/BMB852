# Week 4: FASTQ quality control for *Physcomitrium patens*

## Objective

This assignment uses a controlled paired-end whole-genome sequencing subset
from *Physcomitrium patens* (a moss). The reads are downloaded from SRA,
summarized with SeqKit, trimmed with Cutadapt, and compared with FastQC before
and after trimming. The run was selected because it is an uncommon organism
with paired-end Illumina WGS data and approximately 150 bp reads.

In plain terms, this report asks three questions:

1. What sequencing experiment was used?
2. Were the downloaded reads technically reliable?
3. Did trimming improve the reads without removing most of the data?

FastQC measures technical sequencing quality. It does not identify genes or
prove that a read belongs to a particular biological pathway. Those questions
require a later mapping and annotation workflow.

## Background information

*Physcomitrium patens* has a much smaller public sequencing record than common
human, mouse, or *Drosophila* datasets, but it is still well represented in
public archives. An ENA search for taxonomy ID `3218` returned **2,387 public
sequencing runs** on 26 September 2026. These are run records, not 2,387
different genome assemblies; several runs can belong to the same study or
sample.

The public records are varied:

| Category | Public runs |
| --- | ---: |
| Genomic source | 451 |
| Genomic single-cell source | 14 |
| Paired-end layout | 1,313 |
| Single-end layout | 1,074 |
| Illumina platform | 1,952 |
| Oxford Nanopore platform | 11 |
| WGS strategy | 87 |
| WGA strategy | 143 |
| RNA-seq strategy | 1,586 |
| ChIP-seq strategy | 158 |

This shows why the accession must be checked instead of choosing a dataset only
by species name. The selected run, `ERR8982185`, is one of the paired-end,
Illumina, genomic WGS records. That makes it appropriate for read-quality
assessment and possible whole-genome mapping after a matching moss reference
assembly is obtained.

The counts were collected with the ENA Portal API:

```text
https://www.ebi.ac.uk/ena/portal/api/search?result=read_run&query=tax_eq(3218)
```

The public-data summary describes archive availability, not the quality of all
2,387 runs. FastQC results in this report come only from the first 1,000 spots
of `ERR8982185`.

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

### What each step does

- `fastq-dump` retrieves the first 1,000 sequencing spots and separates the
  paired reads into R1 and R2 files.
- `seqkit stats` counts reads and bases and reports minimum, average, and
  maximum read lengths.
- `fastqc` checks the raw reads and creates one HTML report for each mate.
- `cutadapt` removes Illumina adapter sequences, trims bases below Q20 at the
  read ends, and removes pairs shorter than 30 bp.
- The second FastQC run checks whether the cleaned reads improved.

The raw files are kept unchanged. The trimmed files are separate so that the
before-and-after comparison remains reproducible.

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

### How to read the gallery

In each table, the left graph is the raw read and the right graph is the
trimmed read. R1 and R2 are the two mates from the same paired-end experiment.
The yellow boxes in the per-base quality graph show the middle 50% of quality
values at each position; the red line is the median and the whiskers show the
wider spread. The graph reaches about 151 positions because these reads are
about 151 bp long.

FastQC labels a module as PASS, WARN, or FAIL. A warning means the result needs
context, and a failure means it should be investigated. Neither label alone
proves that the entire sequencing experiment is unusable.

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

### What the individual modules mean

- **Per-base sequence quality:** shows the quality distribution at every base
  position. The yellow box contains the middle 50% of quality values, the red
  line is the median, and the whiskers show the wider spread. The x-axis reaches
  about 151 bp because these reads are about 151 bp long.
- **Per-sequence quality:** shows how many reads have each average quality
  score. A peak toward the high-quality end means most complete reads are
  reliable.
- **Per-base sequence content:** shows the percentage of A, C, G, and T at each
  position. Unexpected shifts can indicate library bias, primer effects, or
  another non-random sequence feature.
- **GC content:** compares the GC distribution of the reads with the expected
  profile. A shifted or unusually broad distribution can reflect real genome
  composition, mixed material, contamination, or technical bias.
- **Sequence length distribution:** shows whether reads have one fixed length or
  a mixture of lengths. Trimming normally makes this distribution more varied.
- **Adapter content:** estimates how much adapter sequence remains at each
  position. A reduction after Cutadapt shows that adapter removal worked.
- **N content:** shows positions where the sequencer could not confidently call
  A, C, G, or T. High N content means uncertain bases.
- **Duplication levels:** shows how often identical sequences occur. Some
  duplication can be expected in a small subset, so it should be interpreted
  with the library type and sampling depth.
- **Per-tile quality:** checks whether one part of the sequencing flow cell has
  unusually low quality. It is a technical check and does not measure gene
  function or biological quality.

### Before and after trimming

The raw subset contained 1,000 pairs. Cutadapt detected adapter sequence in 34
R1 reads and 33 R2 reads. After adapter and quality trimming, 997 pairs
remained, so 99.7% of the pairs passed the minimum-length filter. Three pairs
were removed because they became shorter than 30 bp.

The important result is that most of the data was retained while adapter and
low-quality sequence were removed. The trimmed files are not supposed to have
exactly the same length distribution as the raw files; variable lengths are an
expected result of removing poor-quality ends. The raw files are preserved so
the comparison can be repeated.

### Correct reference for future analysis

Week 2 contains a *Drosophila melanogaster* assembly because that earlier work
focused on the Lamin gene. That assembly is not appropriate for these reads:
this Week-4 run is *Physcomitrium patens*. Mapping moss reads to Drosophila
would produce misleading alignment and coverage results.

Before mapping, obtain a *Physcomitrium patens* reference FASTA and matching
annotation from NCBI or Ensembl Plants. The FASTA, annotation, and index files
must all come from the same assembly release. The correct downstream sequence
is:

```text
Physcomitrium reference FASTA + annotation
        -> FASTA and aligner indexes
        -> map the trimmed R1/R2 reads
        -> check alignment rate and coverage
        -> interpret reads with the moss annotation
```

FastQC is complete without the reference genome. The matching reference is
needed for later mapping, coverage, variant, or gene-level analysis.

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
