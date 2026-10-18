"""Percent-encode embedded transcript-ID pipes so each SnpEff ANN has 16 fields."""
import sys
import argparse
from pathlib import Path
from urllib.parse import unquote


def repair(entry, pseudogenes=frozenset()):
    fields = entry.split('|')
    if len(fields) < 16:
        raise ValueError(f'ANN has fewer than 16 fields: {entry}')
    # This NCBI GFF uses pipes in Feature_ID, e.g. rna-gnl|WGS:ABEU|Pp3c...
    # Preserve the six leading fields and nine trailing fields unambiguously.
    delimiter_changed = len(fields) > 16
    if delimiter_changed:
        left = entry.split('|', 6)
        if left[5] != 'transcript':
            raise ValueError(f'Unexpected embedded delimiters outside a transcript ID: {entry}')
        right = left[6].rsplit('|', 9)
        if len(right) != 10:
            raise ValueError(f'Cannot locate ANN transcript fields: {entry}')
        fields = left[:6] + [right[0].replace('|', '%7C')] + right[1:]
    biotype_changed = False
    if fields[4] in pseudogenes or unquote(fields[6]) in pseudogenes:
        biotype_changed = fields[7] != 'pseudogene'
        fields[7] = 'pseudogene'
    assert len(fields) == 16
    return '|'.join(fields), delimiter_changed, biotype_changed


def gff_pseudogenes(path):
    ids, parents = set(), {}
    with path.open() as handle:
        for line in handle:
            if line.startswith('#'):
                continue
            f = line.rstrip().split('\t')
            if len(f) != 9 or f[2] not in ('gene', 'pseudogene', 'mRNA', 'transcript', 'ncRNA', 'tRNA', 'rRNA'):
                continue
            attrs = dict(item.split('=', 1) for item in f[8].split(';') if '=' in item)
            feature_id = unquote(attrs.get('ID', ''))
            if not feature_id:
                continue
            if f[2] == 'pseudogene' or attrs.get('pseudo') == 'true' or attrs.get('gene_biotype') == 'pseudogene':
                ids.add(feature_id)
            parents[feature_id] = [unquote(v) for v in attrs.get('Parent', '').split(',')]
    for feature_id, parent_ids in parents.items():
        if any(parent in ids for parent in parent_ids):
            ids.add(feature_id)
    return ids


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gff', type=Path)
    args = parser.parse_args()
    pseudogenes = gff_pseudogenes(args.gff) if args.gff else set()
    changed = total = biotypes = 0
    recorded = bio_recorded = False
    for line in sys.stdin:
        if line.startswith('##week8_ANN_feature_id_encoding='):
            recorded = True
        if line.startswith('##week8_GFF_pseudogene_biotypes='):
            bio_recorded = True
        if line.startswith('#CHROM') and not recorded:
            print('##week8_ANN_feature_id_encoding=percent_encoded_embedded_pipe_characters')
        if line.startswith('#CHROM') and args.gff and not bio_recorded:
            print('##week8_GFF_pseudogene_biotypes=NCBI_GFF_pseudo_attributes_and_pseudogene_features')
        if line.startswith('#'):
            sys.stdout.write(line)
            continue
        columns = line.rstrip('\n').split('\t')
        info = columns[7].split(';')
        for i, item in enumerate(info):
            if not item.startswith('ANN='):
                continue
            annotations = []
            for entry in item[4:].split(','):
                fixed, was_changed, bio_changed = repair(entry, pseudogenes)
                annotations.append(fixed)
                changed += was_changed
                biotypes += bio_changed
                total += 1
            info[i] = 'ANN=' + ','.join(annotations)
        columns[7] = ';'.join(info)
        print('\t'.join(columns))
    print(f'Validated {total} ANN entries; percent-encoded transcript-ID delimiters in {changed} entries; restored GFF pseudogene biotypes in {biotypes} entries', file=sys.stderr)


if __name__ == '__main__':
    main()
