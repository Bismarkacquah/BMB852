"""Create an IGV batch script for viewing Week 7 candidates with Week 5 reads."""
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--igv-root', help='Repository root as seen by IGV, e.g. C:/path/BMB852')
args = parser.parse_args()
week7 = Path(__file__).resolve().parents[1]
root = args.igv_root.rstrip('/').replace('\\', '/') if args.igv_root else week7.parent.as_posix()
(week7 / 'screenshots').mkdir(exist_ok=True)
commands = [
    'new',
    'setSleepInterval 500',
    f'genome {root}/Week-5/fasta/GCA_000002425.2_Phypa_V3_genomic.fna',
    f'snapshotDirectory {root}/Week-7/screenshots',
    f'load {root}/Week-7/results/ERR8982185.vcf',
    f'load {root}/Week-5/bam/ERR8982185.sorted.bam',
    f'load {root}/Week-7/results/ERR8982185.pass.vcf',
    'maxPanelHeight 600',
    'setSequenceShowTranslation false',
    'goto CM009322.1:3189400-3191050',
    'snapshot week7_snp_cluster.png',
    'goto CM009322.1:3189480-3189585',
    'sort base CM009322.1:3189512',
    'snapshot week7_snp_zoom.png',
    'goto CM009336.1:3474325-3474390',
    'sort base CM009336.1:3474356',
    'snapshot week7_insertion.png',
    'goto CM009334.1:8569425-8569490',
    'sort base CM009334.1:8569458',
    'snapshot week7_second_snp.png',
    'goto CM009322.1:3189480-3189585',
    f'saveSession {root}/Week-7/scripts/igv_local_session.xml',
]
output = week7 / 'scripts' / 'igv_local_batch.txt'
output.write_text('\n'.join(commands) + '\n', encoding='utf-8')
print(output)
