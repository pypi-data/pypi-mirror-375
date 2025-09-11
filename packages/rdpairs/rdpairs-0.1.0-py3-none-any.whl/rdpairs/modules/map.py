import subprocess
import typer
from typing_extensions import Annotated
from pathlib import Path

app = typer.Typer()

@app.command()
def map(
    input: Annotated[str, typer.Option(help="Input fastq files.")],
    output: Annotated[str, typer.Option(help="Output directory for mapping results.")],
    reference: Annotated[str, typer.Option(help="Reference genome for mapping.")],
    index: Annotated[str, typer.Option(help="minimap2 index for mapping.")],
    threads: Annotated[int, typer.Option(help="Number of threads for mapping.")]=4,
    ):
    """
    Mapping of nanopore reads to a reference genome.
    """
    map_script = Path(__file__).parent / "scripts" / "map.sh"
    subprocess.run(["bash", str(map_script), input, output, reference, index, str(threads)], check=True)