"""Optional bounded prefetch; the Makefile can also download each sample itself."""
import argparse
import concurrent.futures
import json
from pathlib import Path
from workflow import design, get_reads

p=argparse.ArgumentParser()
p.add_argument('--samples',nargs='+',required=True)
p.add_argument('--output',type=Path,default=Path('output'))
p.add_argument('--workers',type=int,default=2)
a=p.parse_args()
rows=[r for r in design('design.csv') if r['sample_id'] in a.samples]
assert len(rows)==len(a.samples)
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
    futures={pool.submit(get_reads,row,a.output/row['sample_id']):row['sample_id'] for row in rows}
    failures={}
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as error:
            failures[futures[future]]=str(error)
            print(f'{futures[future]} failed: {error}',flush=True)
    if failures:
        raise RuntimeError(json.dumps(failures))
