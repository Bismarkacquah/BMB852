"""Prepare the teaching dataset and run Salmon for six single-end libraries."""
import argparse
import csv
import hashlib
import json
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
    checksums = {}
    for path in paths:
        digest = hashlib.sha256()
        with open(data / path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        checksums[path] = digest.hexdigest()
    Path("results/metadata").mkdir(parents=True, exist_ok=True)
    Path("results/metadata/input_checksums.json").write_text(json.dumps(checksums, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=["data", "index", "quant"])
    parser.add_argument("--source", help="Reuse an extracted tutorial directory, e.g. ../Week11")
    parser.add_argument("--data", default="data")
    parser.add_argument("--design", default="src/design.csv")
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
        Path("results/metadata/quant").mkdir(parents=True, exist_ok=True)
        version = subprocess.check_output([args.salmon, "--version"], text=True).strip()
        Path("results/metadata/software_versions.txt").write_text(version + "\n")
        for sample in samples:
            run([args.salmon, "quant", "-i", "index", "-l", "A", "-r",
                 data / f"fastq/{sample}_R1.fq", "-o", Path("results/metadata/quant") / sample,
                 "-p", args.threads, "--fldMean", "200", "--fldSD", "80"])
        Path("results").mkdir(parents=True, exist_ok=True)
        with open("results/quantification_summary.csv", "w", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["Sample", "Processed", "Mapped", "Percent", "Library", "Converged"])
            for sample in samples:
                meta = json.loads((Path("results/metadata/quant") / sample / "aux_info/meta_info.json").read_text())
                writer.writerow([sample, meta["num_processed"], meta["num_mapped"],
                                 round(meta["percent_mapped"], 2),
                                 meta.get("detected_library_type", ",".join(meta["library_types"])),
                                 meta.get("em_converged", "not reported")])


if __name__ == "__main__":
    main()
