# BMB852 Assignment 1

I used Visual Studio Code (VSC) to complete this assignment.

## Samtools Version

### Command

```bash
samtools --version
```

### Output

```text
samtools 1.16.1
Using htslib 1.16
Copyright (C) 2021 Genome Research Ltd.
```

## Nested Directory

### Check the current directory

```bash
pwd
```

### Create the project directories

```bash
mkdir -p data/raw/{fasta,fastq}
mkdir -p data/processed
mkdir -p results/analysis
mkdir -p scripts
```

### Create the files

```bash
touch data/raw/fasta/sequences.fa
touch data/raw/fastq/reads.fq
touch data/processed/trimmed-reads.fq
touch results/analysis/summary.txt
touch scripts/analyze.py
```

## Directory Structure

### Verify the files

```bash
find . -type f
```

### Output

```text
./README.md
./data/raw/fasta/sequences.fa
./data/raw/fastq/reads.fq
./data/processed/trimmed-reads.fq
./results/analysis/summary.txt
./scripts/analyze.py
```

## Accessing Files Using Relative Paths

These paths are relative because they start from the current project directory, `Week-1`.

```bash
cat data/raw/fasta/sequences.fa
cat data/raw/fastq/reads.fq
cat data/processed/trimmed-reads.fq
cat results/analysis/summary.txt
cat scripts/analyze.py
```

### Move through directories with relative paths

```bash
cd data
cd raw
cd fasta
pwd
cd ../../..
pwd
```

## Accessing Files Using Absolute Paths

### Check the current location

```bash
pwd
```

### Access the project files with an absolute path

Replace `<project-path>` with the path printed by `pwd`.

```bash
cat <project-path>/data/raw/fasta/sequences.fa
cat <project-path>/data/raw/fastq/reads.fq
cat <project-path>/data/processed/trimmed-reads.fq
cat <project-path>/results/analysis/summary.txt
cat <project-path>/scripts/analyze.py
```

## Summary

This assignment demonstrates samtools version checking, creating nested directories and files, verifying a project structure, and navigating to files using both relative and absolute paths.
