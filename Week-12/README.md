# Week 12: Generate RNA-Seq count matrices

For this assignment, I used Salmon to estimate transcript counts for the same six samples from Week 11: three Human Brain Reference (HBR) samples and three Universal Human Reference (UHR) samples. I used the chr22 teaching dataset.

The two count matrices are:

- [Transcript counts](results/transcript_counts.tsv): 4,506 transcripts across six samples.
- [Gene counts](results/gene_counts.tsv): 1,371 genes across six samples.

The transcript matrix uses the `NumReads` column from each Salmon `quant.sf` file. To make the gene matrix, the script uses `chr22.gtf` to find which gene each transcript belongs to and adds their counts together. I kept the decimal values because Salmon estimates how reads are shared between transcripts. These are estimated counts, not TPM values.

## How to run

The workflow needs Python 3.9 or newer, GNU Make, and Salmon. I ran it in Ubuntu through WSL using Salmon 2.8.0. Python does not need any extra packages.

From the assignment directory, run:

```bash
make all
make test
```

`make all` downloads the tutorial data, builds the Salmon index, quantifies all six samples, and saves both count matrices in `results/`. The download is about 71 MB. `make test` checks that the matrix script handles fractional counts and transcripts listed in different orders.

If the Week 11 data are already downloaded, they can be reused:

```bash
# GitHub folder names
make all SOURCE=../Week-11

# Local folder names on my computer
make all SOURCE=../Week11
```

The source folder needs the transcript FASTA in `fasta/`, the annotation in `gtf/`, and all six read files in `fastq/`. To change the thread count or Salmon location, use `make all THREADS=4 SALMON=/path/to/salmon`.

To rebuild just the matrices from the existing Salmon results:

```bash
make matrices
```

The scripts are in `src/`. `workflow.py` prepares the data and runs Salmon. `matrices.py` combines the transcript counts and sums them by gene. The sample names and groups are listed in [design.csv](design.csv).

## Results

All six Salmon runs finished and converged. The inferred library type was `SR` for every sample. Since the reads are single-end, I used an assumed fragment-length mean of 200 bp and standard deviation of 80 bp. I also kept separate transcript IDs when their sequences were identical.

| Sample | Reads processed | Reads mapped | Mapping rate |
| --- | ---: | ---: | ---: |
| HBR_1 | 118,571 | 40,779 | 34.39% |
| HBR_2 | 144,826 | 50,259 | 34.70% |
| HBR_3 | 129,786 | 44,536 | 34.31% |
| UHR_1 | 227,392 | 72,951 | 32.08% |
| UHR_2 | 162,373 | 47,780 | 29.43% |
| UHR_3 | 185,442 | 58,416 | 31.50% |

Every transcript had a matching gene in the annotation. For each sample, the total count was the same before and after combining transcripts into genes. The checks are saved in [validation.json](results/validation.json), and the run summary is in [quantification_summary.csv](results/quantification_summary.csv). The original Salmon counts are kept in `quant/`.

These results cover chr22 only. The index does not include genomic decoys, and this is not a whole-transcriptome analysis. The count matrices do not by themselves show which genes are significantly different between HBR and UHR.

## Working with AI

I used AI to help write the Makefile and Python scripts. Giving it the assignment instructions and the Week 11 file layout helped keep the workflow focused on the six samples I already had. The main requirements were to use `NumReads`, keep fractional counts, and match transcripts by their IDs.

The code was checked against the Salmon output rather than accepted without testing. One test changed the order of transcripts between samples and used counts with known gene totals. The final checks also compared every transcript count with its original `quant.sf` value and every gene count with the sum of its transcripts.

## Challenges

The assignment link redirected to the handbook's computer-setup page, so I could not check the intended tutorial instructions. I used the existing course dataset and Salmon's transcript-quantification workflow instead.

Another issue was keeping the Windows files and WSL commands pointed at the same directory. Running Make from the assignment folder in WSL kept the paths consistent.

It was also necessary to separate counts from TPM and keep the transcript IDs consistent with the GTF. The script stops if a transcript has no matching gene. The index found five transcripts with duplicate sequences; their IDs were retained, but the reads cannot reliably distinguish identical sequences.
