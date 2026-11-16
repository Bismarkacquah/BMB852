# Week 12: Generate RNA-Seq count matrices

I used Salmon with the six HBR and UHR samples from Week 11 to generate two count matrices from the chr22 teaching dataset:

- [Transcript counts](results/transcript_counts.tsv): 4,506 transcripts across six samples.
- [Gene counts](results/gene_counts.tsv): 1,371 genes across six samples.

The transcript counts come from Salmon's `NumReads` column. The gene counts are the sum of the transcript counts for each gene, using the matching GTF annotation. Fractional counts are kept.

## How to run

Install Python 3.9 or newer, GNU Make, and Salmon. I used Ubuntu through WSL with Salmon 2.8.0. From this directory, run:

```bash
make all
```

This downloads the data, builds the Salmon index, quantifies the samples, and writes both matrices to `results/`. Sample names are in `src/design.csv`. The scripts are in `src/`: `workflow.py` runs the quantification, and `matrices.py` creates the matrices.

After quantification, the gene and transcript steps can be run separately:

```bash
make gene
make transcript
make compare
```

`make gene` sums transcript counts by gene ID. `make transcript` combines the Salmon counts by transcript ID. `make compare` adds gene names, checks the sums, and updates the examples below. `make matrices` rebuilds both numeric matrices together. `make download` downloads the inputs without running the analysis.

## Run summary

| Sample | Reads processed | Reads mapped | Mapping rate |
| --- | ---: | ---: | ---: |
| HBR_1 | 118,571 | 40,779 | 34.39% |
| HBR_2 | 144,826 | 50,259 | 34.70% |
| HBR_3 | 129,786 | 44,536 | 34.31% |
| UHR_1 | 227,392 | 72,951 | 32.08% |
| UHR_2 | 162,373 | 47,780 | 29.43% |
| UHR_3 | 185,442 | 58,416 | 31.50% |

All six runs converged and reported the library type as `SR`. These mapping rates are for the chr22 teaching reference.

The [run summary](results/quantification_summary.csv) is also saved as a CSV. Each sample folder in [results/metadata/quant/](results/metadata/quant/) contains `cmd_info.json` with the command settings and `aux_info/meta_info.json` with the run statistics. The Salmon version is saved in [software_versions.txt](results/metadata/software_versions.txt).

The [input checksums](results/metadata/input_checksums.json) record SHA-256 hashes for the transcript FASTA, GTF, and six FASTQ files. Running `make all` regenerates the checksums and run summary along with the matrices.

<!-- count-checks:start -->
## Checking the matrices

Both matrices have the same six sample columns. The transcript matrix has 4,506 rows, and the gene matrix has 1,371 rows. The table below shows how many have counts greater than zero in each sample.

| Sample | Nonzero transcripts | Nonzero genes | Transcript total | Gene total | Difference |
| --- | --- | --- | --- | --- | --- |
| HBR_1 | 1307 | 534 | 40778.994 | 40778.994 | 0.000 |
| HBR_2 | 1419 | 569 | 50258.991 | 50258.991 | 0.000 |
| HBR_3 | 1352 | 562 | 44535.999 | 44535.999 | 0.000 |
| UHR_1 | 1618 | 609 | 72950.998 | 72950.998 | 0.000 |
| UHR_2 | 1580 | 660 | 47779.996 | 47779.996 | 0.000 |
| UHR_3 | 1540 | 600 | 58416.006 | 58416.006 | 0.000 |

The totals match for every sample. I also compared each gene count with the sum of its transcripts. All differences were zero across all genes and samples, as expected from this method. This checks the aggregation step rather than agreement between independent counting tools. The full checks are in [count_summary.tsv](results/count_summary.tsv) and [gene_transcript_comparison.tsv](results/gene_transcript_comparison.tsv).

### Gene names and examples

I added gene names from the same GTF used for counting, so this step does not need an online annotation service. The original numeric matrices are unchanged. The named versions are [gene_counts_named.tsv](results/gene_counts_named.tsv) and [transcript_counts_named.tsv](results/transcript_counts_named.tsv). Gene IDs are used for grouping because names may be missing or shared.

| Gene | Gene ID | HBR_1 | HBR_2 | HBR_3 | UHR_1 | UHR_2 | UHR_3 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OR11H1 | ENSG00000130538.4 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| RPL3 | ENSG00000100316.15 | 653.999 | 754.001 | 717.001 | 4009.000 | 2392.999 | 3036.000 |
| SYNGR1 | ENSG00000100321.14 | 757.999 | 992.001 | 857.000 | 51.000 | 46.000 | 40.999 |
| MPPED1 | ENSG00000186732.13 | 121.000 | 150.000 | 135.000 | 1.000 | 2.000 | 2.000 |

OR11H1 has zero counts in every sample. RPL3 has counts in all six samples. SYNGR1 and MPPED1 have higher raw counts in HBR than UHR. For SYNGR1, ENST00000328933.9 contributes most of the HBR gene count, consistent with the transcript discussed in Week 11.

These are raw estimated counts, so library-size differences affect comparisons between samples. They can be checked alongside the Week 11 coverage observations, but they are not a test of differential expression.

### Adding transcripts into a gene count

Here are all the SYNGR1 transcripts. Adding each sample column gives the gene total in the last row. Values are shown at their original precision.

| Transcript | HBR_1 | HBR_2 | HBR_3 | UHR_1 | UHR_2 | UHR_3 |
| --- | --- | --- | --- | --- | --- | --- |
| ENST00000216155.11 | 1.773 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ENST00000318801.8 | 0.000 | 0.000 | 0.000 | 16.699 | 5.073 | 0.000 |
| ENST00000328933.9 | 726.922 | 951.888 | 816.552 | 29.744 | 25.490 | 23.260 |
| ENST00000381535.4 | 12.346 | 12.243 | 13.994 | 0.000 | 0.000 | 7.702 |
| ENST00000406293.7 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ENST00000415332.1 | 0.000 | 0.000 | 0.000 | 0.000 | 12.039 | 7.815 |
| ENST00000489206.1 | 16.958 | 27.870 | 26.454 | 4.557 | 3.398 | 2.222 |
| SYNGR1 gene total | 757.999 | 992.001 | 857.000 | 51.000 | 46.000 | 40.999 |
<!-- count-checks:end -->

## Working with AI

I used AI to help write the Makefile and Python scripts, then asked it to adapt the layout and example checks from Victoria's work to my samples. Specifying `NumReads`, keeping decimal values, and matching transcript IDs helped keep the code focused on the assignment. The gene names came from the local GTF, and the results were checked against my own Salmon output.

## Challenges

The assignment link redirected to the handbook's computer-setup page, so I used the existing course dataset and Salmon's transcript-quantification workflow. I could not verify the intended tutorial instructions.

I also had to keep the Windows file paths consistent with WSL and make sure the transcript IDs matched the GTF. It was important to use counts rather than TPM and avoid rounding fractional values before adding them by gene.

The organization and example checks were adapted from [Victoria's Week 12 work](https://github.com/VAbramRepo/appbio-2026/tree/main/week12). Her gene matrix uses featureCounts; my gene matrix sums Salmon transcript estimates as requested in this assignment.
