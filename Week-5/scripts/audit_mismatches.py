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
