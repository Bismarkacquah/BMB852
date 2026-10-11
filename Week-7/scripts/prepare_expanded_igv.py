"""Choose supported PASS calls and generate reproducible expanded IGV views."""
import argparse
import heapq
import json
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--igv-root', help='Repository root as seen by IGV')
args = parser.parse_args()
week7 = Path(__file__).resolve().parents[1]
expanded = week7 / 'expanded'
root = args.igv_root.rstrip('/').replace('\\', '/') if args.igv_root else week7.parent.as_posix()
pass_vcf = expanded / 'results/ERR8982185.20M.pass.vcf.gz'
query = '%CHROM\t%POS\t%REF\t%ALT\t%QUAL\t%INFO/MQ[\t%DP\t%AD]\n'
process = subprocess.Popen(['bcftools', 'query', '-f', query, str(pass_vcf)], stdout=subprocess.PIPE, text=True)
snps, indels = [], []
for line in process.stdout:
    chrom, pos, ref, alt, qual, mq, dp, ad = line.rstrip().split('\t')
    if '.' in (qual, mq, dp, ad):
        continue
    quality, mapping_quality, depth = float(qual), float(mq), int(dp)
    allele_depths = [int(value) for value in ad.split(',')]
    alt_support = sum(allele_depths[1:])
    if not (12 <= depth <= 60 and quality >= 50 and mapping_quality >= 50):
        continue
    if alt_support < 8 or alt_support / max(sum(allele_depths), 1) < 0.8:
        continue
    candidate = dict(chrom=chrom, pos=int(pos), ref=ref, alt=alt, qual=quality,
                     mq=mapping_quality, dp=depth, ad=ad, filter='PASS')
    # Prefer moderate, well-supported depth rather than extreme repeat pileups.
    score = (-abs(depth - 20), min(quality, 200), mapping_quality, chrom, int(pos))
    item = (score, candidate)
    if len(ref) == len(alt) == 1 and chrom.startswith('CM'):
        heapq.heappush(snps, item)
        if len(snps) > 1000:
            heapq.heappop(snps)
    elif len(ref) != len(alt) and abs(len(ref) - len(alt)) <= 10:
        heapq.heappush(indels, item)
        if len(indels) > 100:
            heapq.heappop(indels)
if process.wait() != 0:
    raise RuntimeError('bcftools query failed')
# Record calls at the earlier examples without assuming that they persist.
comparison_regions = 'CM009322.1:3189512-3189512,CM009336.1:3474336-3474376,CM009334.1:8569458-8569458'
comparison_query = '%CHROM\t%POS\t%REF\t%ALT\t%QUAL\t%FILTER[\t%GT\t%DP\t%AD]\n'
comparison = subprocess.run(['bcftools', 'query', '-r', comparison_regions, '-f', comparison_query,
                             str(expanded / 'results/ERR8982185.20M.filtered.vcf.gz')],
                            check=True, capture_output=True, text=True)
(expanded / 'results/original-loci-variants.tsv').write_text('CHROM\tPOS\tREF\tALT\tQUAL\tFILTER\tGT\tDP\tAD\n' + comparison.stdout)
selected = []
def moderate_pileup(candidate):
    locus = f"{candidate['chrom']}:{candidate['pos']}-{candidate['pos']}"
    depth_result = subprocess.run(['samtools', 'depth', '-r', locus,
                                  str(expanded / 'bam/ERR8982185.20M.sorted.bam')],
                                 check=True, capture_output=True, text=True)
    total_depth = sum(int(line.split()[2]) for line in depth_result.stdout.splitlines())
    candidate['unfiltered_pileup_depth'] = total_depth
    return 12 <= total_depth <= 100

for _, candidate in sorted(snps, reverse=True):
    if candidate['chrom'] not in {item['chrom'] for item in selected} and moderate_pileup(candidate):
        candidate['type'] = 'SNP'
        selected.append(candidate)
    if len(selected) == 2:
        break
for _, candidate in sorted(indels, reverse=True):
    if moderate_pileup(candidate):
        candidate['type'] = 'indel'
        selected.append(candidate)
        break
if not selected:
    raise RuntimeError('No passing calls met the screenshot selection criteria')
(expanded / 'scripts').mkdir(exist_ok=True)
(expanded / 'screenshots').mkdir(exist_ok=True)
(expanded / 'results/igv-selected-variants.json').write_text(json.dumps(selected, indent=2) + '\n')
commands = [
    'new', 'setSleepInterval 1000',
    f'genome {root}/Week-5/fasta/GCA_000002425.2_Phypa_V3_genomic.fna',
    f'snapshotDirectory {root}/Week-7/expanded/screenshots',
    f'load {root}/Week-7/expanded/results/ERR8982185.20M.filtered.vcf.gz',
    f'load {root}/Week-7/expanded/results/ERR8982185.20M.pass.vcf.gz',
    f'load {root}/Week-7/expanded/bam/ERR8982185.20M.sorted.bam',
    'maxPanelHeight 800', 'setSequenceShowTranslation false',
    'goto CM009322.1:3189400-3191050',
    'snapshot expanded_original_snp_cluster.png',
    'goto CM009322.1:3189480-3189585',
    'snapshot expanded_original_snp_zoom.png',
    'goto CM009336.1:3474325-3474390',
    'snapshot expanded_original_insertion.png',
]
for index, candidate in enumerate(selected, 1):
    chrom, pos = candidate['chrom'], candidate['pos']
    commands += [f'goto {chrom}:{max(1, pos - 40)}-{pos + 40}',
                 f'sort base {chrom}:{pos}',
                 f'snapshot expanded_pass_variant_{index}.png']
first = selected[0]
commands += [f"goto {first['chrom']}:{max(1, first['pos'] - 5000)}-{first['pos'] + 5000}",
             'snapshot expanded_regional_overview.png',
             f"goto {first['chrom']}:{max(1, first['pos'] - 40)}-{first['pos'] + 40}",
             f'saveSession {root}/Week-7/expanded/scripts/igv_local_session.xml']
(expanded / 'scripts/igv_local_batch.txt').write_text('\n'.join(commands) + '\n')
print(json.dumps(selected, indent=2))
