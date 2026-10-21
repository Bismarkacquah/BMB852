# Week 9 Assignment

## Design-driven variant calling

This workflow processes ten paired-end *Physcomitrium patens* runs from [PRJEB51295](https://www.ebi.ac.uk/ena/browser/view/PRJEB51295), using the Week 7 reference, [GCA_000002425.2](https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_000002425.2/). Each row in [design.tsv](design.tsv) specifies a sample ID, study label, group, BioSample, two public FASTQ URLs, read-pair count, and ploidy.

## Run

Use a Linux/WSL Bash terminal with the existing **bioinfo environment active**, internet access, and several GB of free disk space. No additional tools or automatic installation steps are required.

```bash
git clone https://github.com/Bismarkacquah/BMB852.git
cd BMB852/Week-9
make check
make test
make -j2
cat output/summary.tsv
```

The [Makefile](Makefile) downloads and checks the exact reference, prepares its indexes, downloads synchronized paired-read subsets, aligns each sample, calls and filters variants, and merges the sample VCFs. Two samples run concurrently, with two threads per sample by default. Use `make` for serial sample processing or `make -j2 THREADS=4` to change the per-sample thread count.

The final files are `output/merged.vcf.gz`, its `.csi` index, `output/summary.tsv`, and `output/validation.json`. Logs and read manifests are saved in each sample directory. `output/vcf.sha256` records VCF checksums. Repeating `make` reuses completed work; changing the design or analysis scripts rebuilds the affected outputs. Failed commands stop the workflow rather than marking a failed stage complete.

To change samples or depth, edit the design rows, or use `make DESIGN=my_design.tsv OUT=my_output`. Sample IDs must be unique; the design requires at least two samples for merging. Preserve the tab-separated columns. The reference checksum and analysis settings are recorded in `output/parameters.json`. No earlier-week files are needed.

## Findings

The ten-sample demonstration used the first **10,000 read pairs per run** and produced **561 distinct merged allele records**. The workflow verified sample order, the exact union of sample alleles, and preservation of sample genotypes. Missing calls remain unknown, rather than being converted to reference genotypes.

This small, deterministic subset tests automation and reproducibility. It is much shallower than Week 8 and is unsuitable for comparing mutation burdens or identifying treatment-specific changes. The `pairs` column can be increased for deeper analysis; doing so increases download, storage, and processing time. The `ploidy=1` setting follows the earlier moss analysis and remains an explicit assumption.

An isolated copy successfully downloaded its own reference and reads and reproduced the same VCF data. Repeating `make -j2` reused completed work. See the [verification record](provenance/verification.txt).

See the [recorded sample counts](results/summary.tsv), [merged VCF](results/merged.vcf.gz), [merge validation](results/validation.json), and [data provenance and filtering settings](provenance/README.md).
