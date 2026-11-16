PYTHON ?= python3
SALMON ?= salmon
THREADS ?= 4
SOURCE ?=

.PHONY: help all data index quant matrices test
.DELETE_ON_ERROR:

help:
	@echo 'make all                  Download data, quantify transcripts, build both matrices'
	@echo 'make all SOURCE=../Week11  Reuse the extracted Week 11 teaching data'
	@echo 'make matrices             Rebuild matrices from existing quant.sf files'

data:
	$(PYTHON) src/workflow.py data $(if $(SOURCE),--source "$(SOURCE)",)

index: data
	$(PYTHON) src/workflow.py index --salmon "$(SALMON)" --threads $(THREADS)

quant: index
	$(PYTHON) src/workflow.py quant --salmon "$(SALMON)" --threads $(THREADS)

matrices:
	$(PYTHON) src/matrices.py

all: quant
	$(PYTHON) src/matrices.py

test:
	$(PYTHON) -m unittest discover -s src -p 'test_*.py'
