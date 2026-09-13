SHELL := /bin/sh

ACCESSION := NC_001367.1

FASTA_URL := https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=$(ACCESSION)&rettype=fasta&retmode=text
GFF_URL := https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=$(ACCESSION)&rettype=gff3&retmode=text

FASTA_DIR := fasta
GFF_DIR := gff

FASTA := $(FASTA_DIR)/$(ACCESSION).fasta
GFF := $(GFF_DIR)/$(ACCESSION).gff3

.PHONY: all genome clean

all: genome

genome: $(FASTA) $(GFF)

$(FASTA_DIR):
	mkdir -p $@

$(GFF_DIR):
	mkdir -p $@

$(FASTA): | $(FASTA_DIR)
	curl --fail --location --retry 3 --output $@ '$(FASTA_URL)'

$(GFF): | $(GFF_DIR)
	curl --fail --location --retry 3 --output $@ '$(GFF_URL)'

clean:
	rm -rf $(FASTA_DIR) $(GFF_DIR)
