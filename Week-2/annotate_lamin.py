#!/usr/bin/env python3
"""Extract the Drosophila Lamin (Lam) gene annotation from GFF3 or GTF."""

import gzip
import re
import sys
from pathlib import Path


GENE_PATTERN = re.compile(r"(?:^|[;\t ])(?:gene|gene_name|Name|gene_id)[= ]\"?Lam\"?(?:;|$)", re.IGNORECASE)


def annotate(input_path: Path, output_path: Path) -> int:
    matched = 0
    with gzip.open(input_path, "rt", encoding="utf-8") as source, output_path.open(
        "w", encoding="utf-8"
    ) as destination:
        for line in source:
            if line.startswith("#") or GENE_PATTERN.search(line):
                destination.write(line)
                if not line.startswith("#"):
                    matched += 1
    return matched


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: python annotate_lamin.py INPUT.gz OUTPUT")
    count = annotate(Path(sys.argv[1]), Path(sys.argv[2]))
    if count == 0:
        raise SystemExit("Lamin (Lam) was not found in the annotation file")
    print(f"Wrote {count} Lamin annotation records to {sys.argv[2]}")