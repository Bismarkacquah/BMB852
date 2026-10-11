# Extend the Week-5 alignment workflow with variant calling.
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
WEEK5 ?= ../Week-5
REFERENCE ?= $(WEEK5)/fasta/GCA_000002425.2_Phypa_V3_genomic.fna
BAM ?= $(WEEK5)/bam/ERR8982185.sorted.bam
THREADS ?= 2
# ENA identifies protonema tissue; use a haploid model for this life stage.
# This is a biological inference, not a direct measurement of sample ploidy.
PLOIDY ?= 1
MIN_MQ ?= 20
MIN_BQ ?= 20
MIN_QUAL ?= 20
MIN_DP ?= 3
RAW := results/ERR8982185.raw.vcf.gz
NORM := results/ERR8982185.normalized.vcf.gz
FILTERED := results/ERR8982185.filtered.vcf.gz
ALL_VCF := results/ERR8982185.vcf
VCF := results/ERR8982185.pass.vcf

.PHONY: all setup alignment check-tools check-inputs summary validate igv FORCE
all: $(ALL_VCF) $(VCF) $(FILTERED).csi results/raw.stats.txt results/pass.stats.txt results/summary.json provenance/inputs.sha256
setup:
	$(MAKE) -C $(WEEK5) setup
alignment:
	$(MAKE) -C $(WEEK5) all THREADS=$(THREADS)
check-tools:
	@for tool in bcftools samtools python3; do command -v $$tool; done
check-inputs: check-tools
	test -s $(REFERENCE)
	test -s $(BAM)
	samtools quickcheck -v $(BAM)
# Reuse the existing BAM. Run make setup alignment first if it is absent.
$(REFERENCE).fai: $(REFERENCE)
	samtools faidx $<
$(BAM).bai: $(BAM)
	samtools index $<
# Track parameter changes so Make does not silently reuse older calls.
provenance/parameters.txt: FORCE
	mkdir -p provenance
	printf '%s\n' 'PLOIDY=$(PLOIDY)' 'MIN_MQ=$(MIN_MQ)' 'MIN_BQ=$(MIN_BQ)' 'MIN_QUAL=$(MIN_QUAL)' 'MIN_DP=$(MIN_DP)' 'BAM=$(BAM)' 'REFERENCE=$(REFERENCE)' > $@.tmp
	if ! cmp -s $@.tmp $@; then mv $@.tmp $@; else rm $@.tmp; fi
$(RAW): $(BAM) $(BAM).bai $(REFERENCE) $(REFERENCE).fai provenance/parameters.txt Makefile | check-inputs
	mkdir -p results provenance
	{ bcftools --version; samtools --version; } > provenance/tool-versions.txt
	bcftools mpileup -Ou -f $(REFERENCE) -q $(MIN_MQ) -Q $(MIN_BQ) -d 1000 -a FORMAT/DP,FORMAT/AD $(BAM) 2> provenance/mpileup.log | bcftools call -mv --ploidy $(PLOIDY) -Oz -o $@ 2> provenance/call.log
$(NORM): $(RAW) $(REFERENCE) $(REFERENCE).fai
	bcftools norm -f $(REFERENCE) -c e -m -any -Oz -o $@ $< 2> provenance/normalization.log
$(FILTERED): $(NORM) provenance/parameters.txt
	bcftools filter -s LowQualOrDepth -e 'QUAL<$(MIN_QUAL) || FMT/DP<$(MIN_DP)' -Oz -o $@ $<
$(FILTERED).csi: $(FILTERED)
	bcftools index -f $<
$(VCF): $(FILTERED)
	bcftools view -f PASS -Ov -o $@ $<
$(ALL_VCF): $(FILTERED)
	bcftools view -Ov -o $@ $<
results/raw.stats.txt: $(RAW)
	bcftools stats $< > $@
results/pass.stats.txt: $(VCF)
	bcftools stats $< > $@
results/summary.json: $(RAW) $(FILTERED) $(VCF) scripts/summarize_vcf.py
	python3 scripts/summarize_vcf.py $(RAW) $(FILTERED) $(VCF) --output $@
summary: results/summary.json
	cat $<
# For Windows IGV from WSL, pass IGV_ROOT=C:/path/to/BMB852.
igv: all
	python3 scripts/prepare_igv.py $(if $(IGV_ROOT),--igv-root "$(IGV_ROOT)")
provenance/inputs.sha256: $(BAM) $(REFERENCE) $(RAW) $(FILTERED) $(ALL_VCF) $(VCF)
	mkdir -p provenance
	sha256sum $(BAM) $(REFERENCE) $(RAW) $(FILTERED) $(ALL_VCF) $(VCF) > $@
validate: all
	bcftools view -Ov $(RAW) > /dev/null
	bcftools norm -f $(REFERENCE) -c e -Ov $(ALL_VCF) > /dev/null
	bcftools norm -f $(REFERENCE) -c e -Ov $(VCF) > /dev/null
	sha256sum -c provenance/inputs.sha256
