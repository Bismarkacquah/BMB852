# Week 2 Assignment - Visualizing Genomic Data

### Setting Yourself Up

Start off by opening your coding & coding assistant software of choice. I am using VS Code for this assignment. 

Next, using the skills learned from week 1, move into your work directory where you are keeping your weekly assignments. 

Create a new directory for week 2:

```bash
mkdir week2
```

Within your new week2 directory, you can make your new README.md file as well as another directory/folder we will call igv

```bash
# make new Read Me file
touch README.md

# make igv folder
mkdir igv
```

Finally, activate your bioinformatics environment:

```bash
bioinfo
```
Now we can begin!

## Obtaining Genomic Information

We are going to create a Makefile for downloading the FASTA and GFF files for a set of genomic data. Before we do this, however, we must select what organism we want to obtain the genomic data of!

After you've found a link that contains downloads for the genomic data of the organism you chose, a Makefile can be created. 

I chose [Zygosaccharomyces bailii](https://jun2026-fungi.ensembl.org/Zygosaccharomyces_bailii_isa1307_gca_000530735/Info/Index), which is [a yeast found in kombucha cultures](https://pmc.ncbi.nlm.nih.gov/articles/PMC7027524/#jfds14992-sec-0120)

You can then use your coding assistant to develop a Makefile to download the FASTA and GFF files and organize them into your igv directory. My [Makefile](https://github.com/lmm683/BMMB-852-lmm/blob/main/week2/igv/Makefile), when run while in the igv directory, creates two new directories for the FASTA and GFF files respectively, downloads each of the files, ensures they are unzipped, renames them to z.bailii.(file type), and moves them into their corresponding directories. 

The Makefile can be used by running the following commands in your terminal:

```bash
# Download & organize both FASTA and GFF files
make

# Download & organize just the FASTA file
make fasta

# Download & organize just the GFF file
make gff

# Remove the FASTA and GFF files & directories
make clean
```

## Visualizing the Genome 

To look at the genomic data you have now downloaded, ensure that you have igv installed. I manually loaded the FASTA and GFF files into my igv browser. You can do this by first opening the FASTA file from the Genomes Tab -> Load Genome from FIle. You can then open the GFF file from the File tab -> Load from File. Your browser should then look like this:

<img width="2268" height="946" alt="image" src="https://github.com/user-attachments/assets/5f7648ab-a80b-4643-9d08-fb6b45cf1555" />

The data displayed on the two available tracks is the raw sequence of base pairs (FASTA file data)
and the amino acids that the codons likely code for (GFF3 file data).

The size of the FASTA file is 21,007 KB (kilobytes), which is very roughly around 21,007,000 bp (base pairs). I am specifically observing the ZBAI_A_scaffold_001 chromosome, which is 41kb (kilobases)

You can find the number of annotations on the GFF file from the following command:

```bash
awk '!/^#/ && NF>=3 {count[$3]++; total++} END {for (k in count) print k, count[k]; print "TOTAL", total}' /home/laurenmags/work/week2/igv/gff/Z.bailii.gff3 | sort -k2,2nr
```
In your case, the file path will look different and reflect your personal file path. 

This command prints a list of all the annotation details:

```bash
TOTAL 43090
exon 10757
CDS 10240
gene 9925
mRNA 9925
biological_region 1055
ncRNA_gene 517
tRNA 514
supercontig 154
rRNA 3
```

Looking at the list of scaffolds, there seems to be 85 chromosomes in this genome. Some chromosomes only have side recorded and others have both. 

This genomic build seems somewhat refined. The genes are all marked, but the number of chromosomes is not super clear.

Using the browser, I can estimate that the genes (shown by the GFF file) are roughly 200-2,000 bp apart.

When you zoom in, you can get a better look at the sequence:

<img width="2242" height="756" alt="image" src="https://github.com/user-attachments/assets/d1739257-6933-4daa-976a-27e8763adc68" />

I have switched the sequence translation to 'mitochondrial yeast', since Z. bailii is a yeast. 

Notice how in the screenshot, I have the sequence expanded to have the three different codon reading frames possible displayed. If we pick one coordinate (base pair) to look at the potential codons it could be in, we can easily see each amino acid it might code for. For example, if we look at coordinate 24,509 of this first chromosome, an A-T base pair, we can see that it might be a part of a codon for I, T, or Y on this side of the chromosome. If we flip the strand, the other side of the base pair could be a part of the codon for K, N, or M.

Flipped sequence:

<img width="2246" height="796" alt="image" src="https://github.com/user-attachments/assets/068c57cf-d25b-4583-a714-810fd56de8e3" />

The gene that contains my selected coordinate is a protein encoding gene that likely is subunit 16 of a protein that  mediates RNA polymerase II transcription:

<img width="537" height="149" alt="image" src="https://github.com/user-attachments/assets/d37ca2f1-956f-4705-b2f2-447466380711" />

The colors of the genes are customizable by their strand orientation:

<img width="2256" height="650" alt="image" src="https://github.com/user-attachments/assets/ef61c3ac-6bb9-4769-a756-7b351d7e8d1e" />

Teal is positive orientation while pink is negative orientation.

You can also expand the view of the genes to get a better look at each of them:

<img width="2254" height="1014" alt="image" src="https://github.com/user-attachments/assets/72ff2670-9503-453e-b854-79cf61f72ca2" />



