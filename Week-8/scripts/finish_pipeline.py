"""Queue annotation after existing Make jobs finish; record success or failure."""
import argparse
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--wait-pid', action='append', type=int, default=[])
a = p.parse_args()
status_path = Path('provenance/pipeline-status.json')


def status(state, **extra):
    status_path.write_text(json.dumps(dict(state=state, updated_utc=datetime.now(timezone.utc).isoformat(), **extra), indent=2) + '\n')


status('running', stage='independent samples and annotation database', waiting_for=a.wait_pid)
for pid in a.wait_pid:
    process = Path(f'/proc/{pid}/cmdline')
    fingerprint = process.read_bytes() if process.exists() else b''
    while process.exists():
        try:
            if process.read_bytes() != fingerprint:
                break
        except FileNotFoundError:
            break
        time.sleep(10)
expected = [Path('annotation/data/Phypa_V3/snpEffectPredictor.bin')]
missing = [str(path) for path in expected if not path.is_file() or not path.stat().st_size]
if missing:
    status('failed', stage='upstream processing', missing_outputs=missing, logs=['provenance/pipeline.log', 'provenance/snpeff-build.log'])
    raise SystemExit('Upstream outputs missing: ' + ', '.join(missing))
status('running', stage='five-sample processing, annotation, comparisons, and IGV')
with Path('provenance/completion.log').open('w') as log:
    result = subprocess.run(['make', 'report'], stdout=log, stderr=subprocess.STDOUT)
if result.returncode == 0:
    report_path = Path('README.md')
    report = report_path.read_text()
    updated = ('### Processing status\n\n'
               '**Data processing and annotation complete.** The five independently processed sample VCFs have been merged, '
               'annotated with SnpEff, and summarized. See the [generated result tables](results/analysis_report.md), '
               '[effect summary](results/effect_summary.json), and [candidate loci](results/effect_candidates.tsv). '
               'IGV review and candidate interpretation remain pending.\n\n'
               '[Pipeline status](provenance/pipeline-status.json) and the provenance logs record completion.\n\n'
               '### Week 7 input validation')
    report_path.write_text(re.sub(r'### Processing status.*?### Week 7 input validation', updated, report, flags=re.S))
status('complete' if result.returncode == 0 else 'failed', stage='five-sample analysis and IGV report', exit_code=result.returncode, log='provenance/completion.log')
raise SystemExit(result.returncode)
