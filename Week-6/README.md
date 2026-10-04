# Structural Variant Analysis Results

## Sample 1: Minimal Structural Variation (SNPs and Small Indels)

Sample 1 displays a relatively normal alignment pattern with minimal structural variation. The coverage histogram shows uniform read depth across the first 15.5 kb of the Ebola genome (NC_002549.1:1-15,573). The majority of reads are gray, indicating normal paired-end alignments with proper orientation. Scattered red and blue colored reads throughout the region suggest the presence of single nucleotide polymorphisms (SNPs) and small insertions/deletions, but no large-scale structural variants are evident. The consistent read orientation and coverage pattern indicate that this sample contains primarily point mutations rather than significant structural rearrangements relative to the reference genome.

---

## Sample 2: Multiple Structural Variants with Abnormal Insert Sizes

Sample 2 exhibits extensive coloration across the entire alignment (NC_002549.1:1-18,959), with almost no gray reads visible. The reads are colored by insert size, revealing massive variation in fragment lengths throughout the region. Multiple colored blocks (blue, green, red, purple, orange, yellow) indicate reads with dramatically different insert sizes than expected. This extensive coloration pattern suggests the presence of **multiple tandem duplications and/or complex rearrangements** throughout the sequenced region. The high density of abnormally-sized read pairs indicates that large portions of this sample show significant structural variation, likely representing repeated regions or inverted sequences where reads cannot properly align with their expected insert sizes.

---

## Sample 3: Tandem Duplication

Sample 3 (NC_002549.1:1,509-17,081) shows clear evidence of **duplication**. The coverage histogram displays a prominent spike in the middle region (approximately 6-8 kb), indicating doubled read coverage in this area compared to flanking regions. The colored reads, primarily displayed in green and blue when grouped by pair orientation, highlight the complex read arrangements characteristic of duplicated sequences. The elevated coverage peak at this locus is the hallmark of a **tandem duplication** where a segment of the genome has been copied adjacent to itself, resulting in reads from both copies mapping to overlapping positions on the reference genome.

---

## Sample 4: Inversion

Sample 4 (NC_002549.1:1-18,959) displays a distinctive **inversion** pattern. The most striking feature is the dense vertical clustering of colored reads (predominantly blue and cyan) concentrated in the 9-10 kb region, while the remainder of the alignment shows mostly gray reads. This tight vertical clustering occurs when read pairs have inverted orientation relative to the expected direction. The concentrated band of abnormally-oriented reads indicates a **localized genomic inversion** where a chromosomal segment has been flipped in orientation. The boundary between the colored cluster and surrounding gray reads marks the approximate location of the inversion breakpoints.

---

## Sample 5: Complex Structural Rearrangement (Inversion or Translocation)

Sample 5 (NC_002549.1:1-18,959) shows a **complex structural rearrangement** with a dense cluster of colored reads (red, green, and blue) concentrated in the 5-8 kb region. Unlike Sample 4's tightly organized vertical band, Sample 5's cluster appears more scattered and chaotic, suggesting a more complex rearrangement. The mix of red (indicating one strand orientation) and green/blue (indicating alternative orientations) throughout the cluster indicates reads with multiple conflicting alignments. This pattern is characteristic of either a **complex inversion** with internal repeats, or possibly a more intricate rearrangement involving **segments rearranged in multiple orientations**. The abnormal pair orientations and spacing throughout this region prevent proper alignment and produce the characteristic chaotic coloration pattern.

---

## Summary of Findings

- **Sample 1:** No structural variants (SNPs/small indels only)
- **Sample 2:** Multiple structural variants with abnormal insert sizes (complex duplications)
- **Sample 3:** Tandem duplication
- **Sample 4:** Inversion
- **Sample 5:** Complex inversion or multi-segment rearrangement

The five samples demonstrate a comprehensive range of genomic variations found in populations, from point mutations to large-scale structural rearrangements.
