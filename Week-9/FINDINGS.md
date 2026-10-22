# Week 9 findings

All results below use the ten 20-million-pair samples. The old smoke-test findings are not mixed into this analysis.

## Coverage and retained calls

| Sample | Label | Retained records | Mean reference depth | Reference covered |
|---|---|---:|---:|---:|
| ERR8982183 | Control#1 | 21,396 | 8.03× | 96.19% |
| ERR8982184 | Control#2 | 22,438 | 8.23× | 96.28% |
| ERR8982185 | CRIS1#1 | 24,042 | 8.42× | 96.48% |
| ERR8982186 | CRIS1#2 | 24,009 | 8.57× | 96.24% |
| ERR8982187 | CRIS2#1 | 23,655 | 8.07× | 96.38% |
| ERR8982188 | CRIS2#2 | 23,461 | 8.33× | 96.25% |
| ERR8982189 | PEG#1 | 21,061 | 7.82× | 95.89% |
| ERR8982190 | PEG#2 | 22,660 | 8.44× | 96.56% |
| ERR8982191 | PEG-DNA#1 | 22,691 | 8.73× | 96.42% |
| ERR8982192 | TAL#1 | 23,364 | 8.39× | 96.20% |

Coverage uses `samtools coverage -q 20 -Q 0`, divided by the entire reference length, including uncovered sequence. Mean depth and coverage breadth describe different properties; neither guarantees adequate depth at every site. Call counts are affected by depth, alignment, and filtering as well as biology.

## IGV read evidence

All ten BAMs and the merged VCF are loaded against the same reference. Each BAM track is named by its run accession. The red rectangle follows the selected reference position through the genotype rows and read tracks. Pink/purple read backgrounds encode strand; colored bases and indel markers indicate sequence differences. Explanations appear below each image.

### Example 1: ABEU02000029.1:3,386 G>T

![Ten-sample SNP evidence](results/igv/example_1.boxed.png)

This SNP has retained calls in **10/10 samples**. The rectangle identifies its exact position, rather than neighboring mismatch columns. Read support is summarized below; `.` means an unknown genotype in the variant-only merge.

| Sample | Label | GT | Usable DP | AD (REF,ALT) | Quality-filtered BAM depth |
|---|---|---|---:|---|---:|
| ERR8982183 | Control#1 | `1` | 10 | `0,10` | 13 |
| ERR8982184 | Control#2 | `1` | 3 | `0,3` | 4 |
| ERR8982185 | CRIS1#1 | `1` | 11 | `0,11` | 11 |
| ERR8982186 | CRIS1#2 | `1` | 11 | `0,11` | 11 |
| ERR8982187 | CRIS2#1 | `1` | 15 | `0,15` | 18 |
| ERR8982188 | CRIS2#2 | `1` | 12 | `0,12` | 17 |
| ERR8982189 | PEG#1 | `1` | 9 | `0,9` | 10 |
| ERR8982190 | PEG#2 | `1` | 11 | `0,11` | 14 |
| ERR8982191 | PEG-DNA#1 | `1` | 8 | `0,8` | 10 |
| ERR8982192 | TAL#1 | `1` | 8 | `0,8` | 8 |

Retained calls occur in these study-label groups: **CRIS1, CRIS2, Control, PEG, PEG-DNA, TAL**. Presence across groups is consistent with a shared difference from the chosen reference, rather than evidence of an editing-specific change. Missing calls elsewhere cannot be interpreted as confirmed reference genotypes.

Position depth without base/mapping-quality thresholds ranges from 4 to 20 reads across samples, using SAMtools depth with its default flag filters. Examples are limited to moderate read density so the ten-track view remains readable.

Usable DP/AD comes from the variant caller. The separate BAM depth uses base quality ≥20 and mapping quality ≥20; overlap handling and filtering can make it differ from caller DP. These are read-support observations, not experimental confirmation or functional-effect predictions.

[Original IGV screenshot](results/igv/example_1.png). The rectangle is a presentation overlay; read data are unchanged.

### Example 2: ABEU02000041.1:25,818 AT>A

![Ten-sample indel evidence](results/igv/example_2.boxed.png)

This indel has retained calls in **10/10 samples**. The rectangle identifies its exact position, rather than neighboring mismatch columns. Read support is summarized below; `.` means an unknown genotype in the variant-only merge.

| Sample | Label | GT | Usable DP | AD (REF,ALT) | Quality-filtered BAM depth |
|---|---|---|---:|---|---:|
| ERR8982183 | Control#1 | `1` | 8 | `0,8` | 8 |
| ERR8982184 | Control#2 | `1` | 8 | `0,8` | 13 |
| ERR8982185 | CRIS1#1 | `1` | 3 | `0,3` | 5 |
| ERR8982186 | CRIS1#2 | `1` | 8 | `3,5` | 9 |
| ERR8982187 | CRIS2#1 | `1` | 8 | `1,7` | 7 |
| ERR8982188 | CRIS2#2 | `1` | 15 | `3,12` | 20 |
| ERR8982189 | PEG#1 | `1` | 7 | `0,7` | 6 |
| ERR8982190 | PEG#2 | `1` | 14 | `1,13` | 13 |
| ERR8982191 | PEG-DNA#1 | `1` | 3 | `0,3` | 4 |
| ERR8982192 | TAL#1 | `1` | 15 | `1,14` | 17 |

Retained calls occur in these study-label groups: **CRIS1, CRIS2, Control, PEG, PEG-DNA, TAL**. Presence across groups is consistent with a shared difference from the chosen reference, rather than evidence of an editing-specific change. Missing calls elsewhere cannot be interpreted as confirmed reference genotypes.

Position depth without base/mapping-quality thresholds ranges from 7 to 24 reads across samples, using SAMtools depth with its default flag filters. Examples are limited to moderate read density so the ten-track view remains readable.

Usable DP/AD comes from the variant caller. The separate BAM depth uses base quality ≥20 and mapping quality ≥20; overlap handling and filtering can make it differ from caller DP. These are read-support observations, not experimental confirmation or functional-effect predictions.

[Original IGV screenshot](results/igv/example_2.png). The rectangle is a presentation overlay; read data are unchanged.

## Regional context

![Ten-sample regional coverage](results/igv/regional.png)

This 5-kb window surrounds the SNP example. Inspect coverage continuity and local read placement before interpreting a variant. Tracks can autoscale independently, so compare their numeric scales rather than apparent bar heights alone.

## Interpretation limits

This is a selected, unbalanced subset of an editing-specificity study. Prefix sampling is deterministic rather than random. Moderate coverage can miss variants, and variant-only merging does not establish which alleles are absent. Common-site genotyping and comparable callable regions are needed before testing group differences. The original study conclusions are context, not conclusions independently established by this exercise.

The saved IGV batch/session contains the execution machine’s paths. Run `make report` to regenerate paths for your checkout. Reopen the original images and your local session to inspect the evidence independently.
