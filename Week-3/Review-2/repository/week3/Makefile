ACCESSION := GCF_900476085.1
ORGANISM := M.gallisepticum

DATA_DIR := data
PACKAGE := $(DATA_DIR)/$(ACCESSION).zip
FNA_FILE := $(DATA_DIR)/fna/$(ORGANISM).fna
GFF_FILE := $(DATA_DIR)/gff/$(ORGANISM).gff

.PHONY: all prepare summary clean

all: summary

prepare:
	@set -eu; \
	if [ -f "$(FNA_FILE)" ] && [ -f "$(GFF_FILE)" ]; then exit 0; fi; \
	command -v datasets >/dev/null 2>&1 || { echo "Error: datasets is required to download the genome." >&2; exit 1; }; \
	command -v unzip >/dev/null 2>&1 || { echo "Error: unzip is required to extract the genome." >&2; exit 1; }; \
	mkdir -p "$(DATA_DIR)" "$(DATA_DIR)/fna" "$(DATA_DIR)/gff"; \
	datasets download genome accession $(ACCESSION) --include genome,gff3 --filename "$(PACKAGE)"; \
	unzip -n "$(PACKAGE)" -d "$(DATA_DIR)"; \
	fna_source=$$(find "$(DATA_DIR)/ncbi_dataset/data" -type f -name '*.fna' -print -quit); \
	gff_source=$$(find "$(DATA_DIR)/ncbi_dataset/data" -type f -name '*.gff' -print -quit); \
	test -n "$$fna_source" && test -n "$$gff_source"; \
	mv "$$fna_source" "$(FNA_FILE)"; \
	mv "$$gff_source" "$(GFF_FILE)"; \
	find "$(DATA_DIR)" -type f \( -name '*.json' -o -name '*.jsonl' -o -name 'md5sum.txt' -o -name 'README.md' \) -delete; \
	rm -rf "$(DATA_DIR)/ncbi_dataset" "$(PACKAGE)"

summary: prepare
	@echo "Genome size: $$(awk '/^>/ {next} {bp += length($$0)} END {print bp + 0}' "$(FNA_FILE)") bp"
	@echo "Chromosomes: $$(awk '/^>/ {count++} END {print count + 0}' "$(FNA_FILE)")"
	@echo "Annotation features: $$(awk 'length($$0) && $$0 !~ /^#/ {count++} END {print count + 0}' "$(GFF_FILE)")"

clean:
	rm -rf "$(DATA_DIR)"
