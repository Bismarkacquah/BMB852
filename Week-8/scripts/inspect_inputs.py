"""Validate Week 7 alleles and summarize gene overlaps; no effect prediction."""
import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vcf', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--gff', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('results'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    fai = {}
    with Path(str(args.reference) + '.fai').open() as handle:
        for line in handle:
            name, length, offset, bases, width = line.split()[:5]
            fai[name] = tuple(map(int, (length, offset, bases, width)))
    bins = defaultdict(list)
    genes = {}
    bin_size = 10000
    with args.gff.open() as handle:
        for line in handle:
            if line.startswith('#'):
                continue
            parts = line.rstrip('\n').split('\t')
            if len(parts) != 9 or parts[2] != 'gene':
                continue
            attributes = dict(item.split('=', 1) for item in parts[8].split(';') if '=' in item)
            gene_id = unquote(attributes['ID'])
            gene = (gene_id, unquote(attributes.get('Name', gene_id)), int(parts[3]), int(parts[4]), parts[6])
            genes[gene_id] = gene
            for bucket in range((gene[2] - 1) // bin_size, (gene[3] - 1) // bin_size + 1):
                bins[(parts[0], bucket)].append(gene)
    counts = Counter()
    gene_counts = Counter()
    contigs = Counter()
    candidates = []
    samples = []
    columns = ['chrom', 'pos', 'ref', 'alt', 'qual', 'depth', 'gene_ids', 'gene_names']
    with args.reference.open('rb') as fasta, gzip.open(args.vcf, 'rt') as vcf, (args.output / 'gene_overlaps.tsv').open('w', newline='') as out:
        writer = csv.writer(out, delimiter='\t')
        writer.writerow(columns)
        for line in vcf:
            if line.startswith('#CHROM'):
                samples = line.rstrip().split('\t')[9:]
            if line.startswith('#'):
                continue
            fields = line.rstrip().split('\t')
            chrom, pos_text, _, ref, alt, qual, filt, info = fields[:8]
            pos = int(pos_text)
            if filt != 'PASS':
                raise ValueError(f'Non-PASS record at {chrom}:{pos}')
            if chrom not in fai:
                raise ValueError(f'Contig absent from FASTA: {chrom}')
            length, offset, bases, width = fai[chrom]
            if pos < 1 or pos + len(ref) - 1 > length:
                raise ValueError(f'Out-of-bounds allele: {chrom}:{pos}')
            observed = bytearray()
            start = pos - 1
            remaining = len(ref)
            while remaining:
                take = min(remaining, bases - start % bases)
                fasta.seek(offset + (start // bases) * width + start % bases)
                observed.extend(fasta.read(take))
                remaining -= take
                start += take
            if observed.decode().upper() != ref.upper():
                raise ValueError(f'REF mismatch: {chrom}:{pos}')
            counts['records'] += 1
            counts['reference_matches'] += 1
            contigs[chrom] += 1
            alleles = alt.split(',')
            counts['snp_records' if len(ref) == 1 and all(len(a) == 1 for a in alleles) else 'indel_records'] += 1
            hits = {}
            for bucket in range((pos - 1) // bin_size, (pos + len(ref) - 2) // bin_size + 1):
                for gene in bins[(chrom, bucket)]:
                    if gene[2] <= pos + len(ref) - 1 and gene[3] >= pos:
                        hits[gene[0]] = gene
            counts['gene_overlapping_records' if hits else 'outside_gene_records'] += 1
            gene_counts.update(hits.keys())
            fmt = dict(zip(fields[8].split(':'), fields[9].split(':'))) if len(fields) > 9 else {}
            row = [chrom, pos, ref, alt, qual, fmt.get('DP', ''), ';'.join(sorted(hits)), ';'.join(hits[k][1] for k in sorted(hits))]
            writer.writerow(row)
            if hits:
                candidates.append(row)
    candidates.sort(key=lambda row: (-float(row[4]), row[0], row[1]))
    # Keep one locus per gene to make the initial review list useful.
    selected, seen = [], set()
    for row in candidates:
        ids = set(row[6].split(';'))
        if not ids & seen:
            selected.append(row)
            seen.update(ids)
        if len(selected) == 10:
            break
    with (args.output / 'candidate_loci.tsv').open('w', newline='') as out:
        writer = csv.writer(out, delimiter='\t')
        writer.writerow(columns)
        writer.writerows(selected)
    summary = dict(counts)
    summary.update(samples=samples, annotation_genes=len(genes), genes_with_variants=len(gene_counts), contigs_with_variants=len(contigs),
                   overlap_definition='VCF REF span intersects GFF gene interval, inclusive coordinates; not a functional effect prediction',
                   inputs={str(p): sha256(p) for p in (args.vcf, args.reference, args.gff, Path(str(args.reference) + '.fai'))})
    (args.output / 'input_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'inputs'}, indent=2))


if __name__ == '__main__':
    main()
