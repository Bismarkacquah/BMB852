# Data provenance

The ten runs in `design.tsv` are the first ten run accessions, sorted by accession, from the 14-run ENA archive saved for Week 8 (`../Week-8/provenance/study-runs.tsv`). They belong to [PRJEB51295](https://www.ebi.ac.uk/ena/browser/view/PRJEB51295). Labels are study metadata, not inferred experimental outcomes. Public paired FASTQ URLs are explicit in the design, so the workflow does not need files from earlier weeks.

Reference: [GCA_000002425.2](https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_000002425.2/), Phypa V3, *Physcomitrium patens*. The downloader verifies the exact uncompressed FASTA SHA-256, `eda3922af8c6711133b05f3261118e5d75adebd3aebc8d47cb9e4cd8b11bc3b4`.

Each run uses its first 10,000 synchronized read pairs, as specified in the design. Prefix sampling is deterministic but is not random. It is much shallower than the 20-million-pair Week 8 datasets. The haploid setting follows the earlier analysis and is an explicit assumption, recorded per sample in `ploidy`.

The workflow uses the original paired reads without an adapter-trimming stage. BWA aligns them to the same reference as the earlier assignment. BCFtools uses mapping quality 20, base quality 20, maximum pileup depth 1,000, and retains normalized variant records with QUAL at least 20 and sample DP at least 3. These are workflow-demonstration settings, not a full-depth evaluation of treatment-specific variation.
