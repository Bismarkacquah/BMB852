# Week 12: Generate RNA-Seq count matrices

I used Salmon to quantify transcripts in three Human Brain Reference (HBR) and three Universal Human Reference (UHR) samples from the chr22 teaching dataset used in Week 11. I then generated two matrices from the same quantification results:

- [Transcript counts](results/transcript_counts.tsv): **4,506 transcripts × 6 samples**.
- [Gene counts](results/gene_counts.tsv): **1,371 genes × 6 samples**.

Each row is a transcript or gene, and columns follow [design.csv](design.csv). Counts come from Salmon's **NumReads**, not TPM. They are estimated read counts and can be fractional. Gene counts are the sum of all transcript counts assigned to that gene in `chr22.gtf`; no rounding or normalization is applied.

## How to run

Use Linux, macOS, or Ubuntu in WSL with Python **3.9+**, GNU Make, and Salmon on `PATH`. Python uses only its standard library. The completed run used **Salmon 2.8.0**; its version is recorded in [software_versions.txt](software_versions.txt).

From this directory:

```bash
# Download the teaching data, build the index, quantify all six samples,
# and generate transcript-level and gene-level matrices.
make all

# Run the regression check.
make test
```

The data download is approximately 71 MB. `src/workflow.py` downloads [rnaseq-tutorial-2026.tar.gz](https://data.biostarhandbook.com/data/rnaseq-tutorial-2026.tar.gz) and copies only the required transcript FASTA, GTF, and six FASTQ files from the archive into `data/`. Input SHA-256 checksums are recorded in [input_checksums.json](input_checksums.json).

If the tutorial data are already extracted locally, reuse them:

```bash
# For the local Week12/ and Week11/ directory layout:
make all SOURCE=../Week11

# For this GitHub repository's Week-12/ and Week-11/ layout:
make all SOURCE=../Week-11
```

The source directory must contain `fasta/chr22.transcripts.fa`, `gtf/chr22.gtf`, and the six `fastq/*_R1.fq` files. Large data and index files are excluded from GitHub. A fresh clone can use `make all` to download them.

The individual stages are available as `make data`, `make index`, and `make quant`. Index and quantification targets run their prerequisite stages. `make matrices` only regenerates the matrices from existing `quant/<sample>/quant.sf` files and `data/gtf/chr22.gtf`.

To specify the executable or thread count:

```bash
make all THREADS=4 SALMON=/path/to/salmon
```

The matrix script can also run directly:

```bash
python3 src/matrices.py --design design.csv --gtf data/gtf/chr22.gtf \
  --quant quant --output results
```

## Workflow and results

1. Build a Salmon index from the tutorial's transcript FASTA. `--keepDuplicates` retains distinct transcript IDs with identical sequences.
2. Quantify each **single-end** FASTQ with `salmon quant -l A -r ...`. Library orientation is inferred automatically; all six runs reported **SR**. The assumed fragment-length prior is mean **200 bp**, standard deviation **80 bp**. These are explicit modeling assumptions because these inputs do not provide paired-end insert lengths.
3. Read each `quant.sf`, join counts by transcript ID, and obtain transcript-to-gene relationships from the matching GTF. Version suffixes are retained.
4. Write both matrices and [tx2gene.tsv](results/tx2gene.tsv). Check that all samples contain the same transcripts, every transcript has a gene, and every sample's total is unchanged after aggregation.

| Sample | Reads processed | Reads mapped | Mapping rate | Sum of estimated counts |
| --- | ---: | ---: | ---: | ---: |
| HBR_1 | 118,571 | 40,779 | 34.39% | 40,778.994 |
| HBR_2 | 144,826 | 50,259 | 34.70% | 50,258.991 |
| HBR_3 | 129,786 | 44,536 | 34.31% | 44,535.999 |
| UHR_1 | 227,392 | 72,951 | 32.08% | 72,950.998 |
| UHR_2 | 162,373 | 47,780 | 29.43% | 47,779.996 |
| UHR_3 | 185,442 | 58,416 | 31.50% | 58,416.006 |

All six optimizations converged. Small differences between mapped read totals and sums of estimated counts reflect the precision of Salmon's reported values. Transcript and gene matrix sums match exactly at that reported precision. All 4,506 annotated transcripts were quantified. See [validation.json](results/validation.json), [quantification_summary.csv](results/quantification_summary.csv), and the retained per-sample `quant.sf`, `cmd_info.json`, and `aux_info/meta_info.json` files.

This is a **chr22 teaching reference**, without genomic decoys, rather than a whole-transcriptome analysis. The mapping percentages describe this restricted reference. These matrices alone do not establish differential expression or statistical significance.

## AI prompting and programming experience

This work was developed with AI assistance. Supplying the assignment requirements and the existing Week 11 files made it possible to reuse the correct six samples and reference files. The useful programming constraints were specific: use `NumReads`, preserve fractional counts, join by transcript ID rather than row position, and require every quantified transcript to map to a gene.

The AI-generated code was checked against actual Salmon output. A small regression fixture deliberately changes transcript row order between samples and uses fractional values with known gene sums. It also checks that an unrecognized transcript causes an error. The full run adds checks for duplicate IDs, invalid counts, sample transcript sets, and preservation of totals. This made verification more useful than relying on code that merely looked plausible.

## Challenges

- **Tutorial link:** On November 15, 2026, the assignment's [short link](https://tinyurl.com/3ztdpkf6) redirected to the handbook's computer-setup page. The older Week 11 tutorial URL did the same. I therefore used the existing course teaching dataset and Salmon's documented transcript-quantification workflow; I could not verify additional instructions behind the intended tutorial link.
- **Windows and Linux tools:** The files are on Windows, while Salmon runs in Ubuntu through WSL. Running Make from the Week 12 directory in WSL kept paths consistent.
- **Counts versus abundance:** Salmon reports both TPM and estimated read counts. Selecting `NumReads` and retaining decimal values avoided converting normalized abundances into a count matrix or losing fractional assignments.
- **Transcript-to-gene matching:** Versioned transcript identifiers must agree between the FASTA, quantification output, and GTF. The script stops on missing mappings rather than silently dropping counts.
- **Identical transcript sequences:** The index detected five duplicate-sequence transcripts. Retaining their IDs preserves the annotated transcript set, although identical sequences cannot be distinguished confidently from these reads alone.

## References

- [Salmon usage and single-end quantification](https://salmon.readthedocs.io/en/latest/salmon.html)
- [Salmon output columns and run metadata](https://salmon.readthedocs.io/en/latest/file_formats.html)
- [Course teaching dataset](https://data.biostarhandbook.com/data/rnaseq-tutorial-2026.tar.gz)
