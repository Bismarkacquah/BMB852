# Workflow code and notes

Run commands from `Week-5`. The comments explain the commands used to prepare the inputs, align the
reads, calculate coverage, and generate the IGV views.

## environment.yml

`name` names the isolated environment. `channels` lists package repositories,
searched in the displayed order. `dependencies` lists programs to install;
`=version` constrains the version. Python runs the helper scripts, BWA aligns
reads, Samtools processes alignments, Cutadapt trims reads, SRA Toolkit retrieves
reads, Make schedules file dependencies, curl downloads references, and gzip
decompresses them. These pins specify a reproduction environment; they are
not a claim that every original preparation tool used exactly these versions.

```yaml
name: week5-moss
channels:
  - conda-forge
  - bioconda
dependencies:
  - python=3.12
  - bwa=0.7.19
  - samtools=1.22.1
  - cutadapt=5.2
  - sra-tools=3.2.1
  - make
  - curl
  - gzip
```

## Makefile

```makefile
# Execute recipes in Bash and stop if any command in a pipeline fails.
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
# A plain make runs the analysis rather than only printing help.
.DEFAULT_GOAL := all
# Remove incomplete target files after a failed recipe.
.DELETE_ON_ERROR:
# Moss reference and trimmed paired-end inputs.
REFERENCE := fasta/GCA_000002425.2_Phypa_V3_genomic.fna
ANNOTATION := ../Week-2/data/GCA_000002425.2_Phypa_V3_genomic.gff
READ1 := ../Week-4/data/trimmed/ERR8982185_1.trimmed.fastq.gz
READ2 := ../Week-4/data/trimmed/ERR8982185_2.trimmed.fastq.gz
# Name alignment and coverage outputs once for reuse below.
BAM := bam/ERR8982185.sorted.bam
STATS := bam/ERR8982185.flagstat.txt
COVERAGE := coverage/ERR8982185.coverage.tsv
DEPTH := coverage/ERR8982185.covered_depth.tsv
SUMMARY := coverage/ERR8982185.depth_summary.json
# Allow the thread count to be overridden, for example make THREADS=4.
THREADS ?= 2
# These names are commands, not files that Make should look for.
.PHONY: all setup check-tools check-inputs reference index align sort index-bam stats coverage depth estimate igv
# Build compact summaries; the 10 GB all-position depth file is unnecessary.
all: $(STATS) $(COVERAGE) $(SUMMARY)
# Download missing inputs without replacing existing nonempty input files.
setup:
	bash scripts/prepare_inputs.sh
# Check the tools used for alignment and summarization.
check-tools:
	command -v bwa
	command -v samtools
	command -v python3
# Verify all four required inputs are nonempty.
check-inputs:
	test -s $(REFERENCE)
	test -s $(ANNOTATION)
	test -s $(READ1)
	test -s $(READ2)
# Keep convenient names for individual stages.
reference: $(REFERENCE).fai
index: $(REFERENCE).bwt
align sort: $(BAM)
index-bam: $(BAM).bai
stats: $(STATS)
coverage: $(COVERAGE)
depth: $(DEPTH)
estimate: $(SUMMARY)
	cat $(SUMMARY)
# BWA builds its companion index files from the reference FASTA.
$(REFERENCE).bwt: $(REFERENCE)
	bwa index $<
# Samtools makes the random-access FASTA index needed by IGV.
$(REFERENCE).fai: $(REFERENCE)
	samtools faidx $<
# Map paired reads and stream alignments directly into coordinate sorting.
$(BAM): $(REFERENCE).bwt $(REFERENCE).fai $(READ1) $(READ2)
	mkdir -p bam
	bwa mem -t $(THREADS) $(REFERENCE) $(READ1) $(READ2) | samtools sort -@ $(THREADS) -o $@
	samtools quickcheck $@
# Index the sorted BAM for region queries and IGV navigation.
$(BAM).bai: $(BAM)
	samtools index $<
# Write alignment-flag counts and percentages.
$(STATS): $(BAM) $(BAM).bai
	samtools flagstat $(BAM) > $@
# Write one coverage summary row per reference sequence.
$(COVERAGE): $(BAM) $(BAM).bai
	mkdir -p coverage
	samtools coverage $(BAM) > $@
# Write sparse position depths; the FASTA index supplies the whole-genome denominator.
$(DEPTH): $(BAM) $(BAM).bai
	mkdir -p coverage
	samtools depth $(BAM) > $@
# Calculate exact depth statistics and the read-pair estimate from the inputs.
$(SUMMARY): $(DEPTH) $(REFERENCE).fai $(READ1) $(READ2) scripts/summarize_depth.py
	python3 scripts/summarize_depth.py
# Generate an IGV batch file containing paths for this checkout.
igv:
	python3 scripts/prepare_igv.py

# Recreate selected-region base observations and read-support pileups.
.PHONY: audit
audit: $(BAM).bai $(REFERENCE).fai
	python3 scripts/audit_mismatches.py
	samtools mpileup -B -Q 0 -f $(REFERENCE) -r CM009336.1:3475540-3475640 $(BAM) > bam/ERR8982185.zoom.pileup.txt
	samtools mpileup -B -Q 0 -f $(REFERENCE) -r CM009316.1:618250-618310 $(BAM) > bam/ERR8982185.read_end.pileup.txt
```

## scripts/prepare_inputs.sh

```bash
#!/usr/bin/env bash
# Stop on failed commands, unset variables, and failures inside pipelines.
set -euo pipefail
# Resolve this script's directory and enter Week-5 regardless of the launch directory.
cd "$(dirname "$0")/.."
# Assembly and sequencing run.
assembly=GCA_000002425.2_Phypa_V3
run=ERR8982185
# Use the first 1,000 sequencing spots.
spots=1000
# NCBI provides both reference sequence and annotation for this assembly.
base="https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/002/425/$assembly"
# Create input directories; existing directories and files are preserved.
mkdir -p fasta ../Week-2/data ../Week-4/data/raw ../Week-4/data/trimmed
# Retrieve each missing reference input; reuse the original Week-2 files if available.
for ext in fna gff; do
    # Use the assembly-specific name to keep FASTA and annotation matched.
    target="../Week-2/data/${assembly}_genomic.$ext"
    # A nonempty existing file does not need another download.
    if [[ ! -s "$target" ]]; then
        # Fail on HTTP errors, follow redirects, and retry transient failures.
        curl --fail --location --retry 3 "$base/${assembly}_genomic.$ext.gz" -o "$target.gz.part"
        # Decompress to a temporary file so interrupted runs do not leave a final output.
        gzip -dc "$target.gz.part" > "$target.part"
        # Confirm the decompressed input is nonempty before giving it the final name.
        test -s "$target.part"
        mv "$target.part" "$target"
    fi
done
# Keep a local FASTA copy for the Week-5 folder and IGV.
if [[ ! -s "fasta/${assembly}_genomic.fna" ]]; then
    cp "../Week-2/data/${assembly}_genomic.fna" "fasta/${assembly}_genomic.fna"
fi
# Download and trim only when either trimmed mate is missing.
if [[ ! -s "../Week-4/data/trimmed/${run}_1.trimmed.fastq.gz" || ! -s "../Week-4/data/trimmed/${run}_2.trimmed.fastq.gz" ]]; then
    # Reuse the raw subset if both mates are already present.
    if [[ ! -s "../Week-4/data/raw/${run}_1.fastq.gz" || ! -s "../Week-4/data/raw/${run}_2.fastq.gz" ]]; then
        # Split paired reads into mate files, compress them, and stop at spot 1,000.
        fastq-dump --split-files --gzip --maxSpotId "$spots" --outdir ../Week-4/data/raw "$run"
    fi
    # Use two cores, trim the two Illumina adapters, trim ends at Q20, and require 30 bases.
    # -o and -p name the paired output files; the final two arguments are raw mate inputs.
    cutadapt -j 2 -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT -q 20,20 -m 30 \
        -o "../Week-4/data/trimmed/${run}_1.trimmed.fastq.gz" -p "../Week-4/data/trimmed/${run}_2.trimmed.fastq.gz" \
        "../Week-4/data/raw/${run}_1.fastq.gz" "../Week-4/data/raw/${run}_2.fastq.gz"
fi
```

## scripts/summarize_depth.py

```python
"""Summarize sparse depth while counting uncovered reference positions."""
import gzip  # Read compressed FASTQ inputs without extracting them.
import json  # Save a small machine-readable report.
import math  # Round the required pair count upward.
from pathlib import Path  # Resolve paths independently of the working directory.
root = Path(__file__).resolve().parents[1]  # Week-5 contains this script folder.
fai = root / "fasta/GCA_000002425.2_Phypa_V3_genomic.fna.fai"  # Reference index.
genome = sum(int(line.split()[1]) for line in fai.read_text().splitlines())  # Sum contig lengths.
covered = total = maximum = 0  # Initialize depth counters.
with (root / "coverage/ERR8982185.covered_depth.tsv").open() as handle:  # Stream, avoiding a large list.
    for line in handle:  # Process each reported position.
        depth = int(line.split()[2])  # Third column is depth.
        covered += depth > 0  # Count only positions with at least one read.
        total += depth  # Add aligned-base observations.
        maximum = max(maximum, depth)  # Track the largest depth.
counts = []  # Keep read and base totals for each mate separately.
for mate in (1, 2):  # Process R1 and R2.
    path = root.parent / f"Week-4/data/trimmed/ERR8982185_{mate}.trimmed.fastq.gz"  # Input mate.
    reads = bases = 0  # Reset mate counters.
    with gzip.open(path, "rt") as handle:  # Decode gzip as text.
        for index, line in enumerate(handle):  # FASTQ records contain four lines.
            if index % 4 == 1:  # The second line contains the sequence.
                reads += 1  # Count a read.
                bases += len(line.strip())  # Count sequenced bases.
    counts.append((reads, bases))  # Save the mate totals.
assert counts[0][0] == counts[1][0] and counts[0][0] > 0, "Mate counts must agree"  # Basic pairing check.
pairs = counts[0][0]  # One R1 plus one R2 is one pair.
bases = sum(item[1] for item in counts)  # Total trimmed bases.
result = dict(genome_bases=genome, covered_bases=covered, sum_depth=total,
              covered_percent=100*covered/genome, mean_depth_genome=total/genome,
              mean_depth_covered=total/covered if covered else 0, max_depth=maximum,
              trimmed_pairs=pairs, trimmed_bases=bases,
              read_pairs_for_10x=math.ceil(10*genome*pairs/bases))  # Calculate the reported metrics.
(root / "coverage/ERR8982185.depth_summary.json").write_text(json.dumps(result, indent=2)+"\n")  # Save JSON.
print(json.dumps(result, indent=2))  # Show the same results in the terminal.
```

## scripts/prepare_igv.py

```python
"""Create an IGV batch script for the four selected regions."""
import argparse  # Accept a host-visible directory when using WSL with Windows IGV.
from pathlib import Path  # Resolve the local checkout.
parser = argparse.ArgumentParser()  # Define the command interface.
parser.add_argument("--igv-root", help="Absolute Week-5 directory as seen by IGV")  # Optional host path.
args = parser.parse_args()  # Read command-line arguments.
root = Path(__file__).resolve().parents[1]  # Local Week-5 directory.
host = (args.igv_root or root.as_posix()).replace("\\", "/").rstrip("/")  # Normalize IGV paths.
parent = host.rsplit("/", 1)[0]  # Week-2 is next to Week-5.
commands = ["new", f"snapshotDirectory {host}/screenshots",
            f"genome {host}/fasta/GCA_000002425.2_Phypa_V3_genomic.fna",
            f"load {parent}/Week-2/data/GCA_000002425.2_Phypa_V3_genomic.gff",
            f"load {host}/bam/ERR8982185.sorted.bam", "maxPanelHeight 500"]  # Load matching inputs.
views = [("CM009336.1:3475540-3475640", "week5_zoom_mismatches.png"),
         ("CM009316.1:618250-618310", "week5_zoom_read_end.png"),
         ("CM009336.1:3475450-3475530", "week5_zoom_depth4.png"),
         ("CM009316.1:8931-13135", "week5_moss_gene_locus.png")]  # Informative intervals.
for locus, filename in views:  # Save the same four views in any checkout.
    commands.extend([f"goto {locus}", f"snapshot {filename}"])  # Navigate, then capture.
commands.append("exit")  # Close the batch IGV instance after capture.
output = root / "scripts/igv_local_batch.txt"  # This machine-specific file is ignored by Git.
output.write_text("\n".join(commands)+"\n")  # Write one command per line.
print(output)  # Tell the user which file to open in IGV.
```

## Syntax and options

| Code | Meaning |
| --- | --- |
| `name=value` in Bash | Assign a variable; quote its expansion to preserve spaces. |
| `$(...)` in Bash | Substitute a command's output. |
| `[[ -s file ]]` | Check that a file exists and is nonempty. |
| `if`, `then`, `fi` | Start a condition, execute its body, and end the condition. |
| `for`, `do`, `done` | Repeat a block for each listed value. |
| `\` at a shell line end | Continue the same command on the next line. |
| `fastq-dump --maxSpotId 1000` | Select the first 1,000 spots rather than downloading the full FASTQ run. |
| `--split-files --gzip` | Write separate compressed mate files. |
| `cutadapt -a`, `-A` | Adapter sequences for read 1 and read 2. |
| `-q 20,20 -m 30` | Trim both ends at Q20 and reject pairs failing the 30-base minimum. |
| `cutadapt -o`, `-p` | Output paths for the two trimmed mate files. |
| `bwa mem -t` | Align paired reads with the specified thread count. |
| `samtools sort -@ ... -o ...` | Sort by coordinate using extra threads and save the BAM. |
| `samtools quickcheck` | Check the header and end-of-file marker; not exhaustive validation of every record. |
| `samtools index`, `faidx` | Index the BAM and FASTA for random access. |
| `samtools flagstat` | Count records by SAM alignment flags. |
| `samtools coverage` | Report covered bases and mean depth for each reference sequence. |
| `samtools depth` | Emit position depths without materializing all uncovered reference positions. |
| `dict(...)`, `json.dumps(...)` | Collect named statistics and serialize them as JSON. |
| `with ... as ...` | Open a file and close it automatically when the block ends. |
| `enumerate(...)` | Return both each item's index and value. |
| `max`, `sum`, `math.ceil` | Find a maximum, add values, and round upward. |

## IGV batch commands

The generator writes `new` to start a fresh session, `snapshotDirectory` to
choose the output folder, `genome` to load the FASTA, and two `load` commands
to add GFF annotations and the BAM. `maxPanelHeight 500` limits panel height
in saved images. Each `goto` selects one interval and the following `snapshot`
writes its PNG. `exit` closes this batch instance after all images are saved.
The generator accepts `--igv-root` because Windows IGV needs Windows paths
when the analysis is run inside WSL.

## Coverage and mismatch interpretation

Whole-genome mean depth is summed depth divided by all FASTA bases, including
uncovered bases. Covered-base mean depth divides by positions with positive
depth only. Percent covered is positive-depth positions / reference length
multiplied by 100. The 10x estimate is rounded up from 10 times reference
length divided by average trimmed bases per pair. It assumes no mapping loss.

The README's `mpileup -B -Q 0 -f ... -r ...` commands inspect selected regions:
`-B` disables base-alignment quality adjustment, `-Q 0` includes low-quality
calls, `-f` provides the reference, and `-r` selects the interval. In pileup
text, dots and commas are reference matches on forward and reverse strands;
letters are observed alternate bases. These are inspection outputs, not
validated variant calls. The saved mismatch audit is a supporting record;
the reproducible pileups are the source for the report's support counts.

## scripts/audit_mismatches.py

Run `make audit` to recreate the mismatch TSV and pileups.

```python
"""Recreate the selected-region mismatch audit directly from BAM and FASTA."""
import csv  # Write a tab-separated evidence table.
import re  # Decode the CIGAR operations describing each alignment.
import subprocess  # Ask Samtools to decode BAM records.
from pathlib import Path  # Locate the checkout without hard-coded user paths.
root = Path(__file__).resolve().parents[1]  # Week-5 directory.
fasta = root / "fasta/GCA_000002425.2_Phypa_V3_genomic.fna"  # Matching reference.
index = {}  # Store random-access offsets for each reference sequence.
for line in Path(str(fasta)+".fai").read_text().splitlines():  # Read FASTA index rows.
    fields = line.split()  # Separate reference name and numerical fields.
    index[fields[0]] = list(map(int, fields[1:]))  # Length, byte offset, bases/line, bytes/line.
rows = []  # Accumulate the small selected-region evidence table.
with fasta.open("rb") as reference:  # Binary mode preserves byte offsets.
    for region in ("CM009316.1:618001-619000", "CM009336.1:3475201-3476100"):
        text = subprocess.check_output(["samtools", "view", "-F", "2308",
                                       str(root / "bam/ERR8982185.sorted.bam"), region], text=True)  # Exclude unmapped/secondary/supplementary records.
        for line in text.splitlines():  # Process each primary aligned read.
            f = line.split("\t")  # Split SAM columns.
            flag, pos, query = int(f[1]), int(f[3]), 0  # Flag, reference position, read offset.
            for amount, op in re.findall(r"(\d+)([MIDNSHP=X])", f[5]):  # Decode CIGAR.
                amount = int(amount)  # Convert operation length to an integer.
                if op in "M=X":  # These operations consume both read and reference.
                    length, offset, width, line_bytes = index[f[2]]  # FASTA layout.
                    start = pos - 1  # Convert one-based SAM to zero-based FASTA offset.
                    reference.seek(offset + start//width*line_bytes + start%width)  # Seek first base.
                    extra = (amount//width+2)*(line_bytes-width)  # Allow for line terminators.
                    seq = reference.read(amount+extra).replace(b"\n", b"").replace(b"\r", b"")[:amount].decode().upper()  # Read reference bases.
                    for i, (a, b) in enumerate(zip(seq, f[9][query:query+amount])):  # Compare aligned bases.
                        if a != b:  # Record mismatches, including unknown N calls.
                            rows.append([f[2], pos+i, a, b, f[0], int(f[4]),
                                         ord(f[10][query+i])-33, query+i+1, len(f[9]),
                                         "-" if flag & 16 else "+"])  # Decode Phred+33 quality and strand.
                    pos += amount  # Advance the reference cursor.
                    query += amount  # Advance the read cursor.
                elif op in "IS":  # Insertions and soft clips consume only read bases.
                    query += amount
                elif op in "DN":  # Deletions and skips consume only reference bases.
                    pos += amount
with (root / "bam/ERR8982185.zoom_mismatches.tsv").open("w", newline="") as output:
    writer = csv.writer(output, delimiter="\t")  # Use TSV for easy inspection.
    writer.writerow(["reference", "position", "ref_base", "read_base", "read", "mapq",
                     "baseq", "position_in_alignment_sequence", "read_length", "strand"])  # Column names.
    writer.writerows(rows)  # Save each observation; do not classify it as a variant.
```
