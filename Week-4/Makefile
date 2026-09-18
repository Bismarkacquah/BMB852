SHELL := /bin/bash

# Override ACCESSION and N on the command line for another paired-end SRA run.
ACCESSION ?= DRR303595
N ?= 100000
THREADS ?= 2

SRA_TOOL ?= fastq-dump
RAW_DIR := data/raw
TRIMMED_DIR := data/trimmed
RAW_QC_DIR := results/qc/raw
TRIMMED_QC_DIR := results/qc/trimmed
REPORT_DIR := results

RAW_R1 := $(RAW_DIR)/lamin_$(ACCESSION)_R1.fastq.gz
RAW_R2 := $(RAW_DIR)/lamin_$(ACCESSION)_R2.fastq.gz
TRIMMED_R1 := $(TRIMMED_DIR)/lamin_$(ACCESSION)_R1.trimmed.fastq.gz
TRIMMED_R2 := $(TRIMMED_DIR)/lamin_$(ACCESSION)_R2.trimmed.fastq.gz

ENA_API := https://www.ebi.ac.uk/ena/portal/api
ENA_RUN_INFO := $(ENA_API)/filereport?accession=$(ACCESSION)&result=read_run&fields=run_accession,study_accession,sample_accession,experiment_accession,library_name,instrument_platform,instrument_model,library_strategy,library_source,library_layout,read_count,base_count,fastq_ftp&format=tsv
ENA_LAMIN_QUERY := $(ENA_API)/search?result=read_run&query=tax_tree(7227)%20AND%20description=%22lamin%22&fields=run_accession,study_accession,experiment_accession,instrument_platform,instrument_model,library_strategy,library_layout,read_count,base_count&format=tsv&limit=100

.PHONY: all check-curl check-sra check-fastqc check-fastp metadata download qc-raw trim qc-trimmed clean

all: metadata qc-trimmed

check-curl:
	@command -v curl >/dev/null 2>&1 || { echo "Error: curl is required."; exit 1; }

check-sra:
	@command -v $(SRA_TOOL) >/dev/null 2>&1 || { echo "Error: $(SRA_TOOL) is required."; exit 1; }

check-fastqc:
	@command -v fastqc >/dev/null 2>&1 || { echo "Error: fastqc is required."; exit 1; }

check-fastp:
	@command -v fastp >/dev/null 2>&1 || { echo "Error: fastp is required."; exit 1; }

metadata: check-curl
	mkdir -p $(REPORT_DIR)
	curl --fail --location --retry 3 --output $(REPORT_DIR)/ena_$(ACCESSION).tsv "$(ENA_RUN_INFO)"
	curl --fail --location --retry 3 --output $(REPORT_DIR)/ena_lamin_search.tsv "$(ENA_LAMIN_QUERY)"

download: check-sra
	mkdir -p $(RAW_DIR)
	@if [[ -s "$(RAW_R1)" && -s "$(RAW_R2)" ]]; then \
		echo "Raw FASTQ files already exist; nothing to download."; \
	else \
		$(SRA_TOOL) --split-files --gzip --maxSpotId $(N) --outdir $(RAW_DIR) $(ACCESSION); \
		mv "$(RAW_DIR)/$(ACCESSION)_1.fastq.gz" "$(RAW_R1)"; \
		mv "$(RAW_DIR)/$(ACCESSION)_2.fastq.gz" "$(RAW_R2)"; \
	fi

qc-raw: download check-fastqc
	mkdir -p $(RAW_QC_DIR)
	fastqc --threads $(THREADS) --outdir $(RAW_QC_DIR) $(RAW_R1) $(RAW_R2)

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

qc-trimmed: trim
	mkdir -p $(TRIMMED_QC_DIR)
	fastqc --threads $(THREADS) --outdir $(TRIMMED_QC_DIR) $(TRIMMED_R1) $(TRIMMED_R2)

clean:
	rm -rf data results
