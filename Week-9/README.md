# Assignment 9: variant calling across ten samples

This workflow calls and merges variants for ten *Physcomitrium patens* samples from study PRJEB51295. Each full-run sample uses 20 million read pairs against the Phypa V3 reference.

Read [FINDINGS.md](FINDINGS.md) for results and interpretation, or [METHODS.md](METHODS.md) for study selection and processing notes.

## Files you need

| File or folder | Purpose |
|---|---|
| `Makefile` | Runs the processing steps described below |
| `design.csv` | Full sample design, read URLs, and settings |
| `design.smoke.csv` | Smaller read limits for a workflow check |
| `scripts/` | Programs used by the Makefile; see the [script guide](scripts/README.md) |
| `results/` | Core saved results: merged VCF, coverage/count tables, validation, settings, and versions |

Historical logs, duplicate test outputs, and example screenshots are excluded from the submission. New working files are written to `output/` and are excluded from Git.

## Setup and first run

Use Linux or WSL with GNU Make, Python 3.11 or newer, BWA, SAMtools, BCFtools, and cutadapt installed. The tested cutadapt version is 5.2. The Makefile checks tools but does not install them.

```bash
git clone https://github.com/Bismarkacquah/BMB852.git
cd BMB852/Week-9
make check
make smoke
```

The smoke test processes 10,000 read pairs per sample and writes to `output-smoke/`. It still downloads and indexes the full reference. Its low-depth results test the workflow and should not be used as the full biological analysis.

## Full analysis

Allow approximately 150 GB free disk space and several hours, depending on the machine and downloads. The saved results can be reviewed without rerunning. The moss reference retains continuity with the completed study analysis; choosing a smaller genome would require a new sample design and analysis.

```bash
make samples
make -j2 batch THREADS=3
```

This runs up to two sample jobs concurrently, with three threads supplied to each sample's processing commands. Use fewer concurrent jobs if memory or disk throughput is limited.

The Makefile connects these stages:

1. Download the reference and build its indexes once for all samples.
2. Download the requested paired reads for each sample.
3. Trim adapters and low-quality sequence.
4. Align reads, then sort and index each BAM.
5. Call, normalize, and filter each sample's variants.
6. Merge the VCFs and validate the allele union, sample order, and carried genotypes.

## Commands and output notes

| Command | Purpose |
|---|---|
| `make help` | Show common commands |
| `make check` | Check tools, design, and thread setting |
| `make samples` | List sample IDs |
| `make smoke` | Run the small ten-sample workflow check |
| `make sample SAMPLE=ERR8982185` | Call one sample from the full design |
| `make batch` | Run all samples and merge calls; also the default target |
| `make analysis` | Add coverage and detailed analysis |
| `make test` | Run design and download helper tests |

FASTQ files contain paired reads; BAM files contain aligned reads; VCF files contain variant calls. Index files allow tools to retrieve genomic regions efficiently.

```bash
cat output/summary.tsv
cat output/validation.json
```

Validation should report `true` for `exact_union_verified` and `genotypes_verified`. These checks confirm that merging preserved the expected records and calls; they do not prove biological accuracy.

If a command fails, address its first error and rerun the same command. Make reuses completed targets whose prerequisites have not changed. `make check` does not check available disk space or install missing software.

Use `OUT=output-fresh` to keep a new run separate. Supply the same `OUT` value to later analysis commands so they use that run's files. No files from earlier weeks are needed.

## Optional figure generation

`make report` retains an optional local IGV reporting workflow. It requires IGV 2.19.8, Java 21 with a working display, and matplotlib 3.10.8. Set `IGV_DIR` to the IGV installation and `PLOT_PYTHON` to a Python interpreter with matplotlib. This updates FINDINGS.md and saved outputs; generated screenshots and detailed logs remain excluded from Git.
