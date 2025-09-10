"""CLI main entry point"""

import typer
from typing import Optional
from rich.console import Console
from pathlib import Path
import shutil

app = typer.Typer(
    name="pydhis2",
    help="Reproducible DHIS2 Python SDK for LMIC scenarios",
    add_completion=False,
)

console = Console()

# Demo subcommand
demo_app = typer.Typer(help="Demo scripts management")
app.add_typer(demo_app, name="demo")


@app.command("version")
def version():
    """Show version information"""
    from pydhis2 import __version__
    console.print(f"pydhis2 version {__version__}")


@app.command("config")
def config(
    url: str = typer.Option(..., "--url", help="DHIS2 base URL"),
    username: Optional[str] = typer.Option(None, "--username", help="Username"),
    password: Optional[str] = typer.Option(None, "--password", help="Password", hide_input=True),
):
    """Configure DHIS2 connection information"""
    import os
    
    # Get default values from environment variables
    if not username:
        username = os.getenv("DHIS2_USERNAME")
    if not password:
        password = os.getenv("DHIS2_PASSWORD")
    
    if not username:
        username = typer.prompt("Username")
    if not password:
        password = typer.prompt("Password", hide_input=True)
    
    # Save to secure storage (simplified for now)
    console.print(f"✓ Configured connection to {url}")
    console.print("📝 Tip: Consider using environment variables for authentication")


# Analytics commands
analytics_app = typer.Typer(help="Analytics data operations")
app.add_typer(analytics_app, name="analytics")


@analytics_app.command("pull")
def analytics_pull(
    url: str = typer.Option(..., "--url", help="DHIS2 base URL"),
    dx: str = typer.Option(..., "--dx", help="Data dimension"),
    ou: str = typer.Option(..., "--ou", help="Organization unit"),
    pe: str = typer.Option(..., "--pe", help="Period dimension"),
    output: str = typer.Option("analytics.parquet", "--out", help="Output file"),
    format: str = typer.Option("parquet", "--format", help="Output format"),
    username: Optional[str] = typer.Option(None, "--username", help="Username"),
    password: Optional[str] = typer.Option(None, "--password", help="Password", hide_input=True),
):
    """Pull Analytics data"""
    console.print("🚧 Analytics pull command - Implementation in progress")
    console.print(f"📊 Would pull data: dx={dx}, ou={ou}, pe={pe}")
    console.print(f"💾 Would save to: {output} ({format})")


# DataValueSets commands  
datavaluesets_app = typer.Typer(help="DataValueSets operations")
app.add_typer(datavaluesets_app, name="datavaluesets")


@datavaluesets_app.command("pull")
def datavaluesets_pull(
    url: str = typer.Option(..., "--url", help="DHIS2 base URL"),
    data_set: Optional[str] = typer.Option(None, "--data-set", help="Data set ID"),
    org_unit: Optional[str] = typer.Option(None, "--org-unit", help="Organization unit ID"),
    period: Optional[str] = typer.Option(None, "--period", help="Period"),
    output: str = typer.Option("datavaluesets.parquet", "--out", help="Output file"),
    username: Optional[str] = typer.Option(None, "--username", help="Username"),
    password: Optional[str] = typer.Option(None, "--password", help="Password", hide_input=True),
):
    """Pull DataValueSets data"""
    console.print("🚧 DataValueSets pull command - Implementation in progress")
    console.print(f"📋 Would pull data from data set: {data_set}")
    console.print(f"💾 Would save to: {output}")


@datavaluesets_app.command("push")
def datavaluesets_push(
    url: str = typer.Option(..., "--url", help="DHIS2 base URL"),
    input_file: str = typer.Option(..., "--input", help="Input file"),
    strategy: str = typer.Option("CREATE_AND_UPDATE", "--strategy", help="Import strategy"),
    username: Optional[str] = typer.Option(None, "--username", help="Username"),
    password: Optional[str] = typer.Option(None, "--password", help="Password", hide_input=True),
):
    """Push DataValueSets data"""
    console.print("🚧 DataValueSets push command - Implementation in progress")
    console.print(f"📤 Would push data from: {input_file}")
    console.print(f"🔧 Using strategy: {strategy}")


# Tracker commands
tracker_app = typer.Typer(help="Tracker operations")
app.add_typer(tracker_app, name="tracker")


@tracker_app.command("events")
def tracker_events(
    url: str = typer.Option(..., "--url", help="DHIS2 base URL"),
    program: Optional[str] = typer.Option(None, "--program", help="Program ID"),
    output: str = typer.Option("events.parquet", "--out", help="Output file"),
    username: Optional[str] = typer.Option(None, "--username", help="Username"),
    password: Optional[str] = typer.Option(None, "--password", help="Password", hide_input=True),
):
    """Pull Tracker events"""
    console.print("🚧 Tracker events command - Implementation in progress")
    console.print(f"🎯 Would pull events from program: {program}")
    console.print(f"💾 Would save to: {output}")


# DQR commands
dqr_app = typer.Typer(help="Data Quality Review (DQR)")
app.add_typer(dqr_app, name="dqr")


@dqr_app.command("analyze")
def dqr_analyze(
    input_file: str = typer.Option(..., "--input", help="Input data file"),
    html_output: Optional[str] = typer.Option(None, "--html", help="HTML report output path"),
    json_output: Optional[str] = typer.Option(None, "--json", help="JSON summary output path"),
):
    """Run data quality assessment"""
    console.print("🚧 DQR analyze command - Implementation in progress")
    console.print(f"🔍 Would analyze data from: {input_file}")
    if html_output:
        console.print(f"📊 Would generate HTML report: {html_output}")
    if json_output:
        console.print(f"📄 Would generate JSON summary: {json_output}")


@app.command("status")
def status():
    """Show system status"""
    console.print("📊 pydhis2 Status:")
    console.print("✅ Core modules loaded")
    console.print("🚧 CLI implementation in progress")
    console.print("📚 See documentation: https://github.com/pydhis2/pydhis2")


# Demo commands
@demo_app.command("list")
def demo_list():
    """List all available demo scripts"""
    demos = {
        "quick": "Basic data fetching and analysis demonstration",
        "demo_test": "Comprehensive API endpoint testing and DQR report",
        "real_health_data": "Realistic health data simulation and analysis",
        "daily_sync": "Example daily data synchronization workflow",
        "monthly_report": "Example monthly reporting workflow",
        "custom_steps": "Custom pipeline steps demonstration"
    }
    
    console.print("📚 Available Demo Scripts:")
    console.print()
    for name, description in demos.items():
        console.print(f"  • [bold blue]{name}[/bold blue]: {description}")
    console.print()
    console.print("Use [bold]pydhis2 demo show <name>[/bold] to view source code")
    console.print("Use [bold]pydhis2 demo copy <name>[/bold] to copy to current directory")


@demo_app.command("show")
def demo_show(name: str):
    """Show the source code of a demo script"""
    demo_files = {
        "quick": "quick_demo.py",
        "demo_test": "demo_test.py", 
        "real_health_data": "real_health_data_demo.py",
        "daily_sync": "pydhis2/demos/daily_sync.py",
        "monthly_report": "pydhis2/demos/monthly_report.py",
        "custom_steps": "pydhis2/demos/custom_steps.py"
    }
    
    if name not in demo_files:
        console.print(f"❌ Demo '{name}' not found. Use 'pydhis2 demo list' to see available demos.")
        return
    
    demo_path = Path(demo_files[name])
    if not demo_path.exists():
        console.print(f"❌ Demo file not found: {demo_path}")
        return
    
    console.print(f"📄 Source code for demo '{name}':")
    console.print(f"📁 File: {demo_path}")
    console.print("─" * 60)
    
    try:
        with open(demo_path, 'r', encoding='utf-8') as f:
            content = f.read()
        console.print(content)
    except Exception as e:
        console.print(f"❌ Error reading file: {e}")


@demo_app.command("copy")
def demo_copy(name: str):
    """Copy a demo script to the current directory"""
    demo_files = {
        "quick": "quick_demo.py",
        "demo_test": "demo_test.py",
        "real_health_data": "real_health_data_demo.py",
        "daily_sync": "pydhis2/demos/daily_sync.py",
        "monthly_report": "pydhis2/demos/monthly_report.py", 
        "custom_steps": "pydhis2/demos/custom_steps.py"
    }
    
    if name not in demo_files:
        console.print(f"❌ Demo '{name}' not found. Use 'pydhis2 demo list' to see available demos.")
        return
    
    source_path = Path(demo_files[name])
    if not source_path.exists():
        console.print(f"❌ Demo file not found: {source_path}")
        return
    
    # Copy to current directory with original filename
    dest_path = Path(source_path.name)
    
    if dest_path.exists():
        console.print(f"⚠️  File {dest_path} already exists. Overwrite? [y/N]: ", end="")
        if input().lower() != 'y':
            console.print("❌ Copy cancelled.")
            return
    
    try:
        shutil.copy2(source_path, dest_path)
        console.print(f"✅ Demo copied to: {dest_path}")
        console.print(f"📝 Run with: py {dest_path}")
    except Exception as e:
        console.print(f"❌ Error copying file: {e}")


if __name__ == "__main__":
    app()
