"""Design-driven moss H3K4me3 peak calling; external tools are never installed here."""
import argparse
import concurrent.futures
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from range_stream import RangeStream

REFERENCE_URL = 'https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/002/425/GCA_000002425.2_Phypa_V3/GCA_000002425.2_Phypa_V3_genomic.fna.gz'
REFERENCE_SHA = 'eda3922af8c6711133b05f3261118e5d75adebd3aebc8d47cb9e4cd8b11bc3b4'
GSIZE = 330000000  # Approximate effective size: 70% of the 471.85-Mb assembly.
ROOT = Path(__file__).resolve().parents[1]
DESIGN_COLUMNS = ('sample_id', 'group', 'replicate', 'role', 'assay', 'mark', 'background', 'bioproject', 'organism', 'layout', 'reads', 'fastq_url', 'source_bytes')
PROJECT = 'PRJDB7369'


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def design(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames and len(reader.fieldnames) == len(set(reader.fieldnames)), 'Missing or duplicate CSV headers'
        assert set(DESIGN_COLUMNS) <= set(reader.fieldnames), 'Missing required design columns'
        rows = list(reader)
    assert rows, 'Empty design'
    ids = [r['sample_id'] for r in rows]
    assert len(ids) == len(set(ids)), 'Duplicate sample IDs'
    assert len({r['fastq_url'] for r in rows}) == len(rows), 'A read library is listed more than once'
    assert {r['bioproject'] for r in rows} == {PROJECT}, 'Use the selected moss BioProject'
    by_id = {r['sample_id']: r for r in rows}
    replicate_keys = set()
    groups = {}
    for r in rows:
        assert re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', r['sample_id']), 'Unsafe sample ID'
        assert r['assay'] == 'ChIP_seq' and r['layout'] == 'SINGLE'
        assert r['organism'] == 'Physcomitrium_patens'
        assert int(r['reads']) > 0 and int(r['source_bytes']) > 0
        assert int(r['replicate']) > 0, 'Replicate must be a positive integer'
        key = (r['group'], int(r['replicate']), r['role'])
        assert key not in replicate_keys, 'Duplicate group/replicate/role assignment'
        replicate_keys.add(key)
        assert r['fastq_url'].startswith('https://ftp.sra.ebi.ac.uk/')
        assert r['role'] in ('background', 'signal')
        for key in ('sample_id', 'group', 'role', 'assay', 'mark', 'bioproject', 'organism', 'layout'):
            assert re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', r[key]), f'Invalid label in {key}'
        if r['role'] == 'background':
            assert r['mark'] == 'H3' and not r['background'], 'Background rows must be total H3 without a background link'
        if r['role'] == 'signal':
            b = by_id[r['background']]
            assert b['role'] == 'background' and b['mark'] == 'H3'
            assert b['group'] == r['group'] and b['replicate'] == r['replicate']
            assert r['mark'] == 'H3K4me3'
            groups.setdefault(r['group'], []).append(r['replicate'])
    assert len(groups) == 2 and all(len(set(v)) >= 2 for v in groups.values()), 'Need two replicates in both groups'
    return rows


def build_design(path):
    """Reconstruct the selected eight moss libraries from ENA run metadata."""
    fields = 'run_accession,study_accession,sample_title,library_strategy,library_layout,fastq_ftp,fastq_bytes,read_count'
    url = f'https://www.ebi.ac.uk/ena/portal/api/filereport?accession={PROJECT}&result=read_run&fields={fields}&format=tsv'
    with urllib.request.urlopen(url, timeout=60) as response:
        records = list(csv.DictReader(response.read().decode('utf-8-sig').splitlines(), delimiter='\t'))
    selected = []
    for source in records:
        title = source['sample_title']
        mark = re.search(r'anti-(H3K4me3|H3) antibody', title)
        group = re.search(r'\((DMSO|Estradiol)\)', title)
        rep = re.search(r'replicate ([12])(?:$|\D)', title)
        if not (mark and group and rep):
            continue
        assert source['study_accession'] == PROJECT
        assert source['library_strategy'].lower() == 'chip-seq' and source['library_layout'] == 'SINGLE'
        assert ';' not in source['fastq_ftp'] and int(source['read_count']) >= 2000000
        selected.append(dict(sample_id=source['run_accession'], group=group[1], replicate=rep[1],
            role='background' if mark[1] == 'H3' else 'signal', assay='ChIP_seq', mark=mark[1],
            background='', bioproject=PROJECT, organism='Physcomitrium_patens', layout='SINGLE',
            reads='2000000', fastq_url='https://'+source['fastq_ftp'], source_bytes=source['fastq_bytes']))
    expected = {(g, str(r), m) for g in ('DMSO','Estradiol') for r in (1,2) for m in ('H3','H3K4me3')}
    assert len(selected) == 8 and {(r['group'],r['replicate'],r['mark']) for r in selected} == expected, 'Unexpected source metadata; review before rebuilding design'
    backgrounds = {(r['group'],r['replicate']):r['sample_id'] for r in selected if r['role']=='background'}
    for row in selected:
        if row['role']=='signal':
            row['background'] = backgrounds[row['group'],row['replicate']]
    path = Path(path)
    temporary = path.with_name(path.name+'.part')
    with temporary.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=DESIGN_COLUMNS, lineterminator='\n')
        writer.writeheader()
        writer.writerows(sorted(selected, key=lambda r:r['sample_id']))
    design(temporary)
    if path.exists() and path.read_bytes() == temporary.read_bytes():
        temporary.unlink()
        print(f'{path}: ENA metadata reproduces the existing design exactly')
    else:
        temporary.replace(path)
        print(f'{path}: wrote eight validated moss ChIP-seq libraries from ENA')


def run(args, **kwargs):
    print('+', ' '.join(map(str, args)), flush=True)
    return subprocess.run(list(map(str, args)), check=True, **kwargs)


def capture(args):
    return subprocess.check_output(list(map(str, args)), text=True)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def reference(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.part')
    with urllib.request.urlopen(REFERENCE_URL, timeout=120) as response, gzip.GzipFile(fileobj=response) as src, temp.open('wb') as dest:
        shutil.copyfileobj(src, dest)
    assert sha(temp) == REFERENCE_SHA, 'Reference checksum mismatch'
    temp.replace(path)


def reads(row, folder):
    target = folder/'reads.fastq.gz'
    signature = {k: row[k] for k in ('sample_id', 'fastq_url', 'reads', 'source_bytes')}
    manifest = folder/'reads.json'
    if target.exists() and manifest.exists():
        old = json.loads(manifest.read_text())
        if old['signature'] == signature and sha(target) == old['sha256']:
            return target
    # A larger completed prefix can supply a smaller run without redownloading.
    if target.exists() and manifest.exists():
        old = json.loads(manifest.read_text())
        previous = old['signature']
        if all(previous[k] == signature[k] for k in ('sample_id', 'fastq_url', 'source_bytes')) and int(previous['reads']) > int(row['reads']) and sha(target) == old['sha256']:
            temp = target.with_suffix('.part')
            with gzip.open(target, 'rb') as src, gzip.open(temp, 'wb', compresslevel=1) as dest:
                for _ in range(int(row['reads'])):
                    h, s, p, q = [src.readline() for _ in range(4)]
                    assert h.startswith(b'@') and p.startswith(b'+') and q.endswith(b'\n') and len(s.strip()) == len(q.strip())
                    dest.write(h+s+p+q)
            temp.replace(target)
            write_json(manifest, {'signature': signature, 'sha256': sha(target)})
            return target
    # Bounded HTTP ranges let us stop after the requested prefix of a large run.
    for attempt in range(3):
        try:
            temp = target.with_suffix('.part')
            with RangeStream(row['fastq_url'], int(row['source_bytes'])) as remote, gzip.GzipFile(fileobj=remote) as src, gzip.open(temp, 'wb', compresslevel=1) as dest:
                for i in range(int(row['reads'])):
                    h, s, p, q = [src.readline() for _ in range(4)]
                    assert h.startswith(b'@') and p.startswith(b'+') and q.endswith(b'\n') and len(s.strip()) == len(q.strip()), 'Invalid FASTQ'
                    dest.write(h+s+p+q)
                    if (i+1) % 1000000 == 0:
                        print(row['sample_id'], i+1, 'reads', flush=True)
            temp.replace(target)
            write_json(manifest, {'signature': signature, 'sha256': sha(target)})
            return target
        except Exception:
            if attempt == 2:
                raise


def align(row, out, ref, threads):
    folder = out/row['sample_id']
    folder.mkdir(parents=True, exist_ok=True)
    fastq = reads(row, folder)
    trimmed = folder/'trimmed.fastq.gz'
    with (folder/'trim.log').open('w') as log:
        run(['cutadapt', '-j', threads, '-a', 'AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC', '-q', '20', '-m', '25', '-o', trimmed, fastq], stdout=log, stderr=subprocess.STDOUT)
    raw = folder/'sorted.bam'
    with (folder/'align.log').open('w') as log:
        bwa = subprocess.Popen(['bwa', 'mem', '-K', '10000000', '-t', str(threads), str(ref), str(trimmed)], stdout=subprocess.PIPE, stderr=log)
        try:
            run(['samtools', 'sort', '-@', threads, '-m', '256M', '-o', raw, '-'], stdin=bwa.stdout, stderr=log)
        finally:
            bwa.stdout.close()
        assert bwa.wait() == 0, 'BWA failed'
    # Single-end libraries: remove coordinate duplicates before filtering.
    dedup = folder/'dedup.bam'
    with (folder/'dedup.log').open('w') as log:
        run(['samtools', 'markdup', '-r', '-s', raw, dedup], stderr=log)
    bam = folder/'filtered.bam'
    run(['samtools', 'view', '-b', '-q', '20', '-F', '2308', '-o', bam, dedup])
    run(['samtools', 'index', bam])
    run(['samtools', 'quickcheck', bam])
    count = int(capture(['samtools', 'view', '-c', bam]))
    assert count > 0, 'No retained reads'
    # Coverage is per-million retained read alignments; no inferred extension.
    # Stage text output on Linux storage to avoid many small writes on WSL mounts.
    with tempfile.TemporaryDirectory(prefix='moss-coverage-') as temp:
        track = Path(temp)/'coverage.bedGraph'
        with track.open('w') as f:
            run(['bedtools', 'genomecov', '-bg', '-scale', str(1000000/count), '-ibam', bam], stdout=f)
        shutil.copyfile(track, folder/(row['sample_id']+'.coverage.bedGraph'))
    write_json(folder/'metrics.json', {'sample_id': row['sample_id'], 'requested_reads': int(row['reads']), 'retained_reads': count})
    # Keep small manifest/logs and final BAM; remove reproducible intermediates.
    for p in (raw, dedup, trimmed):
        p.unlink()
    (folder/'aligned.done').touch()


def peaks(row, out):
    folder = out/row['sample_id']
    with (folder/'macs3.log').open('w') as log:
        run(['macs3', 'callpeak', '-t', folder/'filtered.bam', '-c', out/row['background']/'filtered.bam', '-f', 'BAM', '-g', GSIZE, '--nomodel', '--extsize', '150', '--keep-dup', 'all', '-q', '0.05', '-n', row['sample_id'], '--outdir', folder/'peaks'], stdout=log, stderr=subprocess.STDOUT)
    (folder/'peaks.done').touch()


def intervals(path):
    with path.open() as f:
        return [line.rstrip().split('\t') for line in f if line.strip() and not line.startswith('#')]


def overlap(a, b):
    return max(0, min(int(a[2]), int(b[2])) - max(int(a[1]), int(b[1]))) if a[0] == b[0] else 0


def report(rows, out, ref):
    result = ROOT/'results'
    result.mkdir(exist_ok=True)
    summary = []
    signal = [r for r in rows if r['role'] == 'signal']
    peaks_by_id = {}
    for r in signal:
        sid = r['sample_id']
        source = out/sid/'peaks'/f'{sid}_peaks.narrowPeak'
        ps = intervals(source)
        peaks_by_id[sid] = ps
        assert all(len(p) == 10 and 0 <= int(p[1]) < int(p[2]) for p in ps)
        shutil.copyfile(source, result/f'{sid}.narrowPeak')
        metrics = json.loads((out/sid/'metrics.json').read_text())
        summary.append([sid, r['group'], r['replicate'], int(r['reads']), metrics['retained_reads'], len(ps)])
    with (result/'summary.tsv').open('w') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(['sample', 'group', 'replicate', 'input_reads', 'retained_reads', 'peaks'])
        writer.writerows(summary)
    comparisons, regions = [], {}
    for group in dict.fromkeys(r['group'] for r in signal):
        pair = sorted([r for r in signal if r['group'] == group], key=lambda r: int(r['replicate']))[:2]
        a, b = [peaks_by_id[r['sample_id']] for r in pair]
        # Restrict interval comparisons to matching contigs.
        by_chrom = {}
        for p in b:
            by_chrom.setdefault(p[0], []).append(p)
        supported = [any(overlap(p, q) >= .5*max(int(p[2])-int(p[1]), int(q[2])-int(q[1])) for q in by_chrom.get(p[0], [])) for p in a]
        by_chrom_a = {}
        for p in a:
            by_chrom_a.setdefault(p[0], []).append(p)
        reverse = sum(any(overlap(p, q) >= .5*max(int(p[2])-int(p[1]), int(q[2])-int(q[1])) for q in by_chrom_a.get(p[0], [])) for p in b)
        comparisons.append({'group': group, 'replicate1': pair[0]['sample_id'], 'replicate2': pair[1]['sample_id'], 'peaks1': len(a), 'peaks2': len(b), 'supported1': sum(supported), 'supported2': reverse})
        if group == 'DMSO':
            agree = sorted([p for p, ok in zip(a, supported) if ok], key=lambda p: float(p[8]), reverse=True)
            disagree = sorted([p for p in a if not any(overlap(p, q) for q in by_chrom.get(p[0], []))], key=lambda p: float(p[8]), reverse=True)
            assert agree and disagree, 'No suitable agreement/disagreement regions found'
            for label, candidates in [('agreement', agree), ('disagreement', disagree)]:
                p = candidates[0]
                regions[label] = {'chrom': p[0], 'start': max(1, int(p[1])-1500), 'end': int(p[2])+1500, 'peak_start_0based': int(p[1]), 'peak_end': int(p[2]), 'group': group}
    write_json(result/'replicate_overlap.json', comparisons)
    write_json(result/'regions.json', regions)
    versions = {}
    for tool, args in {'samtools':['--version'], 'cutadapt':['--version'], 'macs3':['--version'], 'bedtools':['--version']}.items():
        versions[tool] = capture([tool]+args).splitlines()[0]
    versions['bwa'] = subprocess.run(['bwa'], capture_output=True, text=True).stderr
    versions['python'] = sys.version
    versions['reference_sha256'] = sha(ref)
    assert versions['reference_sha256'] == REFERENCE_SHA
    versions['settings'] = json.loads((out/'settings.json').read_text())
    write_json(result/'versions.json', versions)
    # Refresh measured README sections whenever a reviewer reruns the report.
    text = (ROOT/'README.md').read_text(encoding='utf-8')
    table = ['## Peak counts and replicate consistency', '',
             '| Sample | Group | Replicate | Input reads | Retained reads | Peaks |',
             '|---|---|---:|---:|---:|---:|']
    table += ['| ' + ' | '.join(str(x) if i < 3 else f'{x:,}' for i, x in enumerate(line)) + ' |' for line in summary]
    table += ['', 'Retained reads are primary alignments after coordinate-duplicate removal and MAPQ filtering. These counts use the selected read prefixes, not the full libraries.', '',
              'A peak is counted as supported when it overlaps a peak in the other replicate by at least 50% of **both** intervals. This is a descriptive overlap measure, not IDR or a differential-enrichment test.', '',
              '| Group | Replicate 1 peaks supported by replicate 2 | Replicate 2 peaks supported by replicate 1 |',
              '|---|---:|---:|']
    for c in comparisons:
        table.append(f'| {c["group"]} | {c["supported1"]:,}/{c["peaks1"]:,} ({100*c["supported1"]/max(1,c["peaks1"]):.1f}%) | {c["supported2"]:,}/{c["peaks2"]:,} ({100*c["supported2"]/max(1,c["peaks2"]):.1f}%) |')
    table += ['', 'Differences in the two percentages reflect differences in peak-set size and boundaries. They should be read alongside the local coverage evidence below.', '']
    text = re.sub(r'## Peak counts and replicate consistency\n.*?(?=## IGV comparison)', '\n'.join(table)+'\n', text, flags=re.S)
    captions = ['## IGV comparison', '', 'The following regions were selected from the DMSO peak calls. Each view contains four coverage tracks (reads per million retained alignments) and four peak tracks, with run accessions matching the design table.', '']
    for label, region in regions.items():
        title = 'Replicates agree' if label == 'agreement' else 'Replicates disagree'
        captions += [f'### {title}: {region["chrom"]}:{region["start"]:,}-{region["end"]:,}', '', f'![{title}, with coverage and peak calls for both groups](results/{label}.png)', '']
        target = f'{region["chrom"]}:{region["peak_start_0based"]+1:,}-{region["peak_end"]:,}'
        if label == 'agreement':
            captions += [f'The selected DMSO replicate 1 peak at **{target}** has a peak in DMSO replicate 2 with at least 50% reciprocal overlap. Compare both coverage profiles and the peak intervals to assess local agreement.', '']
        else:
            captions += [f'The selected DMSO replicate 1 peak at **{target}** has **no overlapping peak call** in DMSO replicate 2. This is disagreement in the called intervals; it does not imply that replicate 2 has no reads or that the mark is biologically absent.', '']
    text = re.sub(r'## IGV comparison\n.*?(?=To regenerate them)', '\n'.join(captions)+'\n', text, flags=re.S)
    (ROOT/'README.md').write_text(text, encoding='utf-8')
    (out/'summary.done').touch()
    print(json.dumps({'summary': summary, 'overlap': comparisons, 'regions': regions}, indent=2))


def igv(rows, out, ref):
    result = ROOT/'results'
    regions = json.loads((result/'regions.json').read_text())
    lines = [f'genome {ref.resolve()}', f'snapshotDirectory {result.resolve()}', 'setSleepInterval 1000']
    # Four coverage tracks and four peak tracks; backgrounds are optional locally.
    for r in rows:
        if r['role'] == 'signal':
            sid = r['sample_id']
            lines += [f'load {(out/sid/(sid+".coverage.bedGraph")).resolve()}', f'load {(result/(sid+".narrowPeak")).resolve()}']
    lines += ['maxPanelHeight 1600', 'squish', 'setDataRange 0,30']
    for r in rows:
        if r['role'] == 'signal':
            sid = r['sample_id']
            lines += [f'setTrackHeight 100 {sid}.coverage.bedGraph', f'setTrackHeight 40 {sid}.narrowPeak']
    for label, region in regions.items():
        maximum = 1.0
        for row in rows:
            if row['role'] != 'signal':
                continue
            sid = row['sample_id']
            with (out/sid/(sid+'.coverage.bedGraph')).open() as f:
                for line in f:
                    chrom, start, end, value = line.split()
                    if chrom == region['chrom'] and int(start) < region['end'] and int(end) >= region['start']:
                        maximum = max(maximum, float(value))
        lines += [f'setDataRange 0,{int(maximum*1.15)+1}']
        lines += [f'goto {region["chrom"]}:{region["start"]}-{region["end"]}', f'snapshot {label}.png']
    lines += [f'saveSession {(out/"igv-session.xml").resolve()}', 'exit']
    batch = out/'igv.batch.txt'
    batch.write_text('\n'.join(lines)+'\n')
    home = Path(os.environ['IGV_DIR'])
    java = home/'jdk-21/bin/java'
    run([java, '--module-path='+str(home/'lib'), '-Xmx2g', '@'+str(home/'igv.args'), '-Djava.net.preferIPv4Stack=true', '--module=org.igv/org.broad.igv.ui.Main', '-g', ref.resolve(), '-b', batch.resolve()])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['build-design','list','dispatch','background-for','validate','reference','settings','align','peaks','report','igv'])
    p.add_argument('--design', default='design.csv')
    p.add_argument('--role')
    p.add_argument('--sample')
    p.add_argument('--out', type=Path, default=Path('output'))
    p.add_argument('--reference', type=Path, default=Path('reference/Phypa_V3.fa'))
    p.add_argument('--threads', type=int, default=4)
    a = p.parse_args()
    assert a.threads > 0
    if a.command == 'build-design':
        build_design(a.design)
        return
    rows = design(a.design)
    if a.command == 'list':
        print(' '.join(r['sample_id'] for r in rows if not a.role or r['role'] == a.role))
    elif a.command == 'dispatch':
        writer = csv.writer(sys.stdout, lineterminator='\n')
        writer.writerow(['sample_id', 'group', 'replicate'])
        writer.writerows([r[k] for k in ('sample_id', 'group', 'replicate')] for r in rows if not a.role or r['role'] == a.role)
    elif a.command == 'background-for':
        row = next(r for r in rows if r['sample_id'] == a.sample)
        assert row['role'] == 'signal', 'Choose a signal sample'
        print(row['background'])
    elif a.command == 'validate':
        print(f'Validated {len(rows)} libraries; two signal replicates in each group with matched H3 backgrounds')
    elif a.command == 'reference':
        reference(a.reference)
    elif a.command == 'settings':
        a.out.mkdir(parents=True, exist_ok=True)
        value = {'design_sha256': sha(a.design), 'reference': str(a.reference.resolve()), 'threads': a.threads, 'gsize': GSIZE, 'qvalue': .05, 'extension': 150}
        path = a.out/'settings.json'
        if not path.exists() or json.loads(path.read_text()) != value:
            write_json(path, value)
    elif a.command in ('align', 'peaks'):
        row = next(r for r in rows if r['sample_id'] == a.sample)
        if a.command == 'align':
            align(row, a.out, a.reference, a.threads)
        else:
            assert row['role'] == 'signal'
            peaks(row, a.out)
    elif a.command == 'report':
        report(rows, a.out, a.reference)
    elif a.command == 'igv':
        igv(rows, a.out, a.reference)


if __name__ == '__main__':
    main()
