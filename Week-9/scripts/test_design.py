"""Check that design errors fail before expensive downloads or alignments."""
import csv
import gzip
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from workflow import design, get_reads, sha


class DesignTests(unittest.TestCase):
    def setUp(self):
        with open('design.csv', encoding='utf-8-sig') as handle:
            self.rows = list(csv.DictReader(handle))

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

    def test_nonpositive_batch_size_rejected(self):
        self.rows[0]['bwa_batch_bases']='0'
        with self.assertRaises(ValueError):
            self.check_rows(self.rows)

    def test_alignment_setting_change_reuses_identical_raw_reads(self):
        row=dict(self.rows[0],pairs='1')
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            hashes={}
            for mate in (1,2):
                path=out/f'read{mate}.fastq.gz'
                with gzip.open(path,'wb') as handle:
                    handle.write(b'@read1\nACGT\n+\nIIII\n')
                hashes[path.name]=sha(path)
            (out/'reads.json').write_text(json.dumps({'design':row,'sha256':hashes}))
            changed=dict(row,bwa_batch_bases=str(int(row['bwa_batch_bases'])+10000000))
            with patch('range_stream.urllib.request.urlopen',side_effect=AssertionError('Unexpected re-download')):
                get_reads(changed,out)
            self.assertEqual(hashes,{name:sha(out/name) for name in hashes})

    def mate_caches(self,out,row,ids):
        for mate,name in enumerate(ids,1):
            target=out/f'read{mate}.fastq.gz'
            with gzip.open(target,'wb') as handle:
                handle.write(b'@'+name+b'\nACGT\n+\nIIII\n')
            record={'sample_id':row['sample_id'],'url':row[f'read{mate}'],'records':1,
                    'source_bytes':int(row[f'read{mate}_bytes']),'mate':mate,'name':target.name,
                    'sha256':sha(target),'id_sha256':hashlib.sha256(b'@'+name+b'\n').hexdigest(),'bases':4}
            (out/f'read{mate}.json').write_text(json.dumps(record))

    def test_complete_mates_recover_without_joint_manifest_or_network(self):
        row=dict(self.rows[0],pairs='1')
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp);self.mate_caches(out,row,[b'read1',b'read1'])
            with patch('range_stream.urllib.request.urlopen',side_effect=AssertionError('Unexpected transfer')):
                get_reads(row,out)
            self.assertTrue((out/'reads.json').exists())

    def test_recovered_mates_with_different_ids_are_rejected(self):
        row=dict(self.rows[0],pairs='1')
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp);self.mate_caches(out,row,[b'read1',b'read2'])
            with self.assertRaises(ValueError):
                get_reads(row,out)
            self.assertFalse((out/'reads.json').exists())


if __name__ == '__main__':
    unittest.main()
