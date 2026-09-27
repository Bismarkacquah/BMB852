"""Create an IGV batch script for the four selected regions."""
import argparse  # Accept a host-visible directory when using WSL with Windows IGV.
from pathlib import Path  # Resolve the local checkout.
parser = argparse.ArgumentParser()  # Define the command interface.
parser.add_argument("--igv-root", help="Absolute Week-5 directory as seen by IGV")  # Optional host path.
args = parser.parse_args()  # Read command-line arguments.
root = Path(__file__).resolve().parents[1]  # Local Week-5 directory.
host = (args.igv_root or root.as_posix()).replace("\\", "/").rstrip("/")  # Normalize IGV paths.
parent = host.rsplit("/", 1)[0]  # Week-2 is next to Week-5.
commands = ["new", f"snapshotDirectory {host}/screenshots",
            f"genome {host}/fasta/GCA_000002425.2_Phypa_V3_genomic.fna",
            f"load {parent}/Week-2/data/GCA_000002425.2_Phypa_V3_genomic.gff",
            f"load {host}/bam/ERR8982185.sorted.bam", "maxPanelHeight 500"]  # Load matching inputs.
views = [("CM009336.1:3475540-3475640", "week5_zoom_mismatches.png"),
         ("CM009316.1:618250-618310", "week5_zoom_read_end.png"),
         ("CM009336.1:3475450-3475530", "week5_zoom_depth4.png"),
         ("CM009316.1:8931-13135", "week5_moss_gene_locus.png")]  # Informative intervals.
for locus, filename in views:  # Save the same four views in any checkout.
    commands.extend([f"goto {locus}", f"snapshot {filename}"])  # Navigate, then capture.
commands.append("exit")  # Close the batch IGV instance after capture.
output = root / "scripts/igv_local_batch.txt"  # This machine-specific file is ignored by Git.
output.write_text("\n".join(commands)+"\n")  # Write one command per line.
print(output)  # Tell the user which file to open in IGV.
