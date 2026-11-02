# Shared preparation, then GNU Parallel dispatches one Make job per CSV row.
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
.DEFAULT_GOAL := help
PYTHON ?= python3
DESIGN ?= design.csv
OUT ?= output
THREADS ?= 4
JOBS ?= 2
REFERENCE ?= reference/Phypa_V3.fa
PARALLEL_CMD ?= parallel
# The dry-run target previews the same dispatch commands without processing data.
PARALLEL_FLAGS = --colsep , --header : --eta --lb -j $(JOBS) --halt soon,fail=1
# Bootstrap must work even if design.csv has not been created yet.
ifneq ($(filter design,$(MAKECMDGOALS)),)
ifneq ($(words $(MAKECMDGOALS)),1)
$(error Run make design separately before analysis targets)
endif
SAMPLES :=
BACKGROUNDS :=
SIGNALS :=
else
SAMPLES := $(shell $(PYTHON) scripts/workflow.py list --design $(DESIGN))
BACKGROUNDS := $(shell $(PYTHON) scripts/workflow.py list --design $(DESIGN) --role background)
SIGNALS := $(shell $(PYTHON) scripts/workflow.py list --design $(DESIGN) --role signal)
ifeq ($(strip $(SAMPLES)),)
$(error Invalid or empty design)
endif
endif
.PHONY: design all batch prepare align sample samples check background peaks report igv help dry-run FORCE
all: batch
design:
	$(PYTHON) scripts/workflow.py build-design --design $(DESIGN)
samples:
	@printf '%s\n' "$(SAMPLES)" | tr ' ' '\n'
help:
	@printf '%s\n' 'make design                  Rebuild the moss design from ENA metadata' 'make batch JOBS=2 THREADS=4   Run CSV jobs with GNU Parallel' 'make dry-run                 Preview per-library commands without processing data' 'make sample SAMPLE=DRR151572 Call one signal with its matched background' 'make background              Process total-H3 libraries' 'make peaks                   Build all four peak sets using Make dependencies' 'make report                  Summarize peak calls and replicate overlap' 'make igv                     Render screenshots (IGV_DIR required)'
check:
	@$(PARALLEL_CMD) --version >/dev/null
	@for tool in bwa samtools bedtools cutadapt macs3; do command -v $$tool >/dev/null || { echo "Missing: $$tool" >&2; exit 1; }; done
	$(PYTHON) scripts/workflow.py validate --design $(DESIGN)
	@test $(THREADS) -gt 0 && test $(JOBS) -gt 0
# Reference/indexes and settings are prepared once before Parallel starts jobs.
$(REFERENCE):
	$(PYTHON) scripts/workflow.py reference --reference $(REFERENCE)
$(REFERENCE).bwt: $(REFERENCE)
	bwa index $(REFERENCE)
$(REFERENCE).fai: $(REFERENCE)
	samtools faidx $(REFERENCE)
$(OUT)/settings.json: FORCE | check
	$(PYTHON) scripts/workflow.py settings --design $(DESIGN) --out $(OUT) --threads $(THREADS) --reference $(REFERENCE)
prepare: $(OUT)/settings.json $(REFERENCE).bwt $(REFERENCE).fai
# Every background finishes before signals start, allowing safe background reuse.
background: prepare
	$(PYTHON) scripts/workflow.py dispatch --design $(DESIGN) --role background | $(PARALLEL_CMD) $(PARALLEL_FLAGS) --joblog $(OUT)/background.jobs.tsv $(MAKE) --no-print-directory -j1 align SAMPLE={sample_id} DESIGN=$(DESIGN) OUT=$(OUT) THREADS=$(THREADS) REFERENCE=$(REFERENCE) PYTHON=$(PYTHON)
batch: background
	$(PYTHON) scripts/workflow.py dispatch --design $(DESIGN) --role signal | $(PARALLEL_CMD) $(PARALLEL_FLAGS) --joblog $(OUT)/signal.jobs.tsv $(MAKE) --no-print-directory -j1 sample SAMPLE={sample_id} DESIGN=$(DESIGN) OUT=$(OUT) THREADS=$(THREADS) REFERENCE=$(REFERENCE) PYTHON=$(PYTHON)
	$(MAKE) --no-print-directory report
# This preview has no preparation prerequisites: no downloads or tool execution.
dry-run:
	$(PYTHON) scripts/workflow.py dispatch --design $(DESIGN) --role background | $(PARALLEL_CMD) $(PARALLEL_FLAGS) --dry-run $(MAKE) --no-print-directory -j1 align SAMPLE={sample_id} DESIGN=$(DESIGN) OUT=$(OUT) THREADS=$(THREADS) REFERENCE=$(REFERENCE) PYTHON=$(PYTHON)
	$(PYTHON) scripts/workflow.py dispatch --design $(DESIGN) --role signal | $(PARALLEL_CMD) $(PARALLEL_FLAGS) --dry-run $(MAKE) --no-print-directory -j1 sample SAMPLE={sample_id} DESIGN=$(DESIGN) OUT=$(OUT) THREADS=$(THREADS) REFERENCE=$(REFERENCE) PYTHON=$(PYTHON)
# Single-library alignment and single-signal peak calling are reusable entry points.
align:
	@test -n "$(filter $(SAMPLE),$(SAMPLES))" || { echo 'Set SAMPLE to a sample_id from design.csv' >&2; exit 1; }
	$(MAKE) "$(OUT)/$(SAMPLE)/aligned.done"
sample:
	@test -n "$(filter $(SAMPLE),$(SIGNALS))" || { echo 'Set SAMPLE to a signal sample_id from design.csv' >&2; exit 1; }
	$(MAKE) "$(OUT)/$(SAMPLE)/peaks.done"
define align_rule
$(OUT)/$(1)/aligned.done: $(DESIGN) scripts/workflow.py scripts/range_stream.py $(OUT)/settings.json $(REFERENCE).bwt $(REFERENCE).fai
	$(PYTHON) scripts/workflow.py align --design $(DESIGN) --sample $(1) --out $(OUT) --reference $(REFERENCE) --threads $(THREADS)
endef
$(foreach s,$(SAMPLES),$(eval $(call align_rule,$(s))))
define peak_rule
$(OUT)/$(1)/peaks.done: $(OUT)/$(1)/aligned.done $(OUT)/$(shell $(PYTHON) scripts/workflow.py background-for --design $(DESIGN) --sample $(1))/aligned.done scripts/workflow.py
	$(PYTHON) scripts/workflow.py peaks --design $(DESIGN) --sample $(1) --out $(OUT)
endef
$(foreach s,$(SIGNALS),$(eval $(call peak_rule,$(s))))
peaks: $(addprefix $(OUT)/,$(addsuffix /peaks.done,$(SIGNALS)))
$(OUT)/summary.done: $(addprefix $(OUT)/,$(addsuffix /peaks.done,$(SIGNALS))) scripts/workflow.py
	$(PYTHON) scripts/workflow.py report --design $(DESIGN) --out $(OUT) --reference $(REFERENCE)
report: $(OUT)/summary.done
# IGV 2.19.8, Java 21, and a working display are needed only for these figures.
igv: report
	$(PYTHON) scripts/workflow.py igv --design $(DESIGN) --out $(OUT) --reference $(REFERENCE)
