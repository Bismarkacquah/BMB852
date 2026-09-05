\# Week 2: Obtain and Visualize Genomic Data



\## Genome Selected



\*\*Organism:\*\* Escherichia coli K-12



\*\*Assembly:\*\* GCF\_000005845.2\_ASM584v2



\### Files Used



\- GCF\_000005845.2\_ASM584v2\_genomic.fna

\- GCF\_000005845.2\_ASM584v2\_genomic.gff



\## Using the Makefile



Run the following command:



make download



This command downloads the FASTA genome sequence and GFF annotation file from NCBI.



\## Obtain Genomic Data Questions



\### How large is the genome?



The genome is approximately 4,641,652 base pairs (4.64 Mb) in length.



\### How many chromosomes does it have?



The genome contains one chromosome.



\### How many annotations are in the annotation file?



The annotation file contains thousands of annotated genomic features, including genes, coding sequences (CDS), regulatory regions, and other genomic elements.



\### How complete is this genomic build?



This assembly appears highly complete because the genome is represented as a single chromosome with extensive annotation coverage and well-defined genomic features.



\## Visualize a Genome Questions



\### How tightly packed are the genes in this genome?



The genes appear to be densely packed. Many neighboring genes are separated by relatively short intergenic regions, which is typical of bacterial genomes.



\### Pick a coordinate on the chromosome and visually inspect the surrounding sequence region.



Coordinate inspected:



NC\_000913.3:3,657,996-3,667,113



\### Describe all six reading frames (codons) that the coordinate could be part of.



The sequence can potentially be translated in six reading frames:



\- +1

\- +2

\- +3

\- -1

\- -2

\- -3



The positive reading frames are on the forward strand, while the negative reading frames are on the reverse strand.



\### Identify the type of feature displayed as a data track.



The displayed data track contains gene and coding sequence (CDS) annotations from the GFF annotation file.



\### Color features by their strand orientation.



Features can be distinguished based on strand orientation, allowing forward-strand and reverse-strand genomic features to be visualized separately.



\## IGV Visualization



The FASTA and GFF files were successfully loaded into IGV. Visualization of the genome showed multiple annotated genes, including:



\- gadW

\- gadY

\- gadX

\- gadA



The annotation track displayed genomic features and their positions along the chromosome.



\## Reproducibility



The genome and annotation files can be reproduced by running the Makefile and downloading the required files from NCBI. The downloaded files can then be loaded into IGV for visualization and inspection.

