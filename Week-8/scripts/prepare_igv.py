"""Prepare real five-sample IGV views, local sessions, and locus-level pileups."""
import argparse
import json
import subprocess
from pathlib import Path
from urllib.parse import unquote

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--reference', type=Path, required=True)
p.add_argument('--gff', type=Path, required=True)
p.add_argument('--igv-root', help='Repository root as seen by Windows IGV, e.g. C:/path/BMB852')
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
selected = json.loads((root / 'results/igv_selected_variants.json').read_text())
runs = [f'ERR898218{i}' for i in range(3, 8)]
igv = root / 'igv'
igv.mkdir(exist_ok=True)
(root / 'png').mkdir(exist_ok=True)
(root / 'results/pileups').mkdir(exist_ok=True)


def display_path(path):
    resolved = path.resolve()
    if a.igv_root:
        return a.igv_root.rstrip('/').replace('\\', '/') + '/' + resolved.relative_to(root.parent).as_posix()
    return resolved.as_posix()


bams = {s: root / f'samples/{s}/{s}.sorted.bam' for s in runs}
bams['ERR8982185'] = root.parent / 'Week-7/expanded/bam/ERR8982185.20M.sorted.bam'
# Use the rebuilt Week 8 BAM if a different PAIRS setting generated one.
if (root / 'samples/ERR8982185/ERR8982185.sorted.bam').exists():
    bams['ERR8982185'] = root / 'samples/ERR8982185/ERR8982185.sorted.bam'
for bam in bams.values():
    if not bam.is_file() or not Path(str(bam) + '.bai').is_file():
        raise FileNotFoundError(f'BAM or index missing: {bam}')

# Extract compact BED12 transcript models around selected loci for IGV.
transcripts, exons = {}, {}
products = {}
with a.gff.open() as handle:
    for line in handle:
        if line.startswith('#'):
            continue
        f = line.rstrip().split('\t')
        if len(f) != 9 or not any(f[0] == c['chrom'] and int(f[3]) <= c['pos'] + 5000 and int(f[4]) >= c['pos'] - 5000 for c in selected):
            continue
        attrs = dict(item.split('=', 1) for item in f[8].split(';') if '=' in item)
        if f[2] in ('mRNA', 'transcript', 'ncRNA', 'tRNA', 'rRNA') and 'ID' in attrs:
            name = unquote(attrs.get('Name', attrs['ID']))
            transcripts[attrs['ID']] = (f[0], int(f[3])-1, int(f[4]), name, f[6])
            products[unquote(attrs['ID'])] = unquote(attrs.get('product', 'not supplied in GFF'))
        elif f[2] == 'exon':
            for parent in attrs.get('Parent', '').split(','):
                exons.setdefault(parent, []).append((int(f[3])-1, int(f[4])))
with (root / 'results/igv_genes.bed').open('w') as handle:
    for name, (chrom, start, end, label, strand) in sorted(transcripts.items(), key=lambda item: (item[1][0], item[1][1])):
        blocks = sorted(set(exons.get(name, [(start, end)])))
        # Only complete exons within the transcript are valid BED blocks.
        blocks = [(s, e) for s, e in blocks if start <= s < e <= end]
        if not blocks:
            continue
        sizes = ','.join(str(e-s) for s, e in blocks)
        offsets = ','.join(str(s-start) for s, e in blocks)
        handle.write(f'{chrom}\t{start}\t{end}\t{label}\t0\t{strand}\t{start}\t{start}\t38,102,128\t{len(blocks)}\t{sizes}\t{offsets}\n')
(root / 'results/selected_gene_products.json').write_text(json.dumps({c['transcript']: products.get(c['transcript'], 'not supplied in GFF') for c in selected}, indent=2) + '\n')

commands = ['new', 'setSleepInterval 1000', f'genome {display_path(a.reference)}',
            f'snapshotDirectory {display_path(root / "png")}',
            f'load {display_path(root / "results/five_samples.annotated.vcf.gz")}',
            f'load {display_path(root / "results/igv_genes.bed")}',
            'maxPanelHeight 2400', 'setSequenceShowTranslation false', 'expand',
            'setTrackHeight 180 igv_genes.bed']
first = selected[0]
commands += [f'goto {first["chrom"]}:{max(1, first["pos"]-100)}-{first["pos"]+100}', 'snapshot 05_five_sample_genotypes.png']
for bam in bams.values():
    commands += [f'load {display_path(bam)}']
commands += ['expand', 'colorBy READ_STRAND', 'scrollToTop']
for bam in bams.values():
    commands += [f'setTrackHeight 240 {bam.name}']
for i, candidate in enumerate(selected, 1):
    chrom, pos = candidate['chrom'], candidate['pos']
    locus = f'{chrom}:{max(1, pos-40)}-{pos+40}'
    commands += [f'goto {locus}', f'sort BASE {chrom}:{pos}', f'snapshot 06_candidate_{i}.png']
    if not a.igv_root:
        for run, bam in bams.items():
            with (root / f'results/pileups/candidate_{i}_{run}.tsv').open('w') as out:
                subprocess.run(['samtools', 'mpileup', '-B', '-q', '20', '-Q', '20', '-f', str(a.reference), '-r', locus, str(bam)], stdout=out, check=True)
commands += [f'goto {first["chrom"]}:{max(1, first["pos"]-2500)}-{first["pos"]+2500}',
             'snapshot 07_regional_coverage.png',
             f'goto {first["chrom"]}:{max(1, first["pos"]-40)}-{first["pos"]+40}',
             f'saveSession {display_path(igv / "five_samples.session.xml")}', 'exit']
batch = igv / ('five_samples.windows.batch.txt' if a.igv_root else 'five_samples.batch.txt')
batch.write_text('\n'.join(commands) + '\n')
print(batch)
