"""Fetch only missing matching NCBI reference files; never replace existing data."""
import argparse
import gzip
import shutil
import urllib.request
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--reference', type=Path, required=True)
p.add_argument('--gff', type=Path, required=True)
a = p.parse_args()
assembly = 'GCA_000002425.2_Phypa_V3'
base = f'https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/002/425/{assembly}'
for target, suffix in ((a.reference, 'genomic.fna.gz'), (a.gff, 'genomic.gff.gz')):
    if target.is_file() and target.stat().st_size:
        print(f'Reuse existing file: {target}')
        continue
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(str(target) + '.part')
    url = f'{base}/{assembly}_{suffix}'
    print(f'Download {url}', flush=True)
    with urllib.request.urlopen(url, timeout=120) as remote, gzip.GzipFile(fileobj=remote) as source, temporary.open('wb') as out:
        shutil.copyfileobj(source, out, length=1024*1024)
    temporary.replace(target)
