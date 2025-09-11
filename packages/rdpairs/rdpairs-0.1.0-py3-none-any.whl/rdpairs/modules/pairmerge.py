import subprocess
import typer
from typing_extensions import Annotated
from pathlib import Path

app = typer.Typer()

@app.command()
def pairmerge(
    input: Annotated[str, typer.Option(help="Input sam/bam file.")],
    output: Annotated[str, typer.Option(help="Output directory for pileup results.")],
    threads: Annotated[int, typer.Option(help="Number of threads for pileup.")]=4,
    ):
    """
    Pileup of mapped reads.
    """
    map_script = Path(__file__).parent / "scripts" / "pileup.sh"
    subprocess.run(["bash", str(map_script), input, output, str(threads)], check=True)