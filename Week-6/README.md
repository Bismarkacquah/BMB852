# Week 6: Evaluate Structural Variants

## Assignment Overview

In this assignment, you will visually evaluate existing alignments and identify structural variants using IGV (Integrative Genomics Viewer).

Five samples have been sequenced with paired-end reads, and a BAM file has been generated for each sample. Each sample may show a different type of variation (or no variation at all).

**Objective:** Visually inspect each BAM file and make your best guess at what kind of structural variation is present relative to the reference genome.

**Note:** No code writing is required for this assignment.

---

## Instructions

### Step 1: Set Up IGV

1. Download and install [IGV (Integrative Genomics Viewer)](http://software.broadinstitute.org/software/igv/)
2. Open IGV

### Step 2: Load the Reference Genome

In IGV:
1. Go to `Genomes → Load Genome from URL`
2. Enter the following URL:
   ```
   https://data.biostarhandbook.com/courses/2026-appbio/igv/fasta/ebola-1976.fa
   ```

### Step 3: Load Each Sample BAM File

For each sample, load the BAM file via `File → Load from URL` (leave the index file path empty):

- **Sample 1:** https://data.biostarhandbook.com/courses/2026-appbio/igv/bam/sample_1.bam
- **Sample 2:** https://data.biostarhandbook.com/courses/2026-appbio/igv/bam/sample_2.bam
- **Sample 3:** https://data.biostarhandbook.com/courses/2026-appbio/igv/bam/sample_3.bam
- **Sample 4:** https://data.biostarhandbook.com/courses/2026-appbio/igv/bam/sample_4.bam
- **Sample 5:** https://data.biostarhandbook.com/courses/2026-appbio/igv/bam/sample_5.bam

### Step 4: Analyze Each Sample

Use the following IGV visual settings to help identify variants:

- **View as pairs** — Shows paired-end reads together
- **Color by strand** — Distinguishes forward and reverse reads
- **Color by insert size** — Highlights abnormal fragment sizes (indicating deletions/inversions)
- **Group by pair orientation** — Groups reads with similar orientations

### Step 5: Document Your Findings

For each sample, provide a paragraph describing:
- The type of structural variant present (or "no variation")
- The evidence from the alignment visualization
- The genomic location (if applicable)

---

## Analysis Results

### Sample 1

**Structural Variant Description:**

[Your analysis here]

---

### Sample 2

**Structural Variant Description:**

[Your analysis here]

---

### Sample 3

**Structural Variant Description:**

[Your analysis here]

---

### Sample 4

**Structural Variant Description:**

[Your analysis here]

---

### Sample 5

**Structural Variant Description:**

[Your analysis here]

---

## Types of Structural Variants to Look For

- **Deletions:** Gaps in read coverage; missing genomic regions
- **Insertions:** Extra bases; reads extending beyond reference
- **Inversions:** Reads oriented in opposite directions; chaotic pair alignments
- **Duplications:** Doubled coverage; multiple reads mapping to same region
- **Translocations:** Reads mapping to different chromosomes (rare in single-chromosome Ebola)
- **No Variation:** Uniform coverage and consistent read orientation

---

## Submission

Once completed, commit and push this directory to GitHub. Submit the URL to your Week-6 directory.
