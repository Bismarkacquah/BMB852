# Reproduce Week 8

Use Linux or Ubuntu under WSL2. Run the commands below in a Bash terminal. Keep the whole repository, since the read downloader imports a helper from `Week-7/scripts/`. You need Git, Conda or Mamba, internet access, sufficient free disk space for five sets of reads and BAMs, and a working graphical display for IGV. Full read processing can take many hours and requires substantially more space than the published VCFs and figures.

## 1. Get the project and software

```bash
git clone https://github.com/Bismarkacquah/BMB852.git
cd BMB852/Week-8
conda env create -f environment.yml
conda activate bmmb852-week8
make check-tools
```

`git clone` downloads the entire repository. `cd` selects this assignment folder. The environment command installs the declared analysis and plotting tools. Activation makes those programs available to subsequent commands. `make check-tools` checks that the main executables can be found. Git and Conda must already be installed.

## 2. Choose what to reproduce

### Recreate the summary figures using the published VCF

This route does not download sequencing reads or align them again:

```bash
sha256sum -c provenance/final-deliverables.sha256
python scripts/summarize_effects.py results/five_samples.annotated.vcf.gz --output results
python scripts/plot_comparisons.py
python scripts/visualize_merged.py
python scripts/annotate_igv.py
```

The first command verifies the published VCF and figure files. The next command reads the VCF annotations and recreates the effect tables. The plotting commands recreate the comparison plots and whole-VCF overview. The final command adds the labeled rectangles to the supplied original IGV screenshots. It does not re-open BAM files or claim to regenerate their underlying alignments. The comparison plots use the published numerical distributions; a full recalculation from reads is the route below.

### Rebuild from sequencing reads

```bash
make setup-reference
make setup-annotation
make test
make -B all THREADS=4 PAIRS=20000000
```

`setup-reference` downloads missing files for the exact assembly and builds missing indexes. `setup-annotation` installs SnpEff and checks its archive/JAR hashes against the recorded hashes. `test` checks merge and annotation handling using temporary fixtures. `-B` forces Make to revisit the analysis targets, including the published sample VCFs. Each sample's processing script checks its own input signature before deciding whether local work can be reused. In a new clone, the excluded raw reads and BAMs are downloaded/generated. The original Week 7 sample is processed in Week 8 when its reusable BAM/VCF inputs are absent.

Keep `PAIRS=20000000` to reproduce this assignment's deterministic first-20-million-pair subsets. `THREADS=4` controls per-sample processing workers. Avoid launching multiple copies of the workflow. Use the same terminal/environment for every command.

The SnpEff download endpoint is maintained upstream. If its contents change, the recorded checksum check should fail. Do not silently remove the checksum check or describe a different version as an exact reproduction. The tested tool versions and software hashes are recorded under `provenance/`.

## 3. Recreate coverage measurements and actual IGV screenshots

Install the Linux distribution of IGV 2.19.8 separately, with its bundled Java 21. Extract it to a location you choose. Then replace the example path below with that directory:

```bash
export IGV_DIR=/absolute/path/to/IGV_Linux_2.19.8
test -f "$IGV_DIR/igv.args"
test -d "$IGV_DIR/lib"
printf 'Display: %s\n' "${DISPLAY:-not set}"
make -B report THREADS=4 PAIRS=20000000
```

`IGV_DIR` tells the included launcher where IGV is installed. The `test` commands check its expected layout. IGV needs a functioning graphical display, such as a Linux desktop or WSLg. Setting `DISPLAY` to an arbitrary value does not create a display. On a headless server, configure a working virtual X display before running the snapshot stage.

The report target recalculates coverage and comparison outputs, prepares a batch file with paths for your checkout, opens all five BAMs with the merged VCF in IGV, saves original screenshots, adds the rectangles, and writes the report. Do not use the published session's workstation paths directly. `scripts/prepare_igv.py`, invoked by Make, regenerates them for your local files.

The annotation software and graphics runtime can affect formatting. Identical variant counts and checked genotypes are more meaningful than pixel-identical screenshots across different operating systems.

## 4. Verify the new outputs

```bash
make test
bcftools query -l results/five_samples.annotated.vcf.gz
bcftools index -n results/five_samples.annotated.vcf.gz
python -m json.tool results/comparison_summary.json
sha256sum -c provenance/final-deliverables.sha256
```

Expected sample IDs, in order: `ERR8982183`, `ERR8982184`, `ERR8982185`, `ERR8982186`, `ERR8982187`. The published analysis has **39,458 allele records**, including **32,276 SNPs** and **7,182 indels**. In `comparison_summary.json`, `exact_union_verified` and `sample_genotypes_verified` must be `true`. The report generator writes checksums for your generated artifacts, so the final checksum command verifies their subsequent integrity; it does not alone prove agreement with the originally published bytes.

If processing stops, read the relevant sample log in `samples/RUN/` or the stage log in `provenance/`. Correct the reported problem before rerunning. Keep intermediate files to allow completed work to be reused. Missing calls in the merged VCF remain unknown rather than being changed to reference genotypes.

See [every analytical command and option](CODE_GUIDE.md), [the Makefile](Makefile), [the measured report](README.md), and [detailed interpretation](RESULTS_EXPLAINED.md).
