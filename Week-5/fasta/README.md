# Week 5 FASTA files

This folder contains the local *Physcomitrium patens* reference genome:

```text
GCA_000002425.2_Phypa_V3_genomic.fna
GCA_000002425.2_Phypa_V3_genomic.fna.fai
```

The large reference and generated indexes are ignored by Git. From `Week-5`,
run `make setup` to retrieve missing inputs or copy the FASTA from Week 2.
`make reference` creates the FASTA index. You can also create that index with
`samtools faidx fasta/GCA_000002425.2_Phypa_V3_genomic.fna` if needed.

The annotation remains at `../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.gff`
(relative to `Week-5`).
