# Initial Week 8 input validation and gene-overlap analysis.
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
PYTHON ?= python3
VCF ?= ../Week-7/expanded/results/ERR8982185.20M.pass.vcf.gz
REFERENCE ?= ../Week-5/fasta/GCA_000002425.2_Phypa_V3_genomic.fna
GFF ?= ../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.gff

SAMPLES := ERR8982183 ERR8982184 ERR8982185 ERR8982186 ERR8982187
PAIRS ?= 20000000
THREADS ?= 4
VCFS := $(foreach run,$(SAMPLES),samples/$(run)/$(run).pass.vcf.gz)
SNPEFF_JAR ?= tools/snpEff/snpEff.jar
SNPEFF_URL ?= https://snpeff-public.s3.amazonaws.com/versions/snpEff_latest_core.zip
GENOME := Phypa_V3
PLOT_PYTHON ?= $(if $(wildcard tools/plotenv/bin/python),tools/plotenv/bin/python,$(PYTHON))

.PHONY: all inspect check-inputs check-tools merge annotate FORCE
all: results/five_samples.annotated.vcf.gz.csi results/five_samples.annotated.vcf.gz.tbi results/effect_summary.json
check-tools:
	@for tool in python3 cutadapt bwa samtools bcftools java; do command -v $$tool; done
check-inputs:
	@test -s "$(VCF)" && test -s "$(REFERENCE)" && test -s "$(REFERENCE).fai" && test -s "$(GFF)"
inspect: check-inputs
	$(PYTHON) scripts/inspect_inputs.py --vcf "$(VCF)" --reference "$(REFERENCE)" --gff "$(GFF)" --output results

provenance/pipeline-parameters.txt: FORCE
	mkdir -p provenance
	printf '%s\n' 'PAIRS=$(PAIRS)' 'REFERENCE=$(REFERENCE)' 'PLOIDY=1' 'MIN_MQ=20' 'MIN_BQ=20' 'MIN_QUAL=20' 'MIN_DP=3' > $@.tmp
	if ! cmp -s $@.tmp $@; then mv $@.tmp $@; else rm $@.tmp; fi

define sample_rule
samples/$(1)/$(1).pass.vcf.gz: scripts/process_sample.sh scripts/download_sample.py scripts/check_download.py provenance/study-runs.tsv provenance/pipeline-parameters.txt $(REFERENCE) $(REFERENCE).fai $(REFERENCE).bwt | check-tools
	bash scripts/process_sample.sh $(1) "$(REFERENCE)" $(PAIRS) $(THREADS)
endef
$(foreach run,$(SAMPLES),$(eval $(call sample_rule,$(run))))

results/five_samples.vcf.gz: $(VCFS) Makefile
	mkdir -p results provenance
	bcftools --version > provenance/week8-tool-versions.txt
	bcftools merge -m none -Oz -o $@ $(VCFS) 2> provenance/merge.log
	bcftools query -l $@ > results/merged_samples.txt
	test "$$(wc -l < results/merged_samples.txt)" -eq 5
	bcftools norm -f "$(REFERENCE)" -c e -Ov $@ > /dev/null
	bcftools stats -s - $@ > results/five_samples.stats.txt
	sha256sum $(VCFS) $@ > provenance/merged.sha256

%.vcf.gz.csi: %.vcf.gz
	bcftools index -f $<
%.vcf.gz.tbi: %.vcf.gz
	bcftools index -t -f $<
merge: results/five_samples.vcf.gz.csi

annotation/data/$(GENOME)/snpEffectPredictor.bin: $(REFERENCE) $(GFF) $(SNPEFF_JAR)
	mkdir -p annotation/data/$(GENOME) provenance
	ln -sfn "$$(realpath $(REFERENCE))" annotation/data/$(GENOME)/sequences.fa
	ln -sfn "$$(realpath $(GFF))" annotation/data/$(GENOME)/genes.gff
	printf '%s\n' 'data.dir = ./data' '$(GENOME).genome : Physcomitrium patens Phypa V3' > annotation/snpEff.config
	cd annotation && java -Xmx4g -jar "$$(realpath ../$(SNPEFF_JAR))" build -gff3 -noCheckCds -noCheckProtein -v -c snpEff.config $(GENOME) > ../provenance/snpeff-build.log 2>&1

results/five_samples.annotated.vcf.gz: results/five_samples.vcf.gz.csi annotation/data/$(GENOME)/snpEffectPredictor.bin scripts/fix_ann_delimiters.py
	java -Xmx4g -jar $(SNPEFF_JAR) -c annotation/snpEff.config -dataDir "$$(realpath annotation/data)" -noDownload -noStats -v $(GENOME) results/five_samples.vcf.gz 2> provenance/snpeff-annotation.log | $(PYTHON) scripts/fix_ann_delimiters.py --gff "$(GFF)" 2> provenance/ann-delimiter-fix.log | bcftools view -Oz -o $@
	bcftools stats -s - $@ > results/five_samples.annotated.stats.txt
annotate: results/five_samples.annotated.vcf.gz.csi

results/effect_summary.json: results/five_samples.annotated.vcf.gz scripts/summarize_effects.py
	$(PYTHON) scripts/summarize_effects.py $< --output results > provenance/effect-summary.log

.PHONY: setup-annotation test
setup-annotation:
	mkdir -p tools provenance
	curl -fL --retry 3 $(SNPEFF_URL) -o tools/snpeff.zip
	$(PYTHON) -m zipfile -e tools/snpeff.zip tools
	if test -s provenance/snpeff-software.sha256; then sha256sum -c provenance/snpeff-software.sha256; fi
	java -jar $(SNPEFF_JAR) -version > provenance/snpeff-version.txt 2>&1
	sha256sum tools/snpeff.zip $(SNPEFF_JAR) > provenance/snpeff-software.sha256
test:
	$(PYTHON) scripts/test_merge.py
	$(PYTHON) scripts/test_ann_format.py

.PHONY: setup-reference analysis figures igv report
setup-reference:
	$(PYTHON) scripts/fetch_reference.py --reference "$(REFERENCE)" --gff "$(GFF)"
	test -s "$(REFERENCE).fai" || samtools faidx "$(REFERENCE)"
	test -s "$(REFERENCE).bwt" || bwa index "$(REFERENCE)"

results/comparison_summary.json: $(VCFS) results/five_samples.annotated.vcf.gz scripts/analyze_multisample.py
	$(PYTHON) scripts/analyze_multisample.py --reference "$(REFERENCE)" > provenance/comparison.log
results/coverage_comparison.json: $(VCFS) scripts/collect_coverage.py
	$(PYTHON) scripts/collect_coverage.py --reference "$(REFERENCE)" > provenance/coverage.log
analysis: all results/comparison_summary.json results/coverage_comparison.json

png/01_sample_variant_counts.png png/02_quality_depth.png png/03_predicted_impacts.png png/04_observed_call_overlap.png &: results/comparison_summary.json results/effect_summary.json scripts/plot_comparisons.py
	$(PLOT_PYTHON) scripts/plot_comparisons.py > provenance/figures.log
figures: png/01_sample_variant_counts.png png/02_quality_depth.png png/03_predicted_impacts.png png/04_observed_call_overlap.png

png/08_all_merged_variants.png png/09_all_call_patterns.png results/WHOLE_VCF_ANALYSIS.md &: results/five_samples.annotated.vcf.gz results/comparison_summary.json scripts/visualize_merged.py
	$(PLOT_PYTHON) scripts/visualize_merged.py > provenance/whole-vcf-visualization.log
figures: png/08_all_merged_variants.png png/09_all_call_patterns.png results/WHOLE_VCF_ANALYSIS.md

igv/five_samples.batch.txt: results/comparison_summary.json results/five_samples.annotated.vcf.gz.tbi scripts/prepare_igv.py $(GFF)
	$(PYTHON) scripts/prepare_igv.py --reference "$(REFERENCE)" --gff "$(GFF)" > provenance/igv-prepare.log 2>&1
igv/snapshots.complete: igv/five_samples.batch.txt scripts/run_igv.sh
	bash scripts/run_igv.sh > provenance/igv-render.log 2>&1
	test -s png/05_five_sample_genotypes.png && test -s png/06_candidate_1.png && test -s png/07_regional_coverage.png
	touch $@
igv: igv/snapshots.complete

png/10_annotated_candidate_1.png png/10_annotated_candidate_2.png png/10_annotated_candidate_3.png &: igv/snapshots.complete scripts/annotate_igv.py
	$(PLOT_PYTHON) scripts/annotate_igv.py
figures: png/10_annotated_candidate_1.png png/10_annotated_candidate_2.png png/10_annotated_candidate_3.png

results/report.complete: analysis figures igv scripts/write_report.py
	$(PYTHON) scripts/write_report.py
	touch $@
report: results/report.complete
