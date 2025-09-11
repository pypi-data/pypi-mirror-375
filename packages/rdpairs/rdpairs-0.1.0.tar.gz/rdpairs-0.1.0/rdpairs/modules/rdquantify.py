import subprocess
import typer
from typing_extensions import Annotated
from pathlib import Path

app = typer.Typer()

@app.command()
def rdquantify(
    input: Annotated[str, typer.Option(help="Input sam/bam file.")],
    output: Annotated[str, typer.Option(help="Output directory for quantification results.")],
    group: Annotated[str, typer.Option(help="Group information for quantification.")],
    threads: Annotated[int, typer.Option(help="Number of threads for quantification.")]=4,
    ):
    """
    Quantification of nascentRNA and allRNA.
    """
    map_script = Path(__file__).parent / "scripts" / "quantify.sh"
    subprocess.run(["bash", str(map_script), input, output, group, str(threads)], check=True)
    