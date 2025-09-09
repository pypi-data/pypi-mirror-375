# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

import functools
import logging
import shutil
import typing
from copy import deepcopy

import pydantic
import typer

import beeai_cli.commands.agent
import beeai_cli.commands.auth
import beeai_cli.commands.build
import beeai_cli.commands.mcp
import beeai_cli.commands.model
import beeai_cli.commands.platform
from beeai_cli.async_typer import AsyncTyper
from beeai_cli.configuration import Configuration
from beeai_cli.console import console
from beeai_cli.utils import verbosity

logging.basicConfig(level=logging.INFO if Configuration().debug else logging.FATAL)

app = AsyncTyper(no_args_is_help=True)
app.add_typer(beeai_cli.commands.model.app, name="model", no_args_is_help=True, help="Manage model providers.")
app.add_typer(beeai_cli.commands.agent.app, name="agent", no_args_is_help=True, help="Manage agents.")
app.add_typer(beeai_cli.commands.platform.app, name="platform", no_args_is_help=True, help="Manage BeeAI platform.")
app.add_typer(beeai_cli.commands.mcp.app, name="mcp", no_args_is_help=True, help="Manage MCP servers and toolkits.")
app.add_typer(beeai_cli.commands.build.app, name="", no_args_is_help=True, help="Build agent images.")
app.add_typer(beeai_cli.commands.auth.app, name="", no_args_is_help=True, help="Beeai login.")


agent_alias = deepcopy(beeai_cli.commands.agent.app)
for cmd in agent_alias.registered_commands:
    cmd.rich_help_panel = "Agent commands"

app.add_typer(agent_alias, name="", no_args_is_help=True)


@functools.cache
def _path() -> str:
    import os

    # These are PATHs where `uv` installs itself when installed through own install script
    # Package managers may install elsewhere, but that location should already be in PATH
    paths = []
    if path := os.getenv("XDG_BIN_HOME"):
        paths.append(path)
    if path := os.getenv("XDG_DATA_HOME"):
        paths.append(f"{path}/../bin")
    paths.append(os.path.expanduser("~/.local/bin"))
    if path := os.getenv("PATH"):
        paths.append(path)
    return os.pathsep.join(paths)


@app.command("version")
async def show_version(verbose: typing.Annotated[bool, typer.Option("-v", help="Show verbose output")] = False):
    """Print version of the BeeAI CLI."""
    import importlib.metadata

    import httpx
    import packaging.version

    import beeai_cli.commands.platform

    with verbosity(verbose=verbose):
        cli_version = importlib.metadata.version("beeai-cli")
        platform_version = await beeai_cli.commands.platform.get_driver().version()

        latest_cli_version: str | None = None
        with console.status("Checking for newer version...", spinner="dots"):
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://pypi.org/pypi/beeai-cli/json")
                PyPIPackageInfo = typing.TypedDict("PyPIPackageInfo", {"version": str})
                PyPIPackage = typing.TypedDict("PyPIPackage", {"info": PyPIPackageInfo})
                if response.status_code == 200:
                    latest_cli_version = pydantic.TypeAdapter(PyPIPackage).validate_json(response.text)["info"][
                        "version"
                    ]

        console.print()
        console.print(f"     beeai-cli version: [bold]{cli_version}[/bold]")
        console.print(
            f"beeai-platform version: [bold]{platform_version.replace('-', '') if platform_version is not None else 'not running'}[/bold]"
        )
        console.print()

        if latest_cli_version and packaging.version.parse(latest_cli_version) > packaging.version.parse(cli_version):
            console.print(
                f"💡 [yellow]HINT[/yellow]: A newer version ([bold]{latest_cli_version}[/bold]) is available. Update using: [green]beeai upgrade[/green]."
            )
        elif platform_version is None:
            console.print(
                "💡 [yellow]HINT[/yellow]: Start the BeeAI platform using: [green]beeai platform start[/green]"
            )
        elif platform_version.replace("-", "") != cli_version:
            console.print(
                "💡 [yellow]HINT[/yellow]: Update the BeeAI platform using: [green]beeai platform start[/green]"
            )
        else:
            console.print("[green]Everything is up to date![/green]")


@app.command("upgrade", hidden=True)
async def upgrade(verbose: typing.Annotated[bool, typer.Option("-v", help="Show verbose output")] = False):
    """Upgrade BeeAI to the latest version."""
    from beeai_cli.commands.platform import start
    from beeai_cli.utils import run_command

    if not shutil.which("uv", path=_path()):
        console.print("[red]Error:[/red] Can't self-upgrade because 'uv' was not found.")
        raise typer.Exit(1)

    with verbosity(verbose=verbose):
        await run_command(
            ["uv", "tool", "install", "--force", "beeai-cli"],
            "Upgrading beeai-cli",
            env={"PATH": _path()},
        )
        await start(set_values_list=[], import_images=[], verbose=verbose)
        await show_version(verbose=verbose)


@app.command("uninstall", hidden=True)
async def uninstall(
    verbose: typing.Annotated[bool, typer.Option("-v", help="Show verbose output")] = False,
):
    """Uninstall BeeAI platform."""
    from beeai_cli.commands.platform import delete
    from beeai_cli.utils import run_command

    if not shutil.which("uv", path=_path()):
        console.print("[red]Error:[/red] Can't self-uninstall because 'uv' was not found.")
        raise typer.Exit(1)

    with verbosity(verbose=verbose):
        await delete(verbose=verbose)
        await run_command(
            ["uv", "tool", "uninstall", "beeai-cli"],
            "Uninstalling beeai-cli",
            env={"PATH": _path()},
        )
        console.print("[green]BeeAI uninstalled successfully.[/green]")


async def _launch_graphical_interface(host_url: str):
    import webbrowser

    import beeai_cli.commands.model

    await beeai_cli.commands.model.ensure_llm_provider()
    webbrowser.open(host_url)


@app.command("ui")
async def ui():
    """Launch the graphical interface."""
    await _launch_graphical_interface(str(Configuration().ui_url))


@app.command("playground")
async def playground() -> None:
    """Launch the graphical interface for the compose playground."""
    await _launch_graphical_interface(str(Configuration().ui_url) + Configuration().playground)


if __name__ == "__main__":
    app()
