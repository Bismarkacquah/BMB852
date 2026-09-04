# Week 1: System Setup and UNIX Fundamentals

## Assignment Completion Summary

### Editor Setup
I have installed **Visual Studio Code (VS Code)** as my primary code editor for this course. It provides excellent support for bioinformatics workflows with integrated terminal functionality and markdown preview capabilities.

## UNIX Commands and Outputs

### 1. Checking samtools Version

```bash
$ samtools --version
samtools 1.16.1
Using htslib 1.16
Copyright (C) 2021 Genome Research Ltd.
```

The samtools version in the bioinformatics environment is **1.16.1**.

### 2. Creating a Nested Directory Structure

```bash
$ mkdir -p data/raw/{fasta,fastq}
$ mkdir -p data/processed
$ mkdir -p results/analysis
$ mkdir -p scripts
```

This creates the following hierarchy:
```
data/
├── raw/
│   ├── fasta/
│   └── fastq/
└── processed/
results/
└── analysis/
scripts/
```

### 3. Creating Files in Different Directories

```bash
$ touch data/raw/fasta/sequences.fa
$ touch data/raw/fastq/reads.fq
$ touch data/processed/trimmed-reads.fq
$ touch scripts/analyze.py
$ touch results/analysis/summary.txt
```

Verifying file creation:
```bash
$ ls -R
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

### 4. Accessing Files Using Relative and Absolute Paths

#### Absolute Paths
```bash
$ cat /home/bismark/BMB852/Week-1/data/raw/fasta/sequences.fa
$ cat /home/bismark/BMB852/Week-1/data/raw/fastq/reads.fq
```

#### Relative Paths (from Week-1 directory)
```bash
$ cat data/raw/fasta/sequences.fa
$ cat data/raw/fastq/reads.fq
$ cat data/processed/trimmed-reads.fq
$ cat ../Week-1/scripts/analyze.py
```

#### Navigating with Relative Paths
```bash
$ cd data/raw/fasta/
$ pwd
/home/bismark/BMB852/Week-1/data/raw/fasta
$ cd ../../..
$ pwd
/home/bismark/BMB852/Week-1
```

## Repository Organization

Following the instructor's feedback, this repository is organized with each assignment in its own dedicated folder to ensure scalability and maintainability throughout the course. This structure allows for easy navigation and the ability to add subsequent weekly assignments without cluttering the main directory.

### Directory Tree
```
BMB852/
├── Week-1/
│   ├── README.md (this file)
│   ├── data/
│   │   ├── raw/
│   │   │   ├── fasta/
│   │   │   │   └── sequences.fa
│   │   │   └── fastq/
│   │   │       └── reads.fq
│   │   └── processed/
│   │       └── trimmed-reads.fq
│   ├── results/
│   │   └── analysis/
│   │       └── summary.txt
│   └── scripts/
│       └── analyze.py
├── Week-2/
└── README.md
```

## Key Learnings

- Successfully set up VS Code as my development environment
- Practiced creating nested directory structures using `mkdir -p`
- Understood the difference between absolute and relative paths
- Learned how to navigate the file system using `cd` and `pwd`
- Confirmed samtools installation and version compatibility
- Implemented proper file organization practices for bioinformatics workflows
