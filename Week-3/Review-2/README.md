# Assessment of a student's repository

I am reviewing Lauren Magliaro's repository: [BMMB-852-lmm](repository/README.md).

## Security Check

I inspected the Week 02 and Week 03 Makefiles. The workflows download genome and annotation files from Ensembl and NCBI using `wget` or the NCBI `datasets` command. The downloaded files are not executed. The URLs should remain restricted to trusted official sources.

The `clean` targets remove downloaded data directories and generated files. This is useful for reproducing a fresh download, but the README should warn users that the command deletes local data.

## README Evaluation

The repository documents the selected organism, the required tools, and the expected FASTA and GFF outputs. The Week 03 Makefile also reports genome size, sequence count, and annotation feature count, which makes the result easier to check.

The workflow is reproducible because variables define the accession, species, output paths, and download URLs. The `prepare` step checks for existing outputs before downloading again, extracts the archive, moves the relevant files, and removes temporary metadata.

One clarity issue is that the Week 02 `clean` recipe removes directories after separately naming files for removal. The directory removal already removes those files, so the redundant file-removal line can be deleted. The README should also show the exact command used to count annotation features.

## Comparison With My Week 2 Lamin Analysis

My Week 2 analysis downloads *Zygosaccharomyces bailii* data from Ensembl,
places the FASTA and GFF3 files in `week2/igv/fasta` and `week2/igv/gff`,
indexes the FASTA, and uses IGV to examine a selected chromosome region,
reading frames, strand orientation, and annotation counts. Lauren's workflow
uses the same general reproducible pattern of a Makefile plus IGV, but her
workflow is organized around separate `fasta` and `gff` targets and explicit
Ensembl variables for the species, assembly, release, URLs, and output files.

Compared with my Lamin workflow, Lauren's Makefile makes the download targets
and output names especially easy to inspect. My README gives more detailed
biological interpretation of the IGV view, including the selected coordinate
and frame/strand observations. Lauren's Week 03 workflow also adds a summary
target that reports genome size, sequence count, and annotation feature count,
which is a useful reproducibility check that my Lamin workflow should include.

## Proposed Edits

- Add explicit messages when FASTA or GFF outputs already exist.
- Remove redundant cleanup commands and keep the `clean` target focused on generated data.
- Put the annotation-count command in the Makefile as a named target.
- Document required tools such as `wget`, `unzip`, `datasets`, and `awk` near the reproduction commands.

## Pull Request

I would submit these changes as a pull request to the forked repository after testing the Makefile from a clean directory. No pull request was created as part of this local review.
