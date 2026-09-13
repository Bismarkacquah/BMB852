SHELL := /bin/bash

ASSEMBLY := GCF_000001215.4_Release_6_plus_ISO1_MT
BASE_URL := https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/215/$(ASSEMBLY)
DATA_DIR := data
FASTA_GZ := $(DATA_DIR)/$(ASSEMBLY)_genomic.fna.gz
FASTA := $(DATA_DIR)/$(ASSEMBLY)_genomic.fna
GFF_GZ := $(DATA_DIR)/$(ASSEMBLY)_genomic.gff.gz
GTF_GZ := $(DATA_DIR)/$(ASSEMBLY)_genomic.gtf.gz
LAMIN_GFF := $(DATA_DIR)/lamin_annotation.gff3
LAMIN_GTF := $(DATA_DIR)/lamin_annotation.gtf

.PHONY: all download annotate count clean

all: download annotate count

download:
	mkdir -p $(DATA_DIR)
	curl -C - -fL --output $(FASTA_GZ) "$(BASE_URL)/$(ASSEMBLY)_genomic.fna.gz"
	curl -C - -fL --output $(GFF_GZ) "$(BASE_URL)/$(ASSEMBLY)_genomic.gff.gz"
	curl -C - -fL --output $(GTF_GZ) "$(BASE_URL)/$(ASSEMBLY)_genomic.gtf.gz"
	gunzip -kf $(FASTA_GZ)
	if command -v samtools >/dev/null 2>&1; then samtools faidx $(FASTA); fi

annotate: download
	zcat $(GFF_GZ) | awk 'BEGIN { IGNORECASE=1 } /^#/ || $$0 ~ /(^|[;\t ])(gene|gene_name|Name|gene_id)[= ]"?Lam"?([; ]|$$)/ { print }' > $(LAMIN_GFF)
	zcat $(GTF_GZ) | awk 'BEGIN { IGNORECASE=1 } /^#/ || $$0 ~ /(^|[;\t ])(gene|gene_name|Name|gene_id)[= ]"?Lam"?([; ]|$$)/ { print }' > $(LAMIN_GTF)

count: annotate
	@echo "GFF3 annotation counts"
	zcat $(GFF_GZ) | awk '!/^#/ && NF >= 3 { count[$$3]++; total++ } END { for (k in count) print k, count[k]; print "TOTAL", total }' | sort -k2,2nr
	@echo "Lamin-only GFF3 records: $$(grep -v '^#' $(LAMIN_GFF) 2>/dev/null | awk 'NF { n++ } END { print n + 0 }')"
	@echo "Lamin-only GTF records: $$(grep -v '^#' $(LAMIN_GTF) 2>/dev/null | awk 'NF { n++ } END { print n + 0 }')"

clean:
	rm -rf $(DATA_DIR)
