import subprocess
import typer
from typing_extensions import Annotated
from pathlib import Path

app = typer.Typer()

@app.command()
def detect(
    input: Annotated[str, typer.Option("--input", "-i", help="Input fastq files.")],
    read1: Annotated[str, typer.Option("--read1", "-1", help="Read1 fastq file.")],
    read2: Annotated[str, typer.Option("--read2", "-2", help="Read2 fastq file.")],
    linker: Annotated[str, typer.Option("--linker", "-l", help="Linker sequence.")],
    rnafq: Annotated[str, typer.Option("--rnafq", "-r", help="Output directory for RNA fastq files.")],
    dnafq: Annotated[str, typer.Option("--dnafq", "-d", help="Output directory for DNA fastq files.")],
    structure: Annotated[str, typer.Option("--structure", "-s", help="RNA-linker-DNA structure.")]="rna-linker-dna",
    threads: Annotated[int, typer.Option(help="Number of threads for QC.")]=4,
    ):
    """
    Split fastq files into RNA and DNA fastq files.
    """
    map_script = Path(__file__).parent.parent / "scripts" / "qc.sh"
    # subprocess.run(["bash", str(map_script), input, linker, rnafq, dnafq, structure, str(threads)], check=True)
    print(map_script)

