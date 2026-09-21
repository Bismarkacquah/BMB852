import gzip
from pathlib import Path


root = Path(__file__).resolve().parent
reference = root / "data" / "GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.fna.gz"
output = root / "data" / "lamin_gene.fasta"
contig = "NT_033779.5"
start = 5_542_480
end = 5_546_642

sequence_parts = []
reading_contig = False
with gzip.open(reference, "rt", encoding="ascii") as handle:
    for line in handle:
        line = line.strip()
        if line.startswith(">"):
            reading_contig = line[1:].split()[0] == contig
            continue
        if reading_contig:
            sequence_parts.append(line)

if not sequence_parts:
    raise RuntimeError(f"Contig {contig} was not found in {reference}")

sequence = "".join(sequence_parts)[start - 1:end]
if len(sequence) != end - start + 1:
    raise RuntimeError(f"Expected {end - start + 1} bp, found {len(sequence)} bp")

output.write_text(
    f">Drosophila_melanogaster_Lam|{contig}:{start}-{end}|assembly=GCF_000001215.4\n"
    + "\n".join(sequence[index:index + 80] for index in range(0, len(sequence), 80))
    + "\n",
    encoding="ascii",
)
print(f"Wrote {output} ({len(sequence)} bp)")
