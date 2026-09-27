#!/usr/bin/env bash
# Stop on failed commands, unset variables, and failures inside pipelines.
set -euo pipefail
# Resolve this script's directory and enter Week-5 regardless of the launch directory.
cd "$(dirname "$0")/.."
# Pin the moss assembly and run used in the submitted analysis.
assembly=GCA_000002425.2_Phypa_V3
run=ERR8982185
# The report uses the first 1,000 sequencing spots, not the full run.
spots=1000
# NCBI provides both reference sequence and annotation for this assembly.
base="https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/002/425/$assembly"
# Create input directories; existing directories and files are preserved.
mkdir -p fasta ../Week-2/data ../Week-4/data/raw ../Week-4/data/trimmed
# Retrieve each missing reference input; reuse the original Week-2 files if available.
for ext in fna gff; do
    # Use the assembly-specific name to keep FASTA and annotation matched.
    target="../Week-2/data/${assembly}_genomic.$ext"
    # A nonempty existing file does not need another download.
    if [[ ! -s "$target" ]]; then
        # Fail on HTTP errors, follow redirects, and retry transient failures.
        curl --fail --location --retry 3 "$base/${assembly}_genomic.$ext.gz" -o "$target.gz.part"
        # Decompress to a temporary file so interrupted runs do not leave a final output.
        gzip -dc "$target.gz.part" > "$target.part"
        # Confirm the decompressed input is nonempty before giving it the final name.
        test -s "$target.part"
        mv "$target.part" "$target"
    fi
done
# Keep a local FASTA copy for the Week-5 folder and IGV.
if [[ ! -s "fasta/${assembly}_genomic.fna" ]]; then
    cp "../Week-2/data/${assembly}_genomic.fna" "fasta/${assembly}_genomic.fna"
fi
# Download and trim only when either trimmed mate is missing.
if [[ ! -s "../Week-4/data/trimmed/${run}_1.trimmed.fastq.gz" || ! -s "../Week-4/data/trimmed/${run}_2.trimmed.fastq.gz" ]]; then
    # Reuse the raw subset if both mates are already present.
    if [[ ! -s "../Week-4/data/raw/${run}_1.fastq.gz" || ! -s "../Week-4/data/raw/${run}_2.fastq.gz" ]]; then
        # Split paired reads into mate files, compress them, and stop at spot 1,000.
        fastq-dump --split-files --gzip --maxSpotId "$spots" --outdir ../Week-4/data/raw "$run"
    fi
    # Use two cores, trim the two Illumina adapters, trim ends at Q20, and require 30 bases.
    # -o and -p name the paired output files; the final two arguments are raw mate inputs.
    cutadapt -j 2 -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT -q 20,20 -m 30 \
        -o "../Week-4/data/trimmed/${run}_1.trimmed.fastq.gz" -p "../Week-4/data/trimmed/${run}_2.trimmed.fastq.gz" \
        "../Week-4/data/raw/${run}_1.fastq.gz" "../Week-4/data/raw/${run}_2.fastq.gz"
fi
