import subprocess
import typer
from typing_extensions import Annotated
from pathlib import Path

app = typer.Typer()

@app.command()
def diffexp(
    input: Annotated[str, typer.Option(help="Input directory for quantification results.")],
    output: Annotated[str, typer.Option(help="Output directory for differential expression results.")],
    ):
    """
    Differential expression analysis of nascentRNA and allRNA.
    """
    map_script = Path(__file__).parent / "scripts" / "diffexp.sh"
    subprocess.run(["bash", str(map_script), input, output], check=True)
