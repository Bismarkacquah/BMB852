#!/usr/bin/env bash
set -euo pipefail
sample=$1
ref=$2
out=$3
threads=$4
design=$5
ploidy=$(python3 scripts/workflow.py ploidy --design "$design" --sample "$sample")
batch_bases=$(python3 scripts/workflow.py batch-bases --design "$design" --sample "$sample")
if [[ ! -f "$out/reused-bam.json" ]]; then
cutadapt -j "$threads" -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT -q 20,20 -m 30 --json "$out/cutadapt.json" -o "$out/read1.trimmed.fastq.gz" -p "$out/read2.trimmed.fastq.gz" "$out/read1.fastq.gz" "$out/read2.fastq.gz" > "$out/cutadapt.log" 2>&1
bwa mem -K "$batch_bases" -t "$threads" -R "@RG\tID:$sample\tSM:$sample\tPL:ILLUMINA" "$ref" "$out/read1.trimmed.fastq.gz" "$out/read2.trimmed.fastq.gz" 2> "$out/bwa.log" |
    samtools sort -@ "$threads" -m 256M -o "$out/aligned.bam.part" 2> "$out/sort.log"
samtools quickcheck -v "$out/aligned.bam.part"
mv "$out/aligned.bam.part" "$out/aligned.bam"
samtools index "$out/aligned.bam"
fi
bcftools mpileup -Ou -f "$ref" -q 20 -Q 20 -d 1000 -a FORMAT/DP,FORMAT/AD "$out/aligned.bam" 2> "$out/mpileup.log" |
    bcftools call -mv --ploidy "$ploidy" -Ou 2> "$out/call.log" |
    bcftools norm -f "$ref" -c e -m -any -Ou 2> "$out/norm.log" |
    bcftools view -i 'QUAL>=20 && FMT/DP>=3' -Oz -o "$out/calls.vcf.gz.part"
mv "$out/calls.vcf.gz.part" "$out/calls.vcf.gz"
bcftools index -f "$out/calls.vcf.gz"
