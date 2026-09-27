# Week 5 BAM files

The BAM outputs are generated locally by the Week-5 Makefile:

```text
ERR8982185.sorted.bam
ERR8982185.sorted.bam.bai
ERR8982185.flagstat.txt
```

The BAM and index are ignored by Git because they are generated binary files. Recreate them with:

```bash
make all THREADS=2
```
