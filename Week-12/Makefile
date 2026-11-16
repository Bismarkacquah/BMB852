PYTHON ?= python3
SALMON ?= salmon
THREADS ?= 4
SOURCE ?=

.PHONY: help all data download index quant matrices gene transcript compare
.DELETE_ON_ERROR:

help:
	@echo 'make all                  Download data, quantify transcripts, build both matrices'
	@echo 'make all SOURCE=../Week11  Reuse the extracted Week 11 teaching data'
	@echo 'make matrices             Rebuild matrices from existing quant.sf files'
	@echo 'make gene / transcript    Build the selected count matrix'
	@echo 'make compare              Add gene names, compare counts, and update examples'

download: data

data:
	$(PYTHON) src/workflow.py data $(if $(SOURCE),--source "$(SOURCE)",)

index: data
	$(PYTHON) src/workflow.py index --salmon "$(SALMON)" --threads $(THREADS)

quant: index
	$(PYTHON) src/workflow.py quant --salmon "$(SALMON)" --threads $(THREADS)

matrices:
	$(PYTHON) src/matrices.py

gene:
	$(PYTHON) src/matrices.py --level gene

transcript:
	$(PYTHON) src/matrices.py --level transcript

compare: matrices
	$(PYTHON) src/check_counts.py

all: quant
	$(PYTHON) src/matrices.py
	$(PYTHON) src/check_counts.py
