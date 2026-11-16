"""Small regression checks for fractional counts and ID-based joins."""
import csv
import tempfile
import unittest
from pathlib import Path
from matrices import build


class MatrixChecks(unittest.TestCase):
    def test_join_sum_and_reject_missing_annotation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            design, gtf = root / "design.csv", root / "genes.gtf"
            design.write_text("sample,group\nA,x\nB,y\n")
            gtf.write_text('chr1\ttest\ttranscript\t1\t10\t.\t+\t.\tgene_id "g1"; transcript_id "t1";\n'
                           'chr1\ttest\ttranscript\t1\t10\t.\t+\t.\tgene_id "g1"; transcript_id "t2";\n'
                           'chr1\ttest\ttranscript\t1\t10\t.\t+\t.\tgene_id "g2"; transcript_id "t3";\n')
            for sample, rows in {"A": "t1\t0.25\nt2\t1.50\nt3\t0\n",
                                 "B": "t3\t4\nt2\t2.75\nt1\t0.25\n"}.items():
                folder = root / "quant" / sample
                folder.mkdir(parents=True)
                (folder / "quant.sf").write_text("Name\tNumReads\n" + rows)
            build(design, gtf, root / "quant", root / "out")
            with open(root / "out/gene_counts.tsv", newline="") as handle:
                rows = list(csv.reader(handle, delimiter="\t"))
            self.assertEqual(rows, [["gene_id", "A", "B"],
                                    ["g1", "1.75", "3.00"], ["g2", "0", "4"]])
            gtf.write_text(gtf.read_text().replace('transcript_id "t3"', 'transcript_id "unmatched"'))
            with self.assertRaisesRegex(ValueError, "Unmapped transcript"):
                build(design, gtf, root / "quant", root / "out")


if __name__ == "__main__":
    unittest.main()
