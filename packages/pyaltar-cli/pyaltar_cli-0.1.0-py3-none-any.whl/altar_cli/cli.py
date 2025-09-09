from pathlib import Path

import click
from rich.console import Console

from . import __version__
from .configs import configs
from .resolver import resolve_component_dependencies
from .utils import parse_version_slug


@click.group()
def main() -> None:
    pass


@main.command()
def version() -> None:
    console = Console()
    console.print(f"Altar CLI version: [green]{__version__}[/green]")


@main.command()
@click.argument("version_slug", type=click.STRING)
@click.argument("components", nargs=-1, type=click.STRING)
@click.option("--verbose", is_flag=True, help="Enable verbose mode to echo steps.")
def add(version_slug: str, components: tuple[str], verbose: bool) -> None:
    console = Console()

    def _create_dir_if_not_exists(directory: Path) -> None:
        if not directory.exists():
            if verbose:
                console.print(f"Creating directory: {directory}")
            directory.mkdir(parents=True)

    def _create_file_if_not_exists(file: Path) -> None:
        if not file.exists():
            if verbose:
                console.print(f"Creating empty file: {file}")
            file.touch()

    _create_dir_if_not_exists(configs.components_dir)

    components_dir_init_file = configs.components_dir / "__init__.py"
    _create_file_if_not_exists(components_dir_init_file)

    if verbose:
        console.print("[bold blue]Resolving Dependencies[/bold blue]")

    resolve_component_dependencies(
        console=console,
        components=components,
        component_dir=configs.components_dir,
        version_slug=parse_version_slug(version_slug),
        verbose=verbose,
    )

    console.print(
        f"\n[bold green]'{', '.join(components)}' added successfully![/bold green]"
    )


if __name__ == "__main__":
    main()
