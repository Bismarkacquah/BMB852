# Execute recipes in Bash and stop if any command in a pipeline fails.
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
# A plain make runs the analysis rather than only printing help.
.DEFAULT_GOAL := all
# Remove incomplete target files after a failed recipe.
.DELETE_ON_ERROR:
# Fixed inputs match the submitted moss analysis.
REFERENCE := fasta/GCA_000002425.2_Phypa_V3_genomic.fna
ANNOTATION := ../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.gff
READ1 := ../Week-4/data/trimmed/ERR8982185_1.trimmed.fastq.gz
READ2 := ../Week-4/data/trimmed/ERR8982185_2.trimmed.fastq.gz
# Name alignment and coverage outputs once for reuse below.
BAM := bam/ERR8982185.sorted.bam
STATS := bam/ERR8982185.flagstat.txt
COVERAGE := coverage/ERR8982185.coverage.tsv
DEPTH := coverage/ERR8982185.covered_depth.tsv
SUMMARY := coverage/ERR8982185.depth_summary.json
# Allow the thread count to be overridden, for example make THREADS=4.
THREADS ?= 2
# These names are commands, not files that Make should look for.
.PHONY: all setup check-tools check-inputs reference index align sort index-bam stats coverage depth estimate igv
# Build compact summaries; the 10 GB all-position depth file is unnecessary.
all: $(STATS) $(COVERAGE) $(SUMMARY)
# Download missing inputs without replacing existing nonempty input files.
setup:
	bash scripts/prepare_inputs.sh
# Check the tools used for alignment and summarization.
check-tools:
	command -v bwa
	command -v samtools
	command -v python3
# Verify all four required inputs are nonempty.
check-inputs:
	test -s $(REFERENCE)
	test -s $(ANNOTATION)
	test -s $(READ1)
	test -s $(READ2)
# Keep convenient names for individual stages.
reference: $(REFERENCE).fai
index: $(REFERENCE).bwt
align sort: $(BAM)
index-bam: $(BAM).bai
stats: $(STATS)
coverage: $(COVERAGE)
depth: $(DEPTH)
estimate: $(SUMMARY)
	cat $(SUMMARY)
# BWA builds its companion index files from the reference FASTA.
$(REFERENCE).bwt: $(REFERENCE)
	bwa index $<
# Samtools makes the random-access FASTA index needed by IGV.
$(REFERENCE).fai: $(REFERENCE)
	samtools faidx $<
# Map paired reads and stream alignments directly into coordinate sorting.
$(BAM): $(REFERENCE).bwt $(REFERENCE).fai $(READ1) $(READ2)
	mkdir -p bam
	bwa mem -t $(THREADS) $(REFERENCE) $(READ1) $(READ2) | samtools sort -@ $(THREADS) -o $@
	samtools quickcheck $@
# Index the sorted BAM for region queries and IGV navigation.
$(BAM).bai: $(BAM)
	samtools index $<
# Write alignment-flag counts and percentages.
$(STATS): $(BAM) $(BAM).bai
	samtools flagstat $(BAM) > $@
# Write one coverage summary row per reference sequence.
$(COVERAGE): $(BAM) $(BAM).bai
	mkdir -p coverage
	samtools coverage $(BAM) > $@
# Write sparse position depths; the FASTA index supplies the whole-genome denominator.
$(DEPTH): $(BAM) $(BAM).bai
	mkdir -p coverage
	samtools depth $(BAM) > $@
# Calculate exact depth statistics and the read-pair estimate from the inputs.
$(SUMMARY): $(DEPTH) $(REFERENCE).fai $(READ1) $(READ2) scripts/summarize_depth.py
	python3 scripts/summarize_depth.py
# Generate an IGV batch file containing paths for this checkout.
igv:
	python3 scripts/prepare_igv.py

# Recreate selected-region base observations and read-support pileups.
.PHONY: audit
audit: $(BAM).bai $(REFERENCE).fai
	python3 scripts/audit_mismatches.py
	samtools mpileup -B -Q 0 -f $(REFERENCE) -r CM009336.1:3475540-3475640 $(BAM) > bam/ERR8982185.zoom.pileup.txt
	samtools mpileup -B -Q 0 -f $(REFERENCE) -r CM009316.1:618250-618310 $(BAM) > bam/ERR8982185.read_end.pileup.txt
