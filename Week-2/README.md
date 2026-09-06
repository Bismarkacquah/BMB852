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

The generated Lamin-specific files are available in this project:

- [Lamin GFF3](lamin_annotation.gff3)
- [Lamin GTF](lamin_annotation.gtf)
- [IGV Lamin annotation](lamin_igv_annotation.png)
- [Lamin chromosome 2 IGV screenshot](lamin_chromosome2_igv.png)
- [Lamin chromosome 2 strand view](lamin_chromosome2_strand.png)
- [Lamin chromosome 2 expanded strand view](lamin_chromosome2_strand_expanded.png)
- [Lamin gene-density IGV view](Lamin_gene_density.png)

The FASTA contains 1,870 sequence records with a total length of 143,726,002 bp.

IGV cannot load the compressed `.fna.gz` directly in this setup. Create the
plain FASTA that IGV needs with:

```bash
python -c "import gzip, shutil; shutil.copyfileobj(gzip.open('GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.fna.gz','rb'), open('GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.fna','wb'))"
```

## Reproduce the download and annotation

From this directory, run:

```bash
make download
make annotate
```

The annotation step uses `annotate_lamin.py` to extract records whose annotation
identifies the gene as `Lam`. It creates:

- `lamin_annotation.gff3`
- `lamin_annotation.gtf`

The script requires Python 3 and reads the compressed annotation files directly.
On systems without `make`, run the equivalent commands:

```bash
python annotate_lamin.py GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.gff.gz lamin_annotation.gff3
python annotate_lamin.py GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.gtf.gz lamin_annotation.gtf
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

To inspect the gene in IGV:

1. Load `GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.fna` as the genome.
2. Load `lamin_annotation.gff3` as an annotation track.
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

4. **How complete is this genomic build?**

	This is a high-quality reference assembly with broad gene and transcript
	annotation, but it is not represented only by the four chromosome names:
	unlocalized, unplaced, and mitochondrial sequences are included as well.

### Visualize the Lamin locus

1. **How tightly packed are the genes?**

	The Lamin locus is very gene-dense. `Hel25E` ends 165 bp before `Lam`, and
	`Oscillin` begins 443 bp after it. Additional nearby genes include `CG14015`,
	`tomb`, `Cap-D3`, and `CG14014`, which are visible in the wider IGV view
	(`NT_033779.5:5,400,000-5,700,000`, Figure 6).

2. **Which coordinate was inspected?**

	`NT_033779.5:5,542,480-5,546,642`

3. **What are the six possible reading frames?**

	Any double-stranded DNA interval has six possible reading frames: +1, +2,
	+3 on the forward strand and -1, -2, -3 on the reverse strand. The Lam
	annotation is on the forward strand.

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
inspection in IGV. The assembly, source files, gene coordinates, and generated
outputs are recorded so the analysis can be reproduced.
