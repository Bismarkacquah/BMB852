SHELL := /bin/bash

SPECIES := zygosaccharomyces_bailii_isa1307_gca_000530735
ASSEMBLY := Z_bailii_ISA1307_version_3
RELEASE := 63
BASE_URL := https://ftp.ensemblgenomes.ebi.ac.uk/pub/fungi/release-$(RELEASE)
FASTA_FILE := Zygosaccharomyces_bailii_isa1307_gca_000530735.$(ASSEMBLY).dna.toplevel.fa.gz
GFF_FILE := Zygosaccharomyces_bailii_isa1307_gca_000530735.$(ASSEMBLY).$(RELEASE).gff3.gz

FASTA_URL := $(BASE_URL)/fasta/fungi_ascomycota1_collection/$(SPECIES)/dna/$(FASTA_FILE)
GFF_URL := $(BASE_URL)/gff3/fungi_ascomycota1_collection/$(SPECIES)/$(GFF_FILE)

.PHONY: all fasta gff clean

FASTA_DIR := fasta
GFF_DIR := gff
FASTA_OUTPUT := $(FASTA_DIR)/Z.bailii.fa
GFF_OUTPUT := $(GFF_DIR)/Z.bailii.gff3

all: fasta gff

fasta: $(FASTA_OUTPUT)

gff: $(GFF_OUTPUT)

$(FASTA_OUTPUT):
	mkdir -p $(FASTA_DIR)
	wget --continue --no-verbose --output-document=$@.gz $(FASTA_URL)
	gunzip -c $@.gz > $@ && rm -f $@.gz

$(GFF_OUTPUT):
	mkdir -p $(GFF_DIR)
	wget --continue --no-verbose --output-document=$@.gz $(GFF_URL)
	gunzip -c $@.gz > $@ && rm -f $@.gz

clean:
	rm -f $(FASTA_FILE) $(GFF_FILE) $(FASTA_OUTPUT) $(GFF_OUTPUT)
	rm -rf $(FASTA_DIR) $(GFF_DIR)
