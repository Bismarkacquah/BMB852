"""Design-driven read subsets, exact reference download, and VCF verification.

Only Python standard-library modules are used. No software is installed.
"""
import argparse
import csv
import concurrent.futures
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path
from range_stream import RangeStream
from read_download import download_mate

REFERENCE_SHA = 'eda3922af8c6711133b05f3261118e5d75adebd3aebc8d47cb9e4cd8b11bc3b4'
BASE = 'https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/002/425/GCA_000002425.2_Phypa_V3/'


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def design(path):
    with open(path, newline='', encoding='utf-8-sig') as handle:
        rows = list(csv.DictReader(handle, delimiter=',' if str(path).endswith('.csv') else '\t'))
    if len(rows) < 2:
        raise ValueError('Design must contain at least two samples for merge')
    seen = set()
    for row in rows:
        sample = row['sample_id']
        if not re.fullmatch(r'[A-Za-z0-9_-]+', sample) or sample in seen:
            raise ValueError(f'Invalid or duplicate sample_id: {sample}')
        seen.add(sample)
        if int(row['pairs']) < 1 or row['ploidy'] not in ('1', '2'):
            raise ValueError(f'Invalid pairs/ploidy for {sample}')
        if int(row['bwa_batch_bases']) < 1:
            raise ValueError(f'Invalid BWA batch size for {sample}')
        for mate in ('read1', 'read2'):
            if not row[mate].startswith('https://'):
                raise ValueError(f'{sample}: public HTTPS FASTQ URL required')
    return rows


def get_reads(row, out):
    out.mkdir(parents=True, exist_ok=True)
    if (out/'reused-bam.json').exists():
        reuse = json.loads((out/'reused-bam.json').read_text())
        if reuse['sample'] != row['sample_id'] or reuse['pairs'] != int(row['pairs']):
            raise ValueError('Reused BAM does not match design sample/depth')
        if sha(out/'aligned.bam') != reuse['bam_sha256']:
            raise ValueError('Reused BAM checksum mismatch')
        subprocess.run(['samtools', 'quickcheck', str(out/'aligned.bam')], check=True)
        print(f'{row["sample_id"]}: verified recorded pre-existing alignment', flush=True)
        return
    manifest = out/'reads.json'
    if manifest.exists():
        old = json.loads(manifest.read_text())
        read_keys=('sample_id','read1','read2','pairs','read1_bytes','read2_bytes')
        if all(old['design'].get(k)==row.get(k) for k in read_keys) and all((out/name).exists() and sha(out/name) == value
                                       for name, value in old['sha256'].items()):
            return
    def download(mate):
        return download_mate(row,mate,out,sha)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        mates = list(pool.map(download, (1, 2)))
    if mates[0]['id_sha256'] != mates[1]['id_sha256']:
        raise ValueError('Mate IDs are not synchronized')
    manifest.write_text(json.dumps({'design': row, 'id_sha256': mates[0]['id_sha256'], 'sha256': {m['name']:m['sha256'] for m in mates}, 'mates':mates}, indent=2)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['list', 'validate', 'ploidy', 'batch-bases', 'reference', 'reads', 'parameters', 'summarize'])
    p.add_argument('--design', default='design.csv')
    p.add_argument('--reference')
    p.add_argument('--sample')
    p.add_argument('--output')
    p.add_argument('--threads', type=int)
    a = p.parse_args()
    if a.action == 'reference':
        target = Path(a.reference)
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = Path(str(target)+'.part')
        with urllib.request.urlopen(BASE+'GCA_000002425.2_Phypa_V3_genomic.fna.gz', timeout=120) as remote, gzip.GzipFile(fileobj=remote) as source, temp.open('wb') as dest:
            shutil.copyfileobj(source, dest)
        if sha(temp) != REFERENCE_SHA:
            raise ValueError('Downloaded reference checksum mismatch')
        temp.replace(target)
        return
    if a.action == 'parameters':
        if sha(a.reference) != REFERENCE_SHA:
            raise ValueError('Reference differs from Week 7 assembly sequence')
        target = Path(a.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps({'reference_sha256': REFERENCE_SHA, 'threads': a.threads,
                           'min_MQ': 20, 'min_BQ': 20, 'min_QUAL': 20, 'min_DP': 3,
                           'trim_quality':'20,20', 'trim_min_length':30,
                           'adapters':['AGATCGGAAGAGCACACGTCTGAACTCCAGTCA','AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT']}, indent=2)+'\n'
        if not target.exists() or target.read_text() != text:
            target.write_text(text)
        return
    rows = design(a.design)
    if a.action == 'list':
        print(' '.join(r['sample_id'] for r in rows))
    elif a.action == 'validate':
        print(f'Validated {len(rows)} unique samples')
    elif a.action in ('reads', 'ploidy', 'batch-bases'):
        row = next(r for r in rows if r['sample_id'] == a.sample)
        if a.action == 'ploidy':
            print(row['ploidy'])
        elif a.action == 'batch-bases':
            print(row['bwa_batch_bases'])
        else:
            get_reads(row, Path(a.output))
    elif a.action == 'summarize':
        out = Path(a.output)
        merged = out/'merged.vcf.gz'
        samples = subprocess.check_output(['bcftools', 'query', '-l', str(merged)], text=True).splitlines()
        if samples != [r['sample_id'] for r in rows]:
            raise ValueError('Merged sample order does not match design')
        union = set()
        expected = {}
        counts = []
        for i, row in enumerate(rows):
            count = 0
            with gzip.open(out/row['sample_id']/'calls.vcf.gz', 'rt') as handle:
                for line in handle:
                    if line.startswith('#'):
                        continue
                    f = line.rstrip().split('\t')
                    key = tuple(f[:2]+[f[3].upper(), f[4].upper()])
                    union.add(key)
                    expected[key, i] = f[9].split(':')[f[8].split(':').index('GT')]
                    count += 1
            counts.append((row['sample_id'], row['label'], row['pairs'], count))
        observed = set()
        with gzip.open(merged, 'rt') as handle:
            for line in handle:
                if line.startswith('#'):
                    continue
                f = line.rstrip().split('\t')
                key = tuple(f[:2]+[f[3].upper(), f[4].upper()])
                observed.add(key)
                gi = f[8].split(':').index('GT')
                for i, value in enumerate(f[9:]):
                    gt = value.split(':')[gi]
                    original = expected.get((key, i))
                    if (original is not None and gt != original) or (original is None and gt not in ('.', './.', '.|.')):
                        raise ValueError('Merged genotype changed or missing call became reference')
        if observed != union:
            raise ValueError('Merged allele union differs from sample VCFs')
        with (out/'summary.tsv').open('w') as handle:
            handle.write('sample_id\tlabel\tread_pairs\tretained_variants\n')
            for row in counts:
                handle.write('\t'.join(map(str, row))+'\n')
        (out/'validation.json').write_text(json.dumps({'samples': samples, 'merged_records': len(observed), 'exact_union_verified': True, 'genotypes_verified': True}, indent=2)+'\n')
        versions = {}
        for tool in ('samtools', 'bcftools'):
            versions[tool] = subprocess.check_output([tool, '--version'], text=True).splitlines()[0]
        (out/'versions.json').write_text(json.dumps(versions, indent=2)+'\n')
        print(f'Validated {len(samples)} samples and {len(observed)} merged alleles')


if __name__ == '__main__':
    main()
