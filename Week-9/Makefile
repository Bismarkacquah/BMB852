# Week 9: reads -> trimmed reads -> BAM -> sample VCFs -> merged VCF.
# See README.md for setup, commands, and resource requirements.
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
.DEFAULT_GOAL := all
# Override settings on the command line, for example OUT=output-fresh.
# THREADS is per sample; make -j controls concurrent jobs.
DESIGN ?= design.csv
OUT ?= output
REFERENCE ?= reference/Phypa_V3.fa
THREADS ?= 2
PYTHON ?= python3
PLOT_PYTHON ?= $(PYTHON)
# Validate the design and create one target per sample at parse time.
SAMPLES := $(shell $(PYTHON) scripts/workflow.py list --design "$(DESIGN)")
ifeq ($(strip $(SAMPLES)),)
$(error Design validation failed; check DESIGN and its required columns)
endif
VCFS := $(addprefix $(OUT)/,$(addsuffix /calls.vcf.gz,$(SAMPLES)))
.PHONY: all batch samples help sample smoke check test analysis report FORCE
# The default design contains all ten samples; plain make runs and merges them.
all: $(OUT)/summary.tsv
batch: all
samples:
	@$(PYTHON) scripts/workflow.py list --design "$(DESIGN)" | tr ' ' '\n'
help:
	@printf '%s\n' 'make samples                 List all samples in design.csv' 'make batch                   Process all ten samples and merge their VCFs' 'make -j2 batch THREADS=3      Process two samples concurrently' 'make sample SAMPLE=ERR8982185 Call one sample' 'make report                  Add coverage and IGV figures (existing IGV required)' 'No software is installed. Inputs are downloaded automatically.'
analysis: batch $(OUT)/analysis.json
sample:
	@test -n "$(SAMPLE)" || { echo 'Set SAMPLE to a sample_id from design.csv' >&2; exit 1; }
	$(MAKE) "$(OUT)/$(SAMPLE)/calls.vcf.gz"
smoke:
	$(MAKE) all DESIGN=design.smoke.csv OUT=output-smoke
check:
	@for tool in python3 bwa samtools bcftools cutadapt; do command -v $$tool >/dev/null || { echo "Missing tool: $$tool" >&2; exit 1; }; done
	$(PYTHON) scripts/workflow.py validate --design "$(DESIGN)"
	@test "$(THREADS)" -gt 0
test:
	$(PYTHON) scripts/test_design.py

# Shared reference: download and index once for all samples.
$(REFERENCE):
	$(PYTHON) scripts/workflow.py reference --reference "$@"
$(REFERENCE).fai: $(REFERENCE)
	samtools faidx "$<"
$(REFERENCE).bwt: $(REFERENCE)
	bwa index "$<"

# Only update this prerequisite when parameters actually change.
$(OUT)/parameters.json: $(REFERENCE) FORCE | check
	$(PYTHON) scripts/workflow.py parameters --reference "$(REFERENCE)" --threads "$(THREADS)" --output "$@"

# Repeat this download/calling recipe for each sample in the design.
# call_from_design.sh handles trimming, alignment, sorting, and filtering.
define sample_rule
$(OUT)/$(1)/calls.vcf.gz: $(DESIGN) scripts/workflow.py scripts/range_stream.py scripts/read_download.py scripts/call_from_design.sh $(REFERENCE) $(REFERENCE).fai $(REFERENCE).bwt $(OUT)/parameters.json
	$(PYTHON) scripts/workflow.py reads --design "$(DESIGN)" --sample "$(1)" --output "$(OUT)/$(1)"
	bash scripts/call_from_design.sh "$(1)" "$(REFERENCE)" "$(OUT)/$(1)" "$(THREADS)" "$(DESIGN)"
endef
$(foreach sample,$(SAMPLES),$(eval $(call sample_rule,$(sample))))

%.vcf.gz.csi: %.vcf.gz
	bcftools index -f "$<"

%.vcf.gz.tbi: %.vcf.gz
	bcftools index -t -f "$<"

# Merge calls; missing genotypes are not assumed to be reference alleles.
$(OUT)/merged.vcf.gz: $(VCFS) $(addsuffix .csi,$(VCFS)) $(DESIGN) Makefile
	bcftools merge -m none -Oz -o "$@.part" $(VCFS)
	mv "$@.part" "$@"

# Summarize calls and validate allele union, sample order, and genotypes.
$(OUT)/summary.tsv: $(OUT)/merged.vcf.gz $(OUT)/merged.vcf.gz.csi scripts/workflow.py
	$(PYTHON) scripts/workflow.py summarize --design "$(DESIGN)" --output "$(OUT)"
	sha256sum $(VCFS) "$(OUT)/merged.vcf.gz" > "$(OUT)/vcf.sha256"

# Optional detailed analysis; ordinary batch runs stop at summary.tsv.
$(OUT)/analysis.json: $(OUT)/summary.tsv scripts/analyze_deep.py
	$(PYTHON) scripts/analyze_deep.py --design "$(DESIGN)" --reference "$(REFERENCE)" --output "$(OUT)" > "$(OUT)/analysis.log"

$(OUT)/igv/render.complete: $(OUT)/analysis.json $(OUT)/merged.vcf.gz.tbi scripts/prepare_igv.py scripts/run_igv.sh scripts/annotate_igv.py
	$(PYTHON) scripts/prepare_igv.py --design "$(DESIGN)" --reference "$(REFERENCE)" --output "$(OUT)"
	bash scripts/run_igv.sh "$(OUT)/igv/ten_samples.batch.txt" > "$(OUT)/igv/render.log" 2>&1
	$(PLOT_PYTHON) scripts/annotate_igv.py --output "$(OUT)"
	touch "$@"

# Requires IGV, Java with a display, and matplotlib.
# Publishes results/, FINDINGS.md, and report provenance.
report: analysis $(OUT)/igv/render.complete
	$(PYTHON) scripts/write_report.py --design "$(DESIGN)" --output "$(OUT)"
