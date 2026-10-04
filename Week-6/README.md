# Week 6: Evaluate Structural Variants

**Organism:** *Ebola virus* (ebola-1976)  
**Technique:** Visual inspection of paired-end read alignments using IGV  
**Objective:** Identify structural variants in 5 sequenced samples

---

## Sample 1: Minimal Structural Variation

### Sample 1 Overview
![Sample 1 Overview](Sample%201%20overview.png)

### Sample 1 - Colored by Read Strand
![Sample 1 by Read Strand](Sample%201%20overview%20by%20reda%20strands.png)

**Observations:** Uniform coverage histogram. Mostly gray reads with proper paired-end orientation. Scattered red and blue reads indicate SNPs. No large structural variants detected.

---

## Sample 2: Multiple Structural Variants

### Sample 2 Overview
![Sample 2 Overview](Sample%202%20overview.png)

### Sample 2 - Colored by Insert Size and Orientation
![Sample 2 by Insert Size](Sample%202%20overview%20by%20insert%20size%20and%20orientation.png)

**Observations:** Extensive multicolored reads throughout entire region (red, blue, green, purple, orange, yellow). Almost no gray reads. Colors represent vastly different insert sizes. Indicates complex structural variants with abnormal fragment lengths across the genome.

---

## Sample 3: Tandem Duplication

### Sample 3a Overview
![Sample 3a Overview](Sample%203a%20overview.png)

### Sample 3b Overview
![Sample 3b Overview](Sample%203b%20overview.png)

### Sample 3 - Colored by Pair Orientation
![Sample 3 by Pair Orientation](Sample%203%20overview%20%20by%20pair%20orientation.png)

### Sample 3 - Colored by Read Strand
![Sample 3 by Read Strand](Sample%203%20overview%20%20by%20read%20strand.png)

**Observations:** Coverage histogram shows prominent spike at 6-8 kb region. Three vertical columns of green/colored blocks. Double coverage in spike region indicates reads from two copies mapping to same location. **Duplication confirmed.**

---

## Sample 4: Inversion

### Sample 4 Overview
![Sample 4 Overview](Sample%204%20overview.png)

### Sample 4 - Viewed as Pairs
![Sample 4 as Pairs](Sample%204%20overview%20viewd%20as%20pairs.png)

### Sample 4 - Grouped by Read Strand
![Sample 4 by Read Strand](Sample%204%20grouped%20by%20read%20strand.png)

### Sample 4 - Colored by Insert Size
![Sample 4 by Insert Size](Sample%204%20overview%20viewd%20by%20insert%20size.png)

**Observations:** Dense cyan vertical line at 9-10 kb with connecting lines between inverted read pairs. Gray reads elsewhere show normal orientation. Inverted reads concentrate at single locus where sequence is flipped. **Inversion confirmed.**

---

## Sample 5: Complex Rearrangement

### Sample 5 Overview
![Sample 5 Overview](Sample%205%20overview.png)

### Sample 5 - Viewed as Pairs
![Sample 5 as Pairs](Sample%205%20overview%20viewd%20as%20pairs.png)

### Sample 5 - Viewed as Pair Orientation
![Sample 5 Pair Orientation](Sample%205%20overview%20viewd%20as%20pair%20orientation.png)

**Observations:** Perfectly parallel red horizontal lines (5-8 kb region) all oriented same direction (RL). Organized pattern but abnormal - reads all point same way. More complex than simple inversion. Likely **inverted tandem duplication or complex multi-segment rearrangement.**

---

## Whole Genome Comparisons

### All Samples Overview
![Whole Genome Overview](Whole%20genome%20overview.png)

### All Samples Comparison 1
![Whole Genome Comparison 1](Whole%20genome%20overview%201.png)

### All Samples Comparison 2
![Whole Genome Comparison 2](Whole%20genome%20overview%202.png)

---

## Comparative Summary

| Sample | Variant Type | Key Feature |
|--------|-------------|------------|
| **1** | None | Gray reads, normal pairs |
| **2** | Complex variants | Rainbow colors, abnormal insert sizes |
| **3** | Tandem duplication | Green columns, coverage peak |
| **4** | Inversion | Cyan line, inverted pairs |
| **5** | Complex rearrangement | Parallel red lines, organized abnormality |

**Conclusion:** Five distinct patterns of genomic variation demonstrated across samples, ranging from point mutations to large structural rearrangements.
