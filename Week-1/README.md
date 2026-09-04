# Week 1: System Setup and UNIX Fundamentals

## Completion Summary

### Editor Setup
Visual Studio Code (VS Code) installed and configured as primary code editor.

### samtools Version
```
samtools 1.16.1
Using htslib 1.16
Copyright (C) 2021 Genome Research Ltd.
```

### Directory Structure Created
```bash
$ mkdir -p data/raw/{fasta,fastq}
$ mkdir -p data/processed
$ mkdir -p results/analysis
$ mkdir -p scripts
```

### Files Created
```bash
$ touch data/raw/fasta/sequences.fa
$ touch data/raw/fastq/reads.fq
$ touch data/processed/trimmed-reads.fq
$ touch scripts/analyze.py
$ touch results/analysis/summary.txt
```

### Directory Listing Output
```bash
$ ls -R
.:
data  results  scripts

./data:
processed  raw

./data/processed:
trimmed-reads.fq

./data/raw:
fasta  fastq

./data/raw/fasta:
sequences.fa

./data/raw/fastq:
reads.fq

./results:
analysis

./results/analysis:
summary.txt

./scripts:
analyze.py
```

### Navigation with Absolute Paths
```bash
$ pwd
/home/bismark/BMB852/Week-1

$ cat /home/bismark/BMB852/Week-1/data/raw/fasta/sequences.fa
$ cat /home/bismark/BMB852/Week-1/data/raw/fastq/reads.fq
```

### Navigation with Relative Paths
```bash
$ cat data/raw/fasta/sequences.fa
$ cat data/raw/fastq/reads.fq
$ cat data/processed/trimmed-reads.fq
$ cat scripts/analyze.py

$ cd data/raw/fasta/
$ pwd
/home/bismark/BMB852/Week-1/data/raw/fasta

$ cd ../../..
$ pwd
/home/bismark/BMB852/Week-1
```
