import typer
from .modules.detect import detect
from .modules.map import map
from .modules.pairmerge import pairmerge
from .modules.rdquantify import rdquantify
from .modules.diffexp import diffexp
from .modules.altersplice import altersplice

app = typer.Typer(add_completion=False)

@app.callback()
def callback():
    """
    RDpairtools is a package for analyzing RNA-DNA interactions sequencing data.
    """

app.command(name="detect")(detect)
app.command(name="map")(map)
app.command(name="pairmerge")(pairmerge)
app.command(name="rdquantify")(rdquantify)
app.command(name="diffexp")(diffexp)
app.command(name="altersplice")(altersplice)

if __name__ == "__main__":
    app()