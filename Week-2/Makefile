.PHONY: download annotate

ASSEMBLY := GCF_000001215.4_Release_6_plus_ISO1_MT
BASE_URL := https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/215/$(ASSEMBLY)

download:
	curl -C - -fLO "$(BASE_URL)/$(ASSEMBLY)_genomic.fna.gz"
	curl -C - -fLO "$(BASE_URL)/$(ASSEMBLY)_genomic.gff.gz"
	curl -C - -fLO "$(BASE_URL)/$(ASSEMBLY)_genomic.gtf.gz"

annotate:
	python annotate_lamin.py $(ASSEMBLY)_genomic.gff.gz lamin_annotation.gff3
	python annotate_lamin.py $(ASSEMBLY)_genomic.gtf.gz lamin_annotation.gtf
