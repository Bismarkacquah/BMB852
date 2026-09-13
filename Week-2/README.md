# Week 2: Annotate the Drosophila Lamin Gene

## Genome selected

- **Organism:** *Drosophila melanogaster* (fruit fly)
- **Assembly:** `GCF_000001215.4_Release_6_plus_ISO1_MT`
- **Repository:** [NCBI Assembly GCF_000001215.4](https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000001215.4/)
- **Annotation source:** FlyBase Release 6.54, distributed by NCBI RefSeq

The target gene is **Lamin**, whose official Drosophila symbol is `Lam` and whose
NCBI locus tag is `Dmel_CG6944`.

## Downloaded files

The `download` target retrieves these compressed files from NCBI. Each filename
below is also a direct one-click download link:

- [Genome FASTA](https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/215/GCF_000001215.4_Release_6_plus_ISO1_MT/GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.fna.gz)
- [GFF3 annotation](https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/215/GCF_000001215.4_Release_6_plus_ISO1_MT/GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.gff.gz)
- [GTF annotation](https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/215/GCF_000001215.4_Release_6_plus_ISO1_MT/GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.gtf.gz)

The Lamin-specific files created for this project are available here:

- [Lamin GFF3](data/lamin_annotation.gff3)
- [Lamin GTF](data/lamin_annotation.gtf)
- [IGV Lamin annotation](lamin_igv_annotation.png)
- [Lamin chromosome 2 IGV screenshot](lamin_chromosome2_igv.png)
- [Lamin chromosome 2 strand view](lamin_chromosome2_strand.png)
- [Lamin chromosome 2 expanded strand view](lamin_chromosome2_strand_expanded.png)
- [Lamin gene-density IGV view](Lamin_gene_density.png)

The FASTA contains 1,870 sequence records with a total length of 143,726,002 bp.

IGV cannot load the compressed `.fna.gz` directly in this setup. The Makefile
creates the plain FASTA in `data/` with `gunzip`. To reproduce that step by
itself, run:

```bash
gunzip -kf data/GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.fna.gz
```

## Reproduce the download and annotation

From the `Week-2` directory, run:

```bash
make download
make annotate
make count
```

The Makefile creates the `data/` directory, downloads the compressed genome and
annotation files, creates the plain FASTA for IGV, and extracts records whose
annotation identifies the gene as `Lam`. It creates:

- `data/lamin_annotation.gff3`
- `data/lamin_annotation.gtf`

The annotation extraction is performed directly with `zcat` and `awk` inside
the Makefile. No separate Python script is required. To run the complete
workflow with one command, use:

```bash
make
```

To remove the downloaded and extracted data and reproduce the workflow from
scratch, use:

```bash
make clean
make
```

## Lamin annotation result

The Lamin gene is annotated on the forward strand of contig `NT_033779.5`:

```text
NT_033779.5:5,542,480-5,546,642
```

The extracted annotation includes the `gene`, transcript, exon, CDS,
start-codon, and stop-codon records for the annotated Lamin isoforms. The GTF
identifies the gene with `gene_id "Dmel_CG6944"` and `gene "Lam"`.

## IGV visualization

For a clean presentation of all screenshots, see the [complete IGV screenshot
file](screenshots.md), or view the [single combined screenshot image](IGV_screenshots_contact_sheet.png).

To inspect the gene in IGV:

1. Load `data/GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.fna` as the genome.
2. Load `data/lamin_annotation.gff3` as an annotation track.
3. Navigate to `NT_033779.5:5,542,480-5,546,642`.

The annotation track shows the Lam gene models and their transcript structures.

![IGV Lamin annotation](lamin_igv_annotation.png)

**Figure 1.** Detailed IGV view of the *Drosophila melanogaster* Lamin (`Lam`)
gene showing its transcript isoforms and exon structures.

![IGV Lamin genome browsing](lamin_genome_browsing.png)

**Figure 2.** Wider IGV view of the Lamin locus showing surrounding annotated
genes, including `DIP-eta`, `CG7236`, `CG9171`, `rau`, `bchs`, `chic`, and `Pfas`.

![Lamin chromosome 2 IGV annotation](lamin_chromosome2_igv.png)

**Figure 3.** Additional IGV view of the Lamin gene on chromosome 2 at
`NT_033779.5:5,542,480-5,546,642`.

![Lamin chromosome 2 strand view](lamin_chromosome2_strand.png)

**Figure 4.** Lamin chromosome 2 view with strand coloring enabled. Forward-
and reverse-strand annotations can be distinguished by their directions and
colors.

![Lamin chromosome 2 expanded strand view](lamin_chromosome2_strand_expanded.png)

**Figure 5.** Expanded IGV view of the Lamin chromosome 2 annotation track,
showing separate transcript and feature rows.

![Lamin gene-density IGV view](Lamin_gene_density.png)

**Figure 6.** Wide IGV view of the 300 kb Lamin neighborhood, showing the
closely spaced annotated genes and transcript models used for the gene-density
answer.

## Questions and answers

### Obtain genomic data

The commands used to answer this section were:

```bash
# Genome size in base pairs
awk '/^>/ { next } { bp += length($0) } END { print bp }' data/GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.fna

# Number of FASTA sequence records
grep -c '^>' data/GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.fna

# Feature counts in the complete GFF3 annotation
zcat data/GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.gff.gz | \
	awk '!/^#/ && NF >= 3 { count[$3]++; total++ } END { for (k in count) print k, count[k]; print "TOTAL", total }' | \
	sort -k2,2nr
```

These commands produce the values reported below: 143,726,002 bp, 1,870
FASTA records, and 414,876 non-comment GFF3 records.

The complete command record is also available through the Makefile:

```bash
make download
make annotate
make count
```

1. **How large is the genome?**

	The downloaded FASTA contains 143,726,002 bp across 1,870 sequence records.

2. **How many chromosomes does it have?**

	*D. melanogaster* has four chromosome pairs: X, 2, 3, and 4. The assembly
	also contains mitochondrial DNA and many unlocalized or unplaced scaffolds,
	which is why the FASTA has 1,870 sequence records rather than only four
	chromosome sequences.

3. **How many annotations are in the annotation file?**

	The downloaded GFF3 contains 414,876 non-comment records, including 17,537
	gene records, 30,802 mRNA records, and 190,710 exon records. The Lamin-only
	files contain 32 GFF3 records and 40 GTF records.

The annotation counts for the full downloaded annotation file were obtained
with this command:

```bash
zcat data/GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.gff.gz | \
  awk '!/^#/ && NF >= 3 { count[$3]++; total++ } END { for (k in count) print k, count[k]; print "TOTAL", total }' | \
  sort -k2,2nr
```

The command reports `TOTAL 414876`. The largest feature categories are:

```text
exon 190710
CDS 163319
mRNA 30802
gene 17537
```

The Lamin-only annotation counts were obtained separately with:

```bash
grep -v '^#' data/lamin_annotation.gff3 | awk 'NF { count[$3]++; total++ } END { for (k in count) print k, count[k]; print "TOTAL", total }' | sort -k2,2nr
grep -v '^#' data/lamin_annotation.gtf | awk 'NF { count[$3]++; total++ } END { for (k in count) print k, count[k]; print "TOTAL", total }' | sort -k2,2nr
```

For the extracted files, these commands report 32 GFF3 records and 40 GTF
records. The counts include every non-comment feature row, including repeated
records for different Lamin transcripts.

4. **How complete is this genomic build?**

	This is a high-quality reference assembly with broad gene and transcript
	annotation, but it is not represented only by the four chromosome names:
	unlocalized, unplaced, and mitochondrial sequences are included as well.

The chromosome and scaffold names can be listed directly from the FASTA with:

```bash
awk '/^>/ { sub(/^>/, ""); print $1 }' data/GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.fna
```

The four main chromosome names can be selected with:

```bash
awk '/^>/{ sub(/^>/, ""); print $1 }' data/GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.fna | \
	grep -E '^(2L|2R|3L|3R|4|X|mitochondrion_genome)$'
```

### Visualize the Lamin locus

1. **How tightly packed are the genes?**

	The Lamin locus is very gene-dense. `Hel25E` ends 165 bp before `Lam`, and
	`Oscillin` begins 443 bp after it. Additional nearby genes include `CG14015`,
	`tomb`, `Cap-D3`, and `CG14014`, which are visible in the wider IGV view
	(`NT_033779.5:5,400,000-5,700,000`, Figure 6).

2. **Which coordinate was inspected?**

	`NT_033779.5:5,542,480-5,546,642`

The Lam records at that coordinate can be checked with:

```bash
awk -F '\t' '$1 == "NT_033779.5" && $4 <= 5546642 && $5 >= 5542480 { print }' data/lamin_annotation.gff3
```

The gene models in the surrounding 300 kb window can be listed with:

```bash
awk -F '\t' '$1 == "NT_033779.5" && $3 == "gene" && $4 <= 5700000 && $5 >= 5400000 { print $1, $4, $5, $7, $9 }' data/lamin_annotation.gff3 | \
	sort -k2,2n
```

3. **What are the six possible reading frames?**

	Any double-stranded DNA interval has six possible reading frames:

| Strand | Frames |
| --- | --- |
| Forward (+) | +1, +2, +3 |
| Reverse (-) | -1, -2, -3 |

In IGV, I inspected `NT_033779.5:5,542,480-5,546,642`, expanded the sequence
track, and enabled translation display. The three forward frames are read from
left to right on the reference strand. The three reverse frames are the
reverse-complement translations. The six frame rows should be read directly
from the expanded data track rather than inferred from the gene model alone.
Lam is annotated on the forward strand, so the annotated coding frame is among
the `+1`, `+2`, and `+3` rows.

To document the six-frame result, capture a screenshot after expanding the data
track and showing all six translation rows. The existing strand and
expanded-locus figures document the annotation context; the six-frame
screenshot should be added beside them when the IGV view is available.

There is no terminal command for this answer. The six-frame result comes from
the IGV interface: load the plain FASTA, navigate to the Lam coordinate,
expand the sequence data track, and enable translation display. The screenshot
is the reproducible evidence for this visual answer.

4. **What feature types are displayed?**

	The Lamin track contains gene, transcript, exon, CDS, start-codon, and
	stop-codon features for multiple Lam isoforms.

5. **How can features be distinguished by strand?**

	In IGV, enable the annotation track's strand coloring option. Forward- and
	reverse-strand features are then shown with different colors; Lam should
	appear as a forward-strand model at the coordinate above.

## Summary

This workflow downloads a Drosophila reference genome and both GFF3 and GTF
annotation formats from NCBI, then extracts the Lamin gene annotation for
inspection in IGV. The assembly, source files, gene coordinates, and created
outputs are recorded so the analysis can be reproduced.
