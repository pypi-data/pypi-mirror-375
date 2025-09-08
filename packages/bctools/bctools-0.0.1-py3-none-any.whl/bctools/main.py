import typer
from .modules.auto import auto
from .modules.detect import detect
from .modules.cluster import cluster
from .modules.correct import correct

app = typer.Typer(add_completion=False)

@app.callback()
def callback():
    """
    bctools is a command line tool for barcodes analysis.
    """

app.command(name="auto")(auto)
app.command(name="detect")(detect)
app.command(name="cluster")(cluster)
app.command(name="correct")(correct)


if __name__ == "__main__":
    app()