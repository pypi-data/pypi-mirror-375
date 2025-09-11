"""Main CLI module for finter-agent."""

import click
from rich.console import Console
from rich.panel import Panel

from src.setup import setup_environment

console = Console()


@click.group()
@click.version_option()
def cli():
    """Finter Agent - Quantitative research platform with specialized agents."""
    pass


@cli.command()
@click.option(
    "--name", default="finter-workspace", help="Project name for the environment"
)
@click.option(
    "--signal",
    "research_type",
    flag_value="signal",
    help="Initialize for signal research (trading strategies)",
)
def init(name: str, research_type: str):
    """Initialize a new quantitative research environment with specialized agents."""
    console.print(
        Panel.fit(
            f"🚀 Initializing Finter Agent environment\n"
            f"Project: [bold cyan]{name}[/bold cyan]\n"
            f"Type: [bold yellow]{research_type}[/bold yellow]",
            border_style="blue",
        )
    )

    try:
        setup_environment(name, research_type)
        console.print(
            Panel.fit(
                "✅ Environment successfully initialized!\n"
                f"Project: [bold green]{name}[/bold green]\n"
                f"Research Type: [bold yellow]{research_type}[/bold yellow]\n"
                "You can now start developing your quantitative research.",
                border_style="green",
                title="Success",
            )
        )
    except Exception as e:
        console.print(
            Panel.fit(
                f"❌ Failed to initialize environment: {str(e)}",
                border_style="red",
                title="Error",
            )
        )
        raise click.Abort()


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
