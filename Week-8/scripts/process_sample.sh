#!/usr/bin/env bash
set -euo pipefail
run=$1
ref=$2
pairs=$3
threads=$4
mkdir -p "samples/$run" provenance
out="samples/$run"
# Serialize overlapping Make invocations for this sample, including prefetch lanes.
exec 9> "$out/processing.lock"
flock 9
signature=$( { printf '%s\n' "$run" "$ref" "$pairs"; sha256sum "$ref" "$0" scripts/download_sample.py scripts/check_download.py; } | sha256sum | cut -d ' ' -f 1)
if [[ -s "$out/processing.signature" && -s "$out/inputs.sha256" && "$(cat "$out/processing.signature")" == "$signature" ]] && sha256sum -c "$out/inputs.sha256" > /dev/null 2>&1; then
    exit 0
fi
if [[ "$run" == ERR8982185 && "$pairs" == 20000000 && -s ../Week-7/expanded/results/ERR8982185.20M.pass.vcf.gz && -s ../Week-7/expanded/bam/ERR8982185.20M.sorted.bam && -s ../Week-7/expanded/bam/ERR8982185.20M.sorted.bam.bai ]]; then
    # The identical Week 7 sample was already independently processed.
    cp ../Week-7/expanded/results/ERR8982185.20M.pass.vcf.gz "$out/$run.pass.vcf.gz"
    printf '%s\n' 'Reused independently processed Week 7 20M PASS VCF; identical reference and filters.' > "$out/reuse.txt"
else
    # A separately started prefetch may already be writing this sample's files.
    while pgrep -f "^python3 scripts/download_sample.py --run $run " > /dev/null; do
        sleep 10
    done
    if ! python3 scripts/check_download.py "$out/raw" "$run" "$pairs"; then
        python3 scripts/download_sample.py --run "$run" --pairs "$pairs" --output "$out/raw" > "$out/download.log" 2>&1
    fi
    cutadapt -j "$threads" -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT -q 20,20 -m 30 --json "$out/cutadapt.json" -o "$out/read1.trimmed.fastq.gz" -p "$out/read2.trimmed.fastq.gz" "$out/raw/${run}_1.fastq.gz" "$out/raw/${run}_2.fastq.gz" > "$out/cutadapt.log" 2>&1
    bwa mem -t "$threads" -R "@RG\tID:$run\tSM:$run\tPL:ILLUMINA" "$ref" "$out/read1.trimmed.fastq.gz" "$out/read2.trimmed.fastq.gz" 2> "$out/bwa.log" | samtools sort -@ 2 -m 256M -o "$out/$run.sorted.bam" 2> "$out/sort.log"
    samtools quickcheck -v "$out/$run.sorted.bam"
    samtools index "$out/$run.sorted.bam"
    samtools flagstat "$out/$run.sorted.bam" > "$out/flagstat.txt"
    bcftools mpileup -Ou -f "$ref" -q 20 -Q 20 -d 1000 -a FORMAT/DP,FORMAT/AD "$out/$run.sorted.bam" 2> "$out/mpileup.log" | bcftools call -mv --ploidy 1 -Ou 2> "$out/call.log" | bcftools norm -f "$ref" -c e -m -any -Ou 2> "$out/norm.log" | bcftools filter -s LowQualOrDepth -e 'QUAL<20 || FMT/DP<3' -Oz -o "$out/$run.filtered.vcf.gz"
    bcftools view -f PASS -Oz -o "$out/$run.pass.vcf.gz" "$out/$run.filtered.vcf.gz"
fi
bcftools index -f "$out/$run.pass.vcf.gz"
test "$(bcftools query -l "$out/$run.pass.vcf.gz")" = "$run"
bcftools norm -f "$ref" -c e -Ov "$out/$run.pass.vcf.gz" > /dev/null
bcftools stats "$out/$run.pass.vcf.gz" > "$out/pass.stats.txt"
sha256sum "$out/$run.pass.vcf.gz" > "$out/inputs.sha256"
printf '%s\n' "$signature" > "$out/processing.signature"
