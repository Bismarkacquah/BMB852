"""Prepare the teaching dataset and run Salmon for six single-end libraries."""
import argparse
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path
from matrices import sample_names

URL = "https://data.biostarhandbook.com/data/rnaseq-tutorial-2026.tar.gz"


def run(command):
    print("+ " + " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), check=True)


def prepare(data, source, samples):
    paths = ["fasta/chr22.transcripts.fa", "gtf/chr22.gtf"]
    paths += [f"fastq/{sample}_R1.fq" for sample in samples]
    data.mkdir(parents=True, exist_ok=True)
    if not all((data / path).is_file() for path in paths):
        if source:
            for path in paths:
                destination = data / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(Path(source) / path, destination)
        else:
            archive = data / "rnaseq-tutorial-2026.tar.gz"
            temporary = archive.with_suffix(".download")
            urllib.request.urlretrieve(URL, temporary)
            temporary.replace(archive)
            with tarfile.open(archive, "r:gz") as bundle:
                members = {member.name.removeprefix("./"): member for member in bundle}
                for path in paths:
                    member = members[path]
                    if not member.isfile():
                        raise ValueError(f"Expected regular archive file: {path}")
                    destination = data / path
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with bundle.extractfile(member) as src, open(destination, "wb") as dst:
                        shutil.copyfileobj(src, dst)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=["data", "index", "quant"])
    parser.add_argument("--source", help="Reuse an extracted tutorial directory, e.g. ../Week11")
    parser.add_argument("--data", default="data")
    parser.add_argument("--design", default="design.csv")
    parser.add_argument("--salmon", default="salmon")
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    samples = sample_names(args.design)
    data = Path(args.data)
    if args.step == "data":
        prepare(data, args.source, samples)
    elif args.step == "index":
        run([args.salmon, "index", "-t", data / "fasta/chr22.transcripts.fa",
             "-i", "index", "--keepDuplicates", "-p", args.threads])
    else:
        Path("quant").mkdir(exist_ok=True)
        for sample in samples:
            run([args.salmon, "quant", "-i", "index", "-l", "A", "-r",
                 data / f"fastq/{sample}_R1.fq", "-o", Path("quant") / sample,
                 "-p", args.threads, "--fldMean", "200", "--fldSD", "80"])


if __name__ == "__main__":
    main()
