SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
.DEFAULT_GOAL := all
DESIGN ?= design.tsv
OUT ?= output
REFERENCE ?= reference/Phypa_V3.fa
THREADS ?= 2
PYTHON ?= python3
SAMPLES := $(shell $(PYTHON) scripts/workflow.py list --design "$(DESIGN)")
ifeq ($(strip $(SAMPLES)),)
$(error Design validation failed; check DESIGN and its required columns)
endif
VCFS := $(addprefix $(OUT)/,$(addsuffix /calls.vcf.gz,$(SAMPLES)))
.PHONY: all check test FORCE
all: $(OUT)/summary.tsv
check:
	@for tool in python3 bwa samtools bcftools; do command -v $$tool >/dev/null || { echo "Missing tool: $$tool" >&2; exit 1; }; done
	$(PYTHON) scripts/workflow.py validate --design "$(DESIGN)"
	@test "$(THREADS)" -gt 0
test:
	$(PYTHON) scripts/test_design.py

$(REFERENCE):
	$(PYTHON) scripts/workflow.py reference --reference "$@"
$(REFERENCE).fai: $(REFERENCE)
	samtools faidx "$<"
$(REFERENCE).bwt: $(REFERENCE)
	bwa index "$<"

# Only update this prerequisite when parameters actually change.
$(OUT)/parameters.json: $(REFERENCE) FORCE | check
	$(PYTHON) scripts/workflow.py parameters --reference "$(REFERENCE)" --threads "$(THREADS)" --output "$@"

define sample_rule
$(OUT)/$(1)/calls.vcf.gz: $(DESIGN) scripts/workflow.py scripts/call_sample.sh $(REFERENCE) $(REFERENCE).fai $(REFERENCE).bwt $(OUT)/parameters.json
	$(PYTHON) scripts/workflow.py reads --design "$(DESIGN)" --sample "$(1)" --output "$(OUT)/$(1)"
	bash scripts/call_sample.sh "$(1)" "$(REFERENCE)" "$(OUT)/$(1)" "$(THREADS)" "$(DESIGN)"
endef
$(foreach sample,$(SAMPLES),$(eval $(call sample_rule,$(sample))))

%.vcf.gz.csi: %.vcf.gz
	bcftools index -f "$<"

$(OUT)/merged.vcf.gz: $(VCFS) $(addsuffix .csi,$(VCFS)) $(DESIGN) Makefile
	bcftools merge -m none -Oz -o "$@.part" $(VCFS)
	mv "$@.part" "$@"

$(OUT)/summary.tsv: $(OUT)/merged.vcf.gz $(OUT)/merged.vcf.gz.csi scripts/workflow.py
	$(PYTHON) scripts/workflow.py summarize --design "$(DESIGN)" --output "$(OUT)"
	sha256sum $(VCFS) "$(OUT)/merged.vcf.gz" > "$(OUT)/vcf.sha256"
