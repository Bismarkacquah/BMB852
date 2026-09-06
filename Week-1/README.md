# BMB852 Assignment 1

I used Visual Studio Code (VSC) to complete this assignment.

## Samtools Version

I activated the bioinformatics Conda environment before checking the installed samtools version.

### Command

```bash
conda activate bioinfo
samtools --version
```

### Output

```text
samtools 1.16.1
Using htslib 1.16
Copyright (C) 2021 Genome Research Ltd.
```

## Nested Directory

The following commands create the nested project folders used to organize raw data, processed data, results, and scripts.

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

These commands create the empty files required for the project structure.

```bash
touch data/raw/fasta/sequences.fa
touch data/raw/fastq/reads.fq
touch data/processed/trimmed-reads.fq
touch results/analysis/summary.txt
touch scripts/analyze.py
```

## Directory Structure

The directory structure was verified after creating the folders and files.

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
Relative paths do not begin with the drive or home-directory location.

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

Absolute paths begin at the root of the filesystem and identify the complete location of a file.

### Check the current location

```bash
pwd
```

Example output:

```text
C:\Users\bxa5404\Documents\GitHub\BMB852\Week-1
```

### Access the project files with an absolute path

The following examples use the path printed by `pwd`.

```bash
cat C:/Users/bxa5404/Documents/GitHub/BMB852/Week-1/data/raw/fasta/sequences.fa
cat C:/Users/bxa5404/Documents/GitHub/BMB852/Week-1/data/raw/fastq/reads.fq
cat C:/Users/bxa5404/Documents/GitHub/BMB852/Week-1/data/processed/trimmed-reads.fq
cat C:/Users/bxa5404/Documents/GitHub/BMB852/Week-1/results/analysis/summary.txt
cat C:/Users/bxa5404/Documents/GitHub/BMB852/Week-1/scripts/analyze.py
```

## Summary

This assignment demonstrates samtools version checking, creating nested directories and files, verifying a project structure, and navigating to files using both relative and absolute paths.
