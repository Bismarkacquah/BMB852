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

This downloads the data, builds the Salmon index, quantifies the samples, and writes both matrices to `results/`. Sample names are in `design.csv`. The scripts are in `src/`: `workflow.py` runs the quantification, and `matrices.py` creates the matrices.

To rebuild only the matrices after quantification, run:

```bash
make matrices
```

## Working with AI

I used AI to help write the Makefile and Python scripts. Providing the assignment instructions and Week 11 file layout helped it use the correct samples. Being specific about using `NumReads`, keeping decimal values, and matching transcript IDs made the code more useful. The counts were checked against the Salmon output, and the totals matched after combining transcripts into genes.

## Challenges

The assignment link redirected to the handbook's computer-setup page, so I used the existing course dataset and Salmon's transcript-quantification workflow. I could not verify the intended tutorial instructions.

I also had to keep the Windows file paths consistent with WSL and make sure the transcript IDs matched the GTF. It was important to use counts rather than TPM and avoid rounding fractional values before adding them by gene.
