from typer import Typer
from .manga_stitcher import main


app = Typer()
app.command()(main)


if __name__ == "__main__":
    app()
