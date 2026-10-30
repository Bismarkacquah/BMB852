# Study and analysis notes

The input study is ENA PRJEB51295, *Genome-wide specificity of genome editing by both CRISPR-Cas9 and TALEN in the model plant Physcomitrium patens*. The design selects ERR8982183–ERR8982192 in accession order: two controls, four CRIS-labelled samples, two PEG-labelled samples, one PEG-DNA sample, and one TAL sample. This is an unbalanced subset of the study.

The reference is Phypa V3 (GCA_000002425.2), with 471,852,792 bases. The uncompressed FASTA SHA-256 is `eda3922af8c6711133b05f3261118e5d75adebd3aebc8d47cb9e4cd8b11bc3b4`.

Each full-depth sample uses the first 20 million synchronized read pairs. Prefix sampling is deterministic rather than random. Cutadapt removes adapters, trims at quality 20, and removes pairs failing a 30-base minimum. BWA MEM aligns reads with sample-specific read groups; SAMtools sorts and indexes alignments. BCFtools calls haploid variants with mapping/base quality thresholds of 20 and maximum pileup depth 1,000, then normalizes and filters at QUAL >=20 and sample DP >=3.

The merge preserves missing genotypes rather than assuming reference calls. Validation checks sample order, the exact allele union, and carried genotypes. Coverage uses `samtools coverage -q 20 -Q 0`, with the whole reference as denominator.

The saved full analysis reused five verified alignments from earlier work and aligned five new samples. The published workflow can download and process all ten samples independently. A second cold full-depth run was not performed. Historical execution logs and screenshots are kept locally rather than included in the submitted file list.
