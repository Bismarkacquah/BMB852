# Data provenance and analysis settings

## Study and selection

The authoritative [ENA project record](https://www.ebi.ac.uk/ena/browser/view/PRJEB51295) is archived in [PRJEB51295.xml](PRJEB51295.xml). Its title is *Genome-wide specificity of genome editing by both CRISPR-Cas9 and TALEN in the model plant Physcomitrium patens*. The study investigates off-target and unexpected genome changes in edited plants and controls. Its published conclusions are background, not outcomes independently established by this assignment.

The live [run metadata](study-runs.tsv), retrieved on 2026-10-21, lists 14 paired-end WGS runs. The primary design selects the first ten accessions in ascending order, ERR8982183 through ERR8982192. It includes two controls, four CRIS-labelled samples, two PEG-labelled samples, one PEG-DNA sample, and one TAL-labelled sample. It excludes TAL#2 and WTA/WTB/WTC, so it is not a balanced reproduction of the full study.

## Reference and read depth

All samples use [GCA_000002425.2](https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_000002425.2/), Phypa V3, with 471,852,792 reference bases. Its exact uncompressed FASTA SHA-256 is `eda3922af8c6711133b05f3261118e5d75adebd3aebc8d47cb9e4cd8b11bc3b4`.

The primary design uses the first 20 million synchronized read pairs per run. With 151-bp reads, this is approximately 12.8x nominal input depth; measured mapped, quality-filtered depth is lower and is reported separately. Prefix sampling is deterministic, not random. Each manifest records the requested count, mate-ID synchronization hash, source URLs, and compressed-file checksums. New manifests also record downloaded nucleotide counts.

## Processing

Cutadapt removes the Illumina adapters specified in the scripts, trims quality 20 from both ends, and removes pairs failing a 30-base minimum. BWA MEM adds run-specific read groups; SAMtools sorts and indexes the BAM. BCFtools uses mapping and base quality thresholds of 20, a maximum pileup depth of 1,000, the design's ploidy, reference normalization, and QUAL >=20 plus sample DP >=3. Haploid calling is an assumption inherited from the earlier moss analysis.

VCFs are merged without assuming missing calls are reference genotypes. The validator checks the exact allele union, sample-column order, and each carried genotype. Variant totals are differences from the selected reference, not counts of editing-induced or off-target mutations.

Coverage uses `samtools coverage -q 20 -Q 0`, with the full reference length as denominator. Locus review additionally uses BAM depth with base and mapping quality >=20. Caller DP and a separate depth calculation can differ because of read-overlap handling and filtering.

## Reuse and reproducibility

On this workstation, the five original 20-million-pair alignments were reused from Week 7/8. Their reference lengths, sample read groups, raw mate counts/ID hashes, BAM integrity, and BAM checksums were verified. New samples use matching read preprocessing. The source alignments are not edited; all ten VCFs are called with the Week 9 script. The published workflow downloads and processes all samples when those local caches are absent and does not depend on earlier-week files.

Optional `scripts/import_alignment.py` supports this local reuse; it is not called by the default workflow. The final deep-run manifests archive the reuse evidence. The CSV records explicit BWA input batch sizes: 40 million bases for ERR8982183/ERR8982185/ERR8982186 and 30 million for the other deep samples. These match the original program headers and logs. Fresh alignments use `bwa mem -K` so batching is independent of thread count. Byte-identical BAMs across environments are not assumed.

The original 10,000-pair smoke evidence is retained under `results/smoke/`. The new `design.smoke.csv` tests the current CSV, trimming, single-sample calling, and merge path. Smoke-test counts are not the full-depth findings. No tools are installed by any target. Additional prerequisites outside this workstation's baseline bioinfo environment are cutadapt, IGV, and matplotlib for boxed screenshots; the README identifies their tested versions.

The report creates a standard Tabix index alongside the compressed VCF for IGV loading, as described in the [IGV file-format documentation](https://igv.org/doc/desktop/FileFormats/DataTracks/). The batch and session paths are regenerated for the execution checkout.

## Final verification

All ten 20-million-pair samples completed successfully. The merged VCF contains 47,442 allele records with verified sample order, exact allele union, and carried genotypes. Eight unit tests, a fresh ten-sample 10,000-pair workflow in an isolated directory, a repeat deep batch, and final VCF/figure checksums passed. The deep run reused five verified BAMs and aligned five new samples; a second cold ten-sample 20-million-pair run was not performed. See [final verification](deep-final-verification.txt) and [fresh smoke verification](final-smoke-verification.txt).

Visual review confirmed that both closeups and the regional view show all ten BAMs. The SNP rectangle follows position 3,386 on ABEU02000029.1. The indel rectangle spans the anchored AT>A event at 25,818 on ABEU02000041.1; the deleted T follows the anchor. Original screenshots are retained alongside the boxed copies. The regional view contains shared coverage gaps, so these regions cannot be treated as confidently reference matching.

BCFtools emits a non-fatal header warning that MQ should have Float type. This reflects the caller's existing MQ header declaration; sample, allele, genotype, and checksum validations still pass. The data were not altered to suppress the warning.
