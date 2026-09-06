#!/usr/bin/env python3
"""Simple script to summarize the raw sequence data in Week 1."""

from pathlib import Path

base = Path(__file__).resolve().parent.parent
fasta_path = base / "data" / "raw" / "fasta" / "sequences.fa"
fastq_path = base / "data" / "raw" / "fastq" / "reads.fq"

fasta_count = 0
fasta_bases = 0
with fasta_path.open("r", encoding="utf-8") as handle:
    for line in handle:
        if line.startswith(">"):
            fasta_count += 1
        else:
            fasta_bases += len(line.strip())

fastq_count = 0
with fastq_path.open("r", encoding="utf-8") as handle:
    for line in handle:
        if line.startswith("@"):
            fastq_count += 1

summary = (
    f"FASTA records: {fasta_count}\n"
    f"FASTA bases: {fasta_bases}\n"
    f"FASTQ reads: {fastq_count}\n"
)

print(summary)
