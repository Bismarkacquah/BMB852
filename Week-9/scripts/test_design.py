"""Check that design errors fail before expensive downloads or alignments."""
import csv
import tempfile
import unittest
from pathlib import Path
from workflow import design


class DesignTests(unittest.TestCase):
    def setUp(self):
        with open('design.tsv') as handle:
            self.rows = list(csv.DictReader(handle, delimiter='\t'))

    def check_rows(self, rows):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'design.tsv'
            with path.open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=self.rows[0], delimiter='\t')
                writer.writeheader()
                writer.writerows(rows)
            return design(path)

    def test_ten_unique_public_samples(self):
        self.assertEqual(len(self.check_rows(self.rows)), 10)

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            self.check_rows([self.rows[0], self.rows[0]])

    def test_invalid_pair_count_rejected(self):
        self.rows[0]['pairs'] = '0'
        with self.assertRaises(ValueError):
            self.check_rows(self.rows)

    def test_local_path_rejected(self):
        self.rows[0]['read1'] = '/private/unavailable.fastq.gz'
        with self.assertRaises(ValueError):
            self.check_rows(self.rows)


if __name__ == '__main__':
    unittest.main()
