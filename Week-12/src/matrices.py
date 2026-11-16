"""Merge Salmon NumReads by transcript ID, then sum transcripts by gene ID."""
import argparse
import csv
import json
import re
from decimal import Decimal
from pathlib import Path


def sample_names(design):
    with open(design, newline="") as handle:
        names = [row["sample"] for row in csv.DictReader(handle)]
    if not names or len(names) != len(set(names)):
        raise ValueError("Design must contain unique, nonempty sample names")
    if any(not re.fullmatch(r"[A-Za-z0-9_-]+", name) for name in names):
        raise ValueError("Sample names must contain only letters, digits, underscores or hyphens")
    return names


def transcript_genes(gtf):
    mapping = {}
    with open(gtf) as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9:
                raise ValueError("Malformed GTF row")
            attributes = dict(re.findall(r'(\w+) "([^"]+)"', fields[8]))
            tx, gene = attributes.get("transcript_id"), attributes.get("gene_id")
            if tx and gene:
                if tx in mapping and mapping[tx] != gene:
                    raise ValueError(f"Transcript maps to multiple genes: {tx}")
                mapping[tx] = gene
    if not mapping:
        raise ValueError("No transcript-to-gene mappings found")
    return mapping


def read_quant(path):
    counts = {}
    with open(path, newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not {"Name", "NumReads"}.issubset(reader.fieldnames or []):
            raise ValueError(f"Missing Salmon count columns: {path}")
        for row in reader:
            tx, value = row["Name"], Decimal(row["NumReads"])
            if tx in counts or not value.is_finite() or value < 0:
                raise ValueError(f"Duplicate transcript or invalid count: {path}: {tx}")
            counts[tx] = value
    if not counts:
        raise ValueError(f"Empty quantification: {path}")
    return counts


def write_table(path, header, rows):
    with open(path, "w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def build(design, gtf, quant, output):
    samples = sample_names(design)
    mapping = transcript_genes(gtf)
    counts = [read_quant(Path(quant) / sample / "quant.sf") for sample in samples]
    ids = set(counts[0])
    if any(set(column) != ids for column in counts):
        raise ValueError("Samples have different transcript sets; use a common index")
    missing = ids - mapping.keys()
    if missing:
        raise ValueError(f"Unmapped transcript IDs (check reference versions): {sorted(missing)[:5]}")
    genes = {}
    for tx in sorted(ids):
        values = genes.setdefault(mapping[tx], [Decimal(0) for _ in samples])
        for i, column in enumerate(counts):
            values[i] += column[tx]
    totals = [sum(column.values(), Decimal(0)) for column in counts]
    gene_totals = [sum((values[i] for values in genes.values()), Decimal(0))
                   for i in range(len(samples))]
    if totals != gene_totals:
        raise ValueError("Transcript and gene totals differ")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    write_table(output / "transcript_counts.tsv", ["transcript_id", *samples],
                ([tx, *(column[tx] for column in counts)] for tx in sorted(ids)))
    write_table(output / "gene_counts.tsv", ["gene_id", *samples],
                ([gene, *genes[gene]] for gene in sorted(genes)))
    write_table(output / "tx2gene.tsv", ["transcript_id", "gene_id"],
                ([tx, mapping[tx]] for tx in sorted(ids)))
    summary = {"samples": samples, "transcripts": len(ids), "genes": len(genes),
               "count_column": "NumReads", "totals_match": True,
               "sample_totals": dict(zip(samples, map(str, totals))),
               "annotated_transcripts_not_quantified": len(mapping.keys() - ids)}
    (output / "validation.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", default="design.csv")
    parser.add_argument("--gtf", default="data/gtf/chr22.gtf")
    parser.add_argument("--quant", default="quant")
    parser.add_argument("--output", default="results")
    args = parser.parse_args()
    build(args.design, args.gtf, args.quant, args.output)
