#!/usr/bin/env python3

from pathlib import Path

import typer

print("Creating app...")
app = typer.Typer()
print(f"App created: {app}")

demos_dir = Path(__file__).parent / "pydhis2" / "demos"
print(f"Demos dir: {demos_dir}")
print(f"Exists: {demos_dir.exists()}")

if demos_dir.exists():
    demos = [f.stem for f in demos_dir.glob("*.py")]
    print(f"Found demos: {demos}")

@app.command()
def test():
    print("Test command executed!")

if __name__ == "__main__":
    print("Running main...")
    app()
