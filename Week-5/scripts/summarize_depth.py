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
