"""Exit successfully only for complete, checksum-verified matching read subsets."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('directory', type=Path)
p.add_argument('run')
p.add_argument('pairs', type=int)
a = p.parse_args()
try:
    manifest = json.loads((a.directory / 'download.json').read_text())
    assert manifest['run'] == a.run and manifest['pairs'] == a.pairs
    assert len(manifest['mates']) == 2
    assert manifest['mates'][0]['read_id_sha256'] == manifest['mates'][1]['read_id_sha256']
    for mate in manifest['mates']:
        path = a.directory / f'{a.run}_{mate["mate"]}.fastq.gz'
        digest = hashlib.sha256()
        with path.open('rb') as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b''):
                digest.update(block)
        assert digest.hexdigest() == mate['sha256']
except (OSError, ValueError, KeyError, AssertionError):
    raise SystemExit(1)
