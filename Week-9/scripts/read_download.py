"""Retry interrupted FASTQ transfers and checkpoint completed mates independently."""
import gzip
import hashlib
import json
import time
from pathlib import Path
from range_stream import RangeStream


def download_mate(row,mate,out,sha):
    target=out/f'read{mate}.fastq.gz'
    cache=out/f'read{mate}.json'
    signature={'sample_id':row['sample_id'],'url':row[f'read{mate}'],
               'records':int(row['pairs']),'source_bytes':int(row[f'read{mate}_bytes'])}
    if cache.exists() and target.exists():
        old=json.loads(cache.read_text())
        if all(old.get(k)==v for k,v in signature.items()) and sha(target)==old['sha256']:
            print(f'{row["sample_id"]}: reuse completed mate {mate}',flush=True)
            return old
    for attempt in range(1,4):
        temporary=Path(str(target)+'.part')
        digest=hashlib.sha256()
        bases=0
        try:
            print(f'{row["sample_id"]}: downloading mate {mate}, attempt {attempt}',flush=True)
            with RangeStream(signature['url'],signature['source_bytes']) as remote, \
                 gzip.GzipFile(fileobj=remote) as source, temporary.open('wb') as raw, \
                 gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0,compresslevel=1) as dest:
                for record in range(signature['records']):
                    head,seq,plus,qual=[source.readline() for _ in range(4)]
                    if not head.startswith(b'@') or not plus.startswith(b'+') or not qual.endswith(b'\n') or len(seq.rstrip())!=len(qual.rstrip()):
                        raise ValueError('Incomplete or malformed FASTQ')
                    read_id=head.split()[0].removesuffix(b'/1').removesuffix(b'/2')
                    digest.update(read_id+b'\n');bases+=len(seq.rstrip())
                    dest.write(head+seq+plus+qual)
                    if (record+1)%1000000==0:
                        print(f'{row["sample_id"]} mate {mate}: {record+1:,} records',flush=True)
            temporary.replace(target)
            result=dict(signature,mate=mate,name=target.name,sha256=sha(target),id_sha256=digest.hexdigest(),bases=bases)
            temp=cache.with_suffix('.tmp')
            temp.write_text(json.dumps(result,indent=2)+'\n');temp.replace(cache)
            return result
        except Exception as error:
            print(f'{row["sample_id"]} mate {mate}, attempt {attempt} failed: {error}',flush=True)
            if attempt==3:
                raise
            time.sleep(2*attempt)
