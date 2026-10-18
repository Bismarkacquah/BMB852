"""Download synchronized first-N read pairs using archived ENA metadata."""
import argparse
import concurrent.futures
import csv
import gzip
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'Week-7' / 'scripts'))
from download_subset import RangeStream, sha256


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', required=True)
    p.add_argument('--pairs', type=int, required=True)
    p.add_argument('--metadata', type=Path, default=Path('provenance/study-runs.tsv'))
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.pairs < 1:
        p.error('--pairs must be positive')
    with a.metadata.open() as handle:
        matches = [r for r in csv.DictReader(handle, delimiter='\t') if r['run_accession'] == a.run]
    if len(matches) != 1:
        raise ValueError('Expected exactly one ENA metadata row')
    row = matches[0]
    urls = row['fastq_ftp'].split(';')
    sizes = list(map(int, row['fastq_bytes'].split(';')))
    if len(urls) != 2 or row['library_layout'] != 'PAIRED':
        raise ValueError('Expected two paired FASTQ files')
    a.output.mkdir(parents=True, exist_ok=True)

    def download(mate):
        url = 'https://' + urls[mate - 1]
        target = a.output / f'{a.run}_{mate}.fastq.gz'
        temporary = Path(str(target) + '.part')
        ids = hashlib.sha256()
        with RangeStream(url, sizes[mate - 1]) as remote, gzip.GzipFile(fileobj=remote) as source, temporary.open('wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, compresslevel=1, mtime=0) as output:
            for i in range(a.pairs):
                header, seq, plus, qual = [source.readline() for _ in range(4)]
                if not header.startswith(b'@') or not plus.startswith(b'+') or not qual or len(seq.rstrip()) != len(qual.rstrip()):
                    raise ValueError(f'Malformed FASTQ in {a.run} mate {mate} at record {i + 1}')
                name = header.split()[0]
                if name.endswith((b'/1', b'/2')):
                    name = name[:-2]
                ids.update(name + b'\n')
                output.write(header + seq + plus + qual)
                if (i + 1) % 1000000 == 0:
                    print(f'{a.run} mate {mate}: {i + 1:,} reads', flush=True)
        temporary.replace(target)
        return dict(mate=mate, records=a.pairs, url=url, path=str(target), read_id_sha256=ids.hexdigest(), sha256=sha256(target))

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        mates = list(pool.map(download, (1, 2)))
    if mates[0]['read_id_sha256'] != mates[1]['read_id_sha256']:
        raise ValueError('Paired read identifiers differ')
    (a.output / 'download.json').write_text(json.dumps(dict(run=a.run, sample=row['sample_accession'], title=row['sample_title'], pairs=a.pairs, selection='first N paired records; not random sampling', mates=mates), indent=2) + '\n')


if __name__ == '__main__':
    main()
