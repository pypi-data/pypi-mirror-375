import subprocess
import typer
from typing_extensions import Annotated
from pathlib import Path

app = typer.Typer()

@app.command()
def altersplice(
    input: Annotated[str, typer.Option(help="Input sam/bam file.")],
    output: Annotated[str, typer.Option(help="Output directory for alternative splicing results.")],
    ):
    """
    Alternative splicing analysis of nascentRNA and allRNA.
    """
    map_script = Path(__file__).parent / "scripts" / "altersplice.sh"
    subprocess.run(["bash", str(map_script), input, output], check=True)
