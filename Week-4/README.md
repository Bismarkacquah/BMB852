# Week 4: Obtain FASTQ data for the *Drosophila* Lamin experiment

## Objective

This assignment evaluates the experimental evidence available for the
*Drosophila melanogaster* Lamin gene and builds a reproducible short-read
quality-control workflow. The genomic context and Lamin annotation were
established in [Week 2](../Week-2/README.md).

The selected experiment is the ENA/SRA run **DRR303595**, from a study of
Lamin-bound regions in *D. melanogaster* muscle. It is a paired-end Illumina
NovaSeq 6000 run, so the workflow produces separate R1 and R2 FASTQ files.

## Evidence from ENA and SRA

The selected run is documented by the ENA run report:

- Run: `DRR303595`
- Study: `PRJDB11874`
- Experiment: `DRX293034`
- Sample: `SAMD00334508`
- Library: `Mef2_ PIGB13_ DamID-Lamin 2`
- Platform: Illumina NovaSeq 6000
- Strategy: `OTHER`
- Layout: paired-end
- Reported data: 111,781,950 read pairs and 33,534,585,000 bases

The run page reports that the complete experiment is approximately 10 GB.
Only a controlled subset is downloaded for this assignment.

To compare the broader public Lamin evidence, the ENA API query
`tax_tree(7227) AND description="lamin"` returned two paired-end Hi-C runs in
the related PRJNA432720 study (`SRR6667398` and `SRR6667399`) in addition to
the selected DamID run. This is an important distinction: a text search for
“lamin” finds both direct Lamin-binding experiments and experiments that use
Lamin as biological context, but they do not all measure the same molecular
signal.

The exact metadata commands are automated by the `metadata` Make target:

```bash
make metadata
```

## Reproducible workflow

The Makefile uses the SRA Toolkit to download only the first `N` spots from
the accession. The default is `N=100000`; this avoids downloading the complete
10-GB run while still producing enough reads for QC visualization.

From the `Week-4` directory:

```bash
# Install or activate an environment containing fastq-dump, FastQC, fastp, and curl.
make N=100000
```

The workflow performs these steps:

1. Downloads the first `N` paired spots from `DRR303595`.
2. Stores raw reads under `data/raw/`.
3. Runs FastQC on the raw reads and writes HTML/ZIP reports under
   `results/qc/raw/`.
4. Runs `fastp` adapter detection and quality trimming.
5. Stores trimmed reads under `data/trimmed/`.
6. Runs FastQC again and writes post-trimming reports under
   `results/qc/trimmed/`.
7. Saves a `fastp` HTML and JSON summary under `results/`.

The Makefile is generic for another paired-end SRA/ENA run:

```bash
make clean
make ACCESSION=SRR6667399 N=100000
```

The accession is the only dataset-specific input. The selected run must be
paired-end because the workflow expects both `_1` and `_2` FASTQ files.

To run individual stages:

```bash
make metadata
make download N=100000
make qc-raw
make trim
make qc-trimmed
```

To remove downloaded reads and generated reports:

```bash
make clean
```

## Quality-control interpretation

FastQC provides the visual before/after comparison required by the assignment:
per-base sequence quality, read-length distribution, GC content, duplicated
sequences, adapter content, and overrepresented sequences. `fastp` provides the
trimming step and a complementary HTML summary of reads retained and bases
removed.

The expected result is not that every warning disappears. Instead, the
post-trimming FastQC reports should be compared with the raw reports. Evidence
that trimming made a meaningful difference includes reduced adapter content,
fewer low-quality terminal bases, and improved per-base quality near the read
ends. The final conclusion should be based on the generated reports rather
than assumed in advance.

## Why this dataset is interesting

The selected run is unusually large for a teaching example: more than 111
million paired spots were deposited from one Illumina NovaSeq 6000 run. The
DamID-Lamin design also differs from ordinary RNA-seq. It is intended to
measure DNA regions associated with Lamin, so a large amount of sequencing
does not automatically imply uniform coverage of the Lamin gene itself. The
experimental strategy, biological selection, and paired-end layout are
therefore as important as the raw read count.

## Code used

The complete computational workflow is in
[Makefile](Makefile). The key commands are:

```bash
fastq-dump --split-files --gzip --maxSpotId 100000 --outdir data/raw DRR303595
fastqc --threads 2 --outdir results/qc/raw data/raw/lamin_DRR303595_R1.fastq.gz data/raw/lamin_DRR303595_R2.fastq.gz
fastp \
  --in1 data/raw/lamin_DRR303595_R1.fastq.gz \
  --in2 data/raw/lamin_DRR303595_R2.fastq.gz \
  --out1 data/trimmed/lamin_DRR303595_R1.trimmed.fastq.gz \
  --out2 data/trimmed/lamin_DRR303595_R2.trimmed.fastq.gz \
  --detect_adapter_for_pe \
  --html results/fastp_DRR303595.html \
  --json results/fastp_DRR303595.json
fastqc --threads 2 --outdir results/qc/trimmed data/trimmed/lamin_DRR303595_R1.trimmed.fastq.gz data/trimmed/lamin_DRR303595_R2.trimmed.fastq.gz
```

These commands are intentionally represented in the Makefile so the workflow
can be rerun without copying commands manually.

