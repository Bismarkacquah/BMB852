# Week 2: Obtain and Visualize Genomic Data

## Genome Selected

**Organism:** Escherichia coli K-12

**Assembly:** GCF_000005845.2_ASM584v2

### Files Used

- `GCF_000005845.2_ASM584v2_genomic.fna`
- `GCF_000005845.2_ASM584v2_genomic.gff`

---

## Using the Makefile

To download the genome sequence and annotation files, run:

```bash
make download
```

This command downloads the FASTA genome sequence and GFF annotation file from NCBI.

---

## Obtain Genomic Data Questions

### 1. How large is the genome?

The genome is approximately **4,641,652 base pairs (4.64 Mb)** in length.

### 2. How many chromosomes does it have?

The genome contains **one chromosome**.

### 3. How many annotations are in the annotation file?

The annotation file contains thousands of annotated genomic features, including genes, coding sequences (CDS), regulatory elements, and other genomic annotations.

### 4. How complete is this genomic build?

This assembly appears highly complete because it is represented as a single chromosome with extensive annotation coverage and well-defined genomic features.

---

## Visualize a Genome Questions

### 1. How tightly packed are the genes?

The genes appear densely packed with relatively short intergenic regions, which is typical of bacterial genomes.

### 2. Pick a coordinate on the chromosome and visually inspect the surrounding sequence region.

**Coordinate inspected:**

`NC_000913.3:3,657,996-3,667,113`

### 3. Describe all six reading frames that the coordinate could be part of.

The sequence can potentially be translated in six reading frames:

- +1
- +2
- +3
- -1
- -2
- -3

The positive reading frames are located on the forward strand, while the negative reading frames are located on the reverse strand.

### 4. Identify the type of feature displayed as a data track.

The displayed data track contains **gene and coding sequence (CDS) annotations** derived from the GFF annotation file.

### 5. Color features by their strand orientation.

Features are displayed according to strand orientation, allowing forward-strand and reverse-strand genomic features to be distinguished visually.

---

## IGV Visualization

The FASTA and GFF files were successfully loaded into IGV for genome visualization.

Annotated genes observed during inspection included:

- gadW
- gadY
- gadX
- gadA

The annotation track displayed genomic features and their positions along the chromosome.

---

## Summary

This exercise demonstrated how to:

1. Download genomic sequence data from NCBI.
2. Obtain genome annotation files.
3. Load genomic data into IGV.
4. Explore genomic coordinates and gene annotations.
5. Visualize genomic features and strand orientation.
6. Interpret genome structure and annotation information.

---

## Reproducibility

The analysis can be reproduced by downloading the FASTA and GFF files using the Makefile and loading the files into IGV for visualization and inspection.