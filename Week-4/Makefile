SHELL := /bin/bash

# Override ACCESSION and N on the command line for another paired-end SRA run.
ACCESSION ?= SRR519926
N ?= 1000
THREADS ?= 2
FASTQC_OPTIONS ?= --nogroup

SRA_TOOL ?= fastq-dump
RAW_DIR := data/raw
TRIMMED_DIR := data/trimmed
RAW_QC_DIR := results/qc/raw
TRIMMED_QC_DIR := results/qc/trimmed
REPORT_DIR := results
RAW_STATS := $(REPORT_DIR)/seqkit_raw_stats.tsv
TRIMMED_STATS := $(REPORT_DIR)/seqkit_trimmed_stats.tsv
SEQUALI_RAW_HTML := $(REPORT_DIR)/sequali_raw.html
SEQUALI_RAW_JSON := $(REPORT_DIR)/sequali_raw.json
SEQUALI_TRIMMED_HTML := $(REPORT_DIR)/sequali_trimmed.html
SEQUALI_TRIMMED_JSON := $(REPORT_DIR)/sequali_trimmed.json
MULTIQC_DIR := $(REPORT_DIR)/multiqc

RAW_R1 := $(RAW_DIR)/$(ACCESSION)_1.fastq.gz
RAW_R2 := $(RAW_DIR)/$(ACCESSION)_2.fastq.gz
TRIMMED_R1 := $(TRIMMED_DIR)/$(ACCESSION)_1.trimmed.fastq.gz
TRIMMED_R2 := $(TRIMMED_DIR)/$(ACCESSION)_2.trimmed.fastq.gz

ENA_API := https://www.ebi.ac.uk/ena/portal/api
ENA_RUN_INFO := $(ENA_API)/filereport?accession=$(ACCESSION)&result=read_run&fields=run_accession,study_accession,sample_accession,experiment_accession,library_name,instrument_platform,instrument_model,library_strategy,library_source,library_layout,read_count,base_count,fastq_ftp&format=tsv

.PHONY: all help versions check-tools check-curl check-sra check-fastqc check-fastp check-seqkit check-sequali check-multiqc metadata download stats stats-trimmed qc-raw trim qc-trimmed sequali-raw sequali-trimmed multiqc clean

all: metadata versions stats-trimmed qc-trimmed sequali-trimmed multiqc

help:
	@echo "Week 4 FASTQ workflow"
	@echo "  make                   Run metadata, download, raw QC, trimming, and trimmed QC"
	@echo "  make N=100000          Limit the run to N sequencing spots"
	@echo "  make versions          Show installed tool versions"
	@echo "  make check-tools       Verify required commands are available"
	@echo "  make metadata          Download ENA metadata only"
	@echo "  make download          Download the raw paired FASTQ subset"
	@echo "  make qc-raw            Run FastQC on raw reads"
	@echo "  make stats             Write seqkit statistics for raw reads"
	@echo "  make trim              Trim reads and write fastp reports"
	@echo "  make stats-trimmed     Write seqkit statistics for trimmed reads"
	@echo "  make sequali-raw      Run Sequali on raw paired reads"
	@echo "  make sequali-trimmed  Run Sequali on trimmed paired reads"
	@echo "  make multiqc          Aggregate FastQC and Sequali reports"
	@echo "  make qc-trimmed        Run FastQC on trimmed reads"
	@echo "  make clean             Remove generated data and reports"

versions: check-tools
	mkdir -p $(REPORT_DIR)
	@{ \
		echo "curl:       $$(curl --version | awk 'NR == 1 {print $$2}')"; \
		echo "fastq-dump: $$(fastq-dump --version 2>&1 | awk 'NR == 1 {print $$NF}')"; \
		echo "fastqc:     $$(fastqc --version 2>&1)"; \
		echo "fastp:      $$(fastp --version 2>&1 | awk 'NR == 1 {print $$NF}')"; \
		echo "seqkit:     $$(seqkit version 2>&1 | awk 'NR == 1 {print $$NF}')"; \
		echo "sequali:    $$(sequali --version 2>&1 | awk 'NR == 1 {print $$NF}')"; \
		echo "multiqc:    $$(multiqc --version 2>&1 | awk 'NR == 1 {print $$NF}')"; \
		echo "make:       $$(make --version | awk 'NR == 1 {print $$3}')"; \
	} | tee $(REPORT_DIR)/versions.txt

check-tools: check-curl check-sra check-fastqc check-fastp check-seqkit check-sequali check-multiqc
	@echo "All required tools are available."

check-curl:
	@command -v curl >/dev/null 2>&1 || { echo "Error: curl is required."; exit 1; }

check-sra:
	@command -v $(SRA_TOOL) >/dev/null 2>&1 || { echo "Error: $(SRA_TOOL) is required."; exit 1; }

check-fastqc:
	@command -v fastqc >/dev/null 2>&1 || { echo "Error: fastqc is required."; exit 1; }

check-fastp:
	@command -v fastp >/dev/null 2>&1 || { echo "Error: fastp is required."; exit 1; }

check-seqkit:
	@command -v seqkit >/dev/null 2>&1 || { echo "Error: seqkit is required."; exit 1; }

check-sequali:
	@command -v sequali >/dev/null 2>&1 || { echo "Error: sequali is required."; exit 1; }

check-multiqc:
	@command -v multiqc >/dev/null 2>&1 || { echo "Error: multiqc is required."; exit 1; }

metadata: check-curl
	mkdir -p $(REPORT_DIR)
	curl --fail --location --retry 3 --output $(REPORT_DIR)/ena_$(ACCESSION).tsv "$(ENA_RUN_INFO)"

stats: download check-seqkit
	mkdir -p $(REPORT_DIR)
	seqkit stats --tabular $(RAW_R1) $(RAW_R2) | tee $(RAW_STATS)

download: check-sra
	mkdir -p $(RAW_DIR)
	@set -euo pipefail; \
	if [[ -s "$(RAW_R1)" && -s "$(RAW_R2)" ]]; then \
		echo "Raw FASTQ files already exist; nothing to download."; \
	else \
		$(SRA_TOOL) --split-files --gzip --maxSpotId $(N) --outdir $(RAW_DIR) $(ACCESSION); \
		mv "$(RAW_DIR)/$(ACCESSION)_1.fastq.gz" "$(RAW_R1)"; \
		mv "$(RAW_DIR)/$(ACCESSION)_2.fastq.gz" "$(RAW_R2)"; \
	fi

qc-raw: download check-fastqc
	mkdir -p $(RAW_QC_DIR)
	fastqc $(FASTQC_OPTIONS) --threads $(THREADS) --outdir $(RAW_QC_DIR) $(RAW_R1) $(RAW_R2)

trim: qc-raw check-fastp
	mkdir -p $(TRIMMED_DIR) $(REPORT_DIR)
	fastp \
		--in1 $(RAW_R1) \
		--in2 $(RAW_R2) \
		--out1 $(TRIMMED_R1) \
		--out2 $(TRIMMED_R2) \
		--detect_adapter_for_pe \
		--html $(REPORT_DIR)/fastp_$(ACCESSION).html \
		--json $(REPORT_DIR)/fastp_$(ACCESSION).json

stats-trimmed: trim check-seqkit
	mkdir -p $(REPORT_DIR)
	seqkit stats --tabular $(TRIMMED_R1) $(TRIMMED_R2) | tee $(TRIMMED_STATS)

sequali-raw: download check-sequali
	mkdir -p $(REPORT_DIR)
	sequali --threads $(THREADS) --html $(SEQUALI_RAW_HTML) --json $(SEQUALI_RAW_JSON) $(RAW_R1) $(RAW_R2)

sequali-trimmed: trim check-sequali
	mkdir -p $(REPORT_DIR)
	sequali --threads $(THREADS) --html $(SEQUALI_TRIMMED_HTML) --json $(SEQUALI_TRIMMED_JSON) $(TRIMMED_R1) $(TRIMMED_R2)

multiqc: qc-trimmed sequali-raw sequali-trimmed check-multiqc
	mkdir -p $(MULTIQC_DIR)
	multiqc --force --outdir $(MULTIQC_DIR) --filename multiqc_report.html $(RAW_QC_DIR) $(TRIMMED_QC_DIR) $(REPORT_DIR)/sequali_raw.json $(REPORT_DIR)/sequali_trimmed.json

qc-trimmed: trim
	mkdir -p $(TRIMMED_QC_DIR)
	fastqc $(FASTQC_OPTIONS) --threads $(THREADS) --outdir $(TRIMMED_QC_DIR) $(TRIMMED_R1) $(TRIMMED_R2)

clean:
	rm -rf data results
