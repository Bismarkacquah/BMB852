# Script guide

Run the workflow through the parent Makefile. These helpers keep its recipes short.

| Stage | Files | Purpose |
|---|---|---|
| Workflow | `workflow.py` | Validate design, prepare inputs, summarize and validate calls |
| Download | `read_download.py`, `range_stream.py` | Retrieve the requested paired-read subset |
| Variant calling | `call_from_design.sh` | Trim, align, sort, call, normalize, and filter |
| Analysis | `analyze_deep.py` | Calculate coverage and select review examples |
| IGV | `prepare_igv.py`, `run_igv.sh`, `annotate_igv.py` | Prepare sessions, render screenshots, and mark loci |
| Reporting | `write_report.py` | Publish outputs and generate FINDINGS.md |
| Tests | `test_design.py` | Check design validation and download helpers |

Saved analysis outputs are in `../results/`. Study and processing notes are in `../METHODS.md`.
