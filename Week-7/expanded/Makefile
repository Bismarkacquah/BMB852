# Expanded Week 7 analysis, kept separate from the original 1,000-pair run.
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
PAIRS ?= 20000000
THREADS ?= 4
SORT_THREADS ?= 2
REFERENCE := ../../Week-5/fasta/GCA_000002425.2_Phypa_V3_genomic.fna
READ1 := data/trimmed/ERR8982185_1.trimmed.fastq.gz
READ2 := data/trimmed/ERR8982185_2.trimmed.fastq.gz
BAM := bam/ERR8982185.20M.sorted.bam
RAW := results/ERR8982185.20M.raw.vcf.gz
FILTERED := results/ERR8982185.20M.filtered.vcf.gz
PASS := results/ERR8982185.20M.pass.vcf.gz
PLOIDY ?= 1
MIN_DP ?= 3
MIN_QUAL ?= 20

.PHONY: all download align variants stats coverage validate igv FORCE
all: $(BAM).bai results/flagstat.txt results/coverage.tsv results/depth-summary.json $(FILTERED).csi $(PASS).csi $(FILTERED).tbi $(PASS).tbi results/summary.json results/raw.stats.txt results/pass.stats.txt provenance/inputs.sha256
download: provenance/download.json
align: $(BAM).bai
variants: $(FILTERED).csi $(PASS).csi
stats: results/raw.stats.txt results/pass.stats.txt
coverage: results/depth-summary.json
provenance/parameters.txt: FORCE
	mkdir -p provenance
	printf '%s\n' 'PAIRS=$(PAIRS)' 'PLOIDY=$(PLOIDY)' 'MIN_DP=$(MIN_DP)' 'MIN_QUAL=$(MIN_QUAL)' > $@.tmp
	if ! cmp -s $@.tmp $@; then mv $@.tmp $@; else rm $@.tmp; fi
provenance/subset-parameters.txt: FORCE
	mkdir -p provenance
	printf '%s\n' 'PAIRS=$(PAIRS)' > $@.tmp
	if ! cmp -s $@.tmp $@; then mv $@.tmp $@; else rm $@.tmp; fi
provenance/download.json: ../scripts/download_subset.py provenance/subset-parameters.txt
	mkdir -p data/raw provenance
	python3 ../scripts/download_subset.py --pairs $(PAIRS) --output-dir data/raw --manifest $@ > provenance/download.log 2>&1
$(READ1) $(READ2) &: provenance/download.json
	mkdir -p data/trimmed
	cutadapt -j $(THREADS) -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT -q 20,20 -m 30 --json provenance/cutadapt.json -o $(READ1) -p $(READ2) data/raw/ERR8982185_1.fastq.gz data/raw/ERR8982185_2.fastq.gz > provenance/cutadapt.log 2>&1
$(BAM): $(READ1) $(READ2) $(REFERENCE).bwt $(REFERENCE).fai
	mkdir -p bam provenance
	bwa mem -t $(THREADS) -R '@RG\tID:ERR8982185_20M\tSM:ERR8982185\tPL:ILLUMINA' $(REFERENCE) $(READ1) $(READ2) 2> provenance/bwa.log | samtools sort -@ $(SORT_THREADS) -m 256M -o $@ 2> provenance/sort.log
	samtools quickcheck -v $@
$(BAM).bai: $(BAM)
	samtools index $<
results/flagstat.txt: $(BAM)
	mkdir -p results
	samtools flagstat $(BAM) > $@
results/coverage.tsv: $(BAM) $(BAM).bai
	mkdir -p results
	samtools coverage $(BAM) > $@
results/depth-summary.json: $(BAM) $(BAM).bai $(REFERENCE).fai provenance/cutadapt.json ../scripts/summarize_expanded_depth.py
	mkdir -p results
	samtools depth -Q 20 $(BAM) | python3 ../scripts/summarize_expanded_depth.py --fai $(REFERENCE).fai --cutadapt provenance/cutadapt.json --output $@
$(RAW): $(BAM) $(BAM).bai $(REFERENCE).fai provenance/parameters.txt
	mkdir -p results provenance
	{ bcftools --version; samtools --version; bwa 2>&1 || true; cutadapt --version; } > provenance/tool-versions.txt
	bcftools mpileup -Ou -f $(REFERENCE) -q 20 -Q 20 -d 1000 -a FORMAT/DP,FORMAT/AD $(BAM) 2> provenance/mpileup.log | bcftools call -mv --ploidy $(PLOIDY) -Oz -o $@ 2> provenance/call.log
results/ERR8982185.20M.normalized.vcf.gz: $(RAW) $(REFERENCE)
	bcftools norm -f $(REFERENCE) -c e -m -any -Oz -o $@ $< 2> provenance/normalization.log
$(FILTERED): results/ERR8982185.20M.normalized.vcf.gz provenance/parameters.txt
	bcftools filter -s LowQualOrDepth -e 'QUAL<$(MIN_QUAL) || FMT/DP<$(MIN_DP)' -Oz -o $@ $<
$(PASS): $(FILTERED)
	bcftools view -f PASS -Oz -o $@ $<
%.vcf.gz.csi: %.vcf.gz
	bcftools index -f $<
%.vcf.gz.tbi: %.vcf.gz
	bcftools index -t -f $<
results/summary.json: $(RAW) $(FILTERED) $(PASS) ../scripts/summarize_vcf.py
	python3 ../scripts/summarize_vcf.py $(RAW) $(FILTERED) $(PASS) --output $@
results/raw.stats.txt: $(RAW)
	bcftools stats $< > $@
results/pass.stats.txt: $(PASS)
	bcftools stats $< > $@
provenance/inputs.sha256: $(BAM) $(READ1) $(READ2) $(FILTERED) $(PASS)
	mkdir -p provenance
	sha256sum $(BAM) $(READ1) $(READ2) $(FILTERED) $(PASS) > $@
validate: all
	samtools quickcheck -v $(BAM)
	bcftools norm -f $(REFERENCE) -c e -Ov $(PASS) > /dev/null
	sha256sum -c provenance/inputs.sha256
igv: all
	python3 ../scripts/prepare_expanded_igv.py $(if $(IGV_ROOT),--igv-root "$(IGV_ROOT)")
