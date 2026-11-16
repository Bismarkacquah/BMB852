# Control#1 recovery

The original long-running shell job ended with an unexpected-EOF parsing error after its processing script was edited while it was running. Its completed coordinate-sorted BAM, BAM index, and filtered VCF remained intact. Make removed the PASS VCF on recipe failure.

Recovery reused the existing filtered VCF: `bcftools view -f PASS -Oz`, followed by CSI indexing, reference-allele validation (`bcftools norm -f ... -c e`), VCF statistics, and SHA-256 recording. SAMtools quickcheck passed for the existing BAM. The recovered PASS VCF contains 21,396 records. Alignment and variant-calling thresholds were not changed.

A duplicate restart was stopped during trimming, before it could overwrite the completed BAM. Its interrupted trimmed FASTQ files are being regenerated from the checksum-verified raw files with the same cutadapt settings. No running processing scripts are being edited further.
