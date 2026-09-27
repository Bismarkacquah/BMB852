SHELL := /bin/bash

REFERENCE := ../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.fna
ANNOTATION := ../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.gff
READ1 := ../Week-4/data/trimmed/ERR8982185_1.trimmed.fastq.gz
READ2 := ../Week-4/data/trimmed/ERR8982185_2.trimmed.fastq.gz
RESULTS := results
INDEX := $(REFERENCE)
SAM := $(RESULTS)/alignments/ERR8982185.sam
BAM := $(RESULTS)/alignments/ERR8982185.sorted.bam
STATS := $(RESULTS)/alignments/ERR8982185.flagstat.txt
DEPTH := $(RESULTS)/coverage/ERR8982185.depth.tsv
THREADS ?= 2
BWA ?= bwa
SAMTOOLS ?= samtools

# Approximate minimum spots for 10x using 471,852,792 bp and 292.7 kb per pair.
TARGET_COVERAGE ?= 10
READ_PAIRS_FOR_10X ?= 16122

.PHONY: help check-inputs dirs estimate index align sort index-bam stats depth all clean

help:
	@echo "Week 5 Physcomitrium downstream analysis"
	@echo "  make check-inputs  Verify shared Week 2 and Week 4 files"
	@echo "  make dirs          Create Week 5 output directories"
	@echo "  make estimate      Report the read count needed for 10x coverage"
	@echo "  make index         Build the aligner reference index"
	@echo "  make align         Align trimmed paired reads"
	@echo "  make all           Build, sort, index, and summarize the BAM"

check-inputs:
	test -s $(REFERENCE)
	test -s $(ANNOTATION)
	test -s $(READ1)
	test -s $(READ2)
	@echo "Shared Physcomitrium reference and trimmed reads are available."

estimate:
	@echo "Genome size: 471852792 bp"
	@echo "Target coverage: $(TARGET_COVERAGE)x"
	@echo "Estimated read pairs required: $(READ_PAIRS_FOR_10X)"
	@echo "The current Week-4 subset contains only 997 trimmed pairs."

index: check-inputs dirs
	$(BWA) index $(REFERENCE)

align: index
	$(BWA) mem -t $(THREADS) $(REFERENCE) $(READ1) $(READ2) > $(SAM)

sort: align
	$(SAMTOOLS) sort -@ $(THREADS) -o $(BAM) $(SAM)
	rm -f $(SAM)

index-bam: sort
	$(SAMTOOLS) index $(BAM)

stats: index-bam
	$(SAMTOOLS) flagstat $(BAM) | tee $(STATS)

depth: index-bam
	$(SAMTOOLS) depth -aa $(BAM) > $(DEPTH)

all: stats depth

dirs:
	mkdir -p $(RESULTS)/alignments $(RESULTS)/coverage $(RESULTS)/figures

clean:
	rm -rf $(RESULTS)
