"""Add gene names, compare gene counts with transcript sums, and show examples."""
import argparse
import csv
import re
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from matrices import transcript_genes, write_table


def read_matrix(path):
    with open(path, newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        values = {row[0]: list(map(Decimal, row[1:])) for row in reader}
    return header[1:], values


def markdown(headers, rows):
    def line(values):
        return "| " + " | ".join(map(str, values)) + " |"
    return "\n".join([line(headers), line(["---"] * len(headers)),
                      *(line(row) for row in rows)])


def report(gtf, output, readme):
    output = Path(output)
    samples, transcripts = read_matrix(output / "transcript_counts.tsv")
    gene_samples, genes = read_matrix(output / "gene_counts.tsv")
    if samples != gene_samples:
        raise ValueError("Sample order differs between matrices")
    mapping = transcript_genes(gtf)
    names = {}
    with open(gtf) as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            attributes = dict(re.findall(r'(\w+) "([^"]+)"', line.split("\t")[8]))
            if "gene_id" in attributes and "gene_name" in attributes:
                names[attributes["gene_id"]] = attributes["gene_name"]
    summed = defaultdict(lambda: [Decimal(0) for _ in samples])
    members = defaultdict(list)
    for tx, values in transcripts.items():
        gene = mapping[tx]
        members[gene].append(tx)
        for i, value in enumerate(values):
            summed[gene][i] += value
    if set(summed) != set(genes):
        raise ValueError("Gene sets differ")
    differences = {gene: [value - total for value, total in zip(genes[gene], summed[gene])]
                   for gene in genes}
    if any(value != 0 for row in differences.values() for value in row):
        raise ValueError("Some gene counts differ from their transcript sums")
    write_table(output / "gene_counts_named.tsv", ["gene_id", "gene_name", *samples],
                ([gene, names.get(gene, "NA"), *values] for gene, values in genes.items()))
    write_table(output / "transcript_counts_named.tsv",
                ["transcript_id", "gene_id", "gene_name", *samples],
                ([tx, mapping[tx], names.get(mapping[tx], "NA"), *values]
                 for tx, values in transcripts.items()))
    write_table(output / "gene_transcript_comparison.tsv",
                ["gene_id", "gene_name", *(sample + "_difference" for sample in samples)],
                ([gene, names.get(gene, "NA"), *values] for gene, values in differences.items()))
    summary = []
    for i, sample in enumerate(samples):
        tx_total = sum(values[i] for values in transcripts.values())
        gene_total = sum(values[i] for values in genes.values())
        summary.append([sample, sum(values[i] > 0 for values in transcripts.values()),
                        sum(values[i] > 0 for values in genes.values()), tx_total, gene_total,
                        gene_total - tx_total])
    headers = ["Sample", "Nonzero transcripts", "Nonzero genes", "Transcript total", "Gene total", "Difference"]
    write_table(output / "count_summary.tsv", headers, summary)
    selected = [gene for name in ("OR11H1", "RPL3", "SYNGR1", "MPPED1")
                for gene in genes if names.get(gene) == name]
    gene_rows = [[names[gene], gene, *genes[gene]] for gene in selected]
    syn = next(gene for gene in selected if names[gene] == "SYNGR1")
    # Show all isoforms of one gene so the example can be checked by addition.
    tx_rows = [[tx, *transcripts[tx]] for tx in members[syn]]
    tx_rows.append(["SYNGR1 gene total", *genes[syn]])
    text = "\n\n".join([
        "## Checking the matrices",
        f"Both matrices have the same six sample columns. The transcript matrix has {len(transcripts):,} rows, and the gene matrix has {len(genes):,} rows. The table below shows how many have counts greater than zero in each sample.",
        markdown(headers, summary),
        "The totals match for every sample. I also compared each gene count with the sum of its transcripts. All differences were zero across all genes and samples, as expected from this method. This checks the aggregation step rather than agreement between independent counting tools. The full checks are in [count_summary.tsv](results/count_summary.tsv) and [gene_transcript_comparison.tsv](results/gene_transcript_comparison.tsv).",
        "### Gene names and examples",
        "I added gene names from the same GTF used for counting, so this step does not need an online annotation service. The original numeric matrices are unchanged. The named versions are [gene_counts_named.tsv](results/gene_counts_named.tsv) and [transcript_counts_named.tsv](results/transcript_counts_named.tsv). Gene IDs are used for grouping because names may be missing or shared.",
        markdown(["Gene", "Gene ID", *samples], gene_rows),
        "OR11H1 has zero counts in every sample. RPL3 has counts in all six samples. SYNGR1 and MPPED1 have higher raw counts in HBR than UHR. For SYNGR1, ENST00000328933.9 contributes most of the HBR gene count, consistent with the transcript discussed in Week 11.",
        "These are raw estimated counts, so library-size differences affect comparisons between samples. They can be checked alongside the Week 11 coverage observations, but they are not a test of differential expression.",
        "### Adding transcripts into a gene count",
        "Here are all the SYNGR1 transcripts. Adding each sample column gives the gene total in the last row. Values are shown at their original precision.",
        markdown(["Transcript", *samples], tx_rows),
    ])
    path = Path(readme)
    content = path.read_text(encoding="utf-8")
    start, end = "<!-- count-checks:start -->", "<!-- count-checks:end -->"
    block = start + "\n" + text + "\n" + end
    if start in content:
        before, rest = content.split(start, 1)
        _, after = rest.split(end, 1)
        content = before + block + after
    else:
        content = content.replace("## Working with AI", block + "\n\n## Working with AI")
    path.write_text(content, encoding="utf-8")
    print(f"Checked {len(genes)} genes across {len(samples)} samples; all differences are zero.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gtf", default="data/gtf/chr22.gtf")
    parser.add_argument("--output", default="results")
    parser.add_argument("--readme", default="README.md")
    args = parser.parse_args()
    report(args.gtf, args.output, args.readme)
