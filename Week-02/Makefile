SHELL := /bin/bash

ASSEMBLY := GCA_000002425.2_Phypa_V3
BASE_URL := https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/002/425/$(ASSEMBLY)
DATA_DIR := data
FASTA_GZ := $(DATA_DIR)/$(ASSEMBLY)_genomic.fna.gz
FASTA := $(DATA_DIR)/$(ASSEMBLY)_genomic.fna
GFF_GZ := $(DATA_DIR)/$(ASSEMBLY)_genomic.gff.gz
GTF_GZ := $(DATA_DIR)/$(ASSEMBLY)_genomic.gtf.gz
GFF := $(DATA_DIR)/$(ASSEMBLY)_genomic.gff
GTF := $(DATA_DIR)/$(ASSEMBLY)_genomic.gtf

.PHONY: all download annotate count clean

all: download annotate count

download:
	mkdir -p $(DATA_DIR)
	curl -C - -fL --output $(FASTA_GZ) "$(BASE_URL)/$(ASSEMBLY)_genomic.fna.gz"
	curl -C - -fL --output $(GFF_GZ) "$(BASE_URL)/$(ASSEMBLY)_genomic.gff.gz"
	curl -C - -fL --output $(GTF_GZ) "$(BASE_URL)/$(ASSEMBLY)_genomic.gtf.gz"
	gunzip -kf $(FASTA_GZ)
	gunzip -kf $(GFF_GZ)
	gunzip -kf $(GTF_GZ)
	if command -v samtools >/dev/null 2>&1; then samtools faidx $(FASTA); fi

annotate: download
	@echo "Genome-wide annotation files are available at $(GFF) and $(GTF)."

count: annotate
	@echo "GFF3 annotation counts"
	awk '!/^#/ && NF >= 3 { count[$$3]++; total++ } END { for (k in count) print k, count[k]; print "TOTAL", total }' $(GFF) | sort -k2,2nr
	@echo "FASTA sequence records: $$(grep -c '^>' $(FASTA))"
	@echo "FASTA total bases: $$(awk '/^>/ { next } { bp += length($$0) } END { print bp }' $(FASTA))"

clean:
	rm -rf $(DATA_DIR)
