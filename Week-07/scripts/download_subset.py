"""Stream the first N records of each ENA mate file into deterministic gzip files."""
import argparse
import concurrent.futures
import gzip
import hashlib
import json
import time
import urllib.request
from pathlib import Path


class RangeStream:
    """Read ordered HTTP byte ranges while prefetching a bounded number of chunks."""
    def __init__(self, url, total, block=8 * 1024 * 1024, workers=4):
        self.url, self.total, self.block = url, total, block
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
        self.next_offset = 0
        self.pending = []
        self.buffer = b''
        self.position = 0
        for _ in range(workers):
            self.schedule()

    def schedule(self):
        if self.next_offset < self.total:
            start = self.next_offset
            end = min(start + self.block, self.total) - 1
            self.next_offset = end + 1
            self.pending.append(self.pool.submit(self.fetch, start, end))

    def fetch(self, start, end):
        request = urllib.request.Request(self.url, headers={'Range': f'bytes={start}-{end}'})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    expected = f'bytes {start}-{end}/{self.total}'
                    if response.status != 206 or response.headers.get('Content-Range') != expected:
                        raise ValueError('Server did not return the requested byte range')
                    data = response.read()
                    if len(data) != end - start + 1:
                        raise ValueError('Incomplete HTTP byte range')
                    return data
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2)

    def read(self, size=-1):
        if size < 0:
            raise ValueError('Unbounded remote reads are disabled')
        pieces = []
        while size:
            if self.position == len(self.buffer):
                if not self.pending:
                    break
                self.buffer = self.pending.pop(0).result()
                self.position = 0
                self.schedule()
            count = min(size, len(self.buffer) - self.position)
            pieces.append(self.buffer[self.position:self.position + count])
            self.position += count
            size -= count
        return b''.join(pieces)

    def __enter__(self):
        return self

    def __exit__(self, *unused):
        self.pool.shutdown(wait=True, cancel_futures=True)


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def download(mate, pairs, directory):
    url = f'https://ftp.sra.ebi.ac.uk/vol1/fastq/ERR898/005/ERR8982185/ERR8982185_{mate}.fastq.gz'
    target = directory / f'ERR8982185_{mate}.fastq.gz'
    temporary = target.with_suffix(target.suffix + '.part')
    for attempt in range(1, 4):
        try:
            ids = hashlib.sha256()
            bases = 0
            total_bytes = {1: 5066704787, 2: 5548594672}[mate]
            with RangeStream(url, total_bytes) as response, \
                    gzip.GzipFile(fileobj=response) as source, temporary.open('wb') as raw, \
                    gzip.GzipFile(filename='', mode='wb', fileobj=raw, compresslevel=1, mtime=0) as output:
                for record in range(1, pairs + 1):
                    header, seq, plus, qual = [source.readline() for _ in range(4)]
                    if not header.startswith(b'@') or not plus.startswith(b'+') or not qual:
                        raise ValueError(f'Mate {mate}: incomplete FASTQ at record {record}')
                    if len(seq.rstrip()) != len(qual.rstrip()):
                        raise ValueError(f'Mate {mate}: sequence/quality length mismatch at {record}')
                    name = header.split()[0]
                    if name.endswith((b'/1', b'/2')):
                        name = name[:-2]
                    ids.update(name + b'\n')
                    bases += len(seq.rstrip())
                    output.write(header + seq + plus + qual)
                    if record % 1000000 == 0:
                        print(f'Mate {mate}: {record:,} reads downloaded', flush=True)
            temporary.replace(target)
            return dict(mate=mate, url=url, records=pairs, bases=bases,
                        read_id_sha256=ids.hexdigest(), path=str(target),
                        compressed_sha256=sha256(target), compressed_bytes=target.stat().st_size)
        except Exception as error:
            print(f'Mate {mate}, attempt {attempt}: {error}', flush=True)
            if attempt == 3:
                raise
            time.sleep(2 * attempt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', required=True, type=int)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    args = parser.parse_args()
    if args.pairs <= 0:
        parser.error('--pairs must be positive')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(download, mate, args.pairs, args.output_dir) for mate in (1, 2)]
        results = [future.result() for future in futures]
    if results[0]['read_id_sha256'] != results[1]['read_id_sha256']:
        raise ValueError('Mate read identifiers differ: paired inputs are not synchronized')
    args.manifest.write_text(json.dumps(dict(run='ERR8982185', pairs=args.pairs,
                                           selection='first N records of each ENA mate file',
                                           transfer='ordered HTTP byte ranges, four workers per mate',
                                           mates=results), indent=2) + '\n')
    print(f'Finished: {args.pairs:,} synchronized read pairs', flush=True)
