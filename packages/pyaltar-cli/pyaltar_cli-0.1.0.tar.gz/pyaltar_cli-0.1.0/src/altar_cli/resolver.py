import ast
from collections import deque
from graphlib import CycleError, TopologicalSorter
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from click.exceptions import ClickException
from rich.console import Console

BASE_URL = "https://raw.githubusercontent.com/pyaether/altar-ui/refs/{version_slug}/src/altar_ui/{component_name}.py"


def _get_dependent_components(component_file_content: str) -> list[str]:
    tree = ast.parse(component_file_content)
    dependent_components = [
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        if node.level > 0
        if node.module
    ]
    return dependent_components


def resolve_component_dependencies(
    console: Console,
    components: tuple[str],
    component_dir: Path,
    version_slug: str,
    verbose: bool = False,
) -> None:
    topological_dependency_graph = TopologicalSorter()

    components_to_resolve: deque[str] = deque(components)
    resolved_components: set[str] = set()

    component_content_cache: dict[str, str] = {}

    if verbose:
        console.print("[bold cyan]Building dependency graph...[/bold cyan]")

    while components_to_resolve:
        component_name = components_to_resolve.popleft()
        if component_name in resolved_components:
            continue

        resolved_components.add(component_name)
        component_path = component_dir / f"{component_name}.py"

        if component_path.exists():
            with open(component_path, encoding="utf-8") as file:
                component_file_content = file.read()
            if verbose:
                console.print(
                    f"[dim][green]Component '{component_name}' found in the project.[/green][/dim]"
                )
        else:
            if verbose:
                console.print(
                    f"[yellow]Component '{component_name}' not found in the project. Downloading...[/yellow]"
                )
            component_url = BASE_URL.format(
                version_slug=version_slug, component_name=component_name
            )

            try:
                request = Request(  # noqa: S310
                    component_url,
                    headers={
                        "User-Agent": "aether-pyaltar-cli",
                        "Accept": "application/vnd.github.v3+json",
                    },
                )
                with urlopen(request) as response:  # noqa: S310
                    component_file_content = response.read().decode("utf-8")
            except HTTPError as error:
                console.print(
                    f"[bold red]Error: Failed to download '[bold]{component_name}[/bold]'.\nServer returned HTTP Status [bold]{error.code}[/bold]. The component may not exist for this version.[/bold red]"
                )
                raise ClickException("Could not retrieve all required components.")
            except URLError:
                console.print(
                    f"[bold red]Error: A network error occurred while downloading '{component_name}'.[/bold red]"
                )
                raise ClickException("A network error prevented dependency resolution.")

        component_content_cache[component_name] = component_file_content
        dependent_components = _get_dependent_components(component_file_content)
        topological_dependency_graph.add(component_name, *dependent_components)

        if dependent_components:
            deps_str = ", ".join(f"[cyan]{dep}[/cyan]" for dep in dependent_components)
            console.print(f"[dim][green]{component_name}[/green][/dim]")
            console.print(f"[dim]   └── Requires: {deps_str}[/dim]")

        for components in dependent_components:
            if components not in resolved_components:
                components_to_resolve.append(components)

    if verbose:
        console.print("[bold cyan]Adding components...[/bold cyan]")

    try:
        topological_dependency_graph.prepare()
    except CycleError as error:
        console.print("[bold red]Error: A circular dependency was detected![/bold red]")
        console.print(f"Cycle path: {' -> '.join(error.args[1])}")
        raise ClickException("Circular dependency detected.")

    while topological_dependency_graph.is_active():
        for component_name in topological_dependency_graph.get_ready():
            component_path = component_dir / f"{component_name}.py"

            if not component_path.exists():
                with open(component_path, "w", encoding="utf-8") as file:
                    file.write(component_content_cache[component_name])

            topological_dependency_graph.done(component_name)

    return
