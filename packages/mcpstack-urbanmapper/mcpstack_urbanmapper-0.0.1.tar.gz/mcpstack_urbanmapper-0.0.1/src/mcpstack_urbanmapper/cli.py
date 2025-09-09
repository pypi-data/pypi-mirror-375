from __future__ import annotations

import json
from typing import Annotated

import typer
from beartype import beartype
from MCPStack.core.tool.cli.base import BaseToolCLI, ToolConfig
from rich.console import Console
from rich.panel import Panel

from .actions.shared import get_env_defaults

console = Console()


@beartype
class UrbanMapperCLI(BaseToolCLI):
    @classmethod
    def get_app(cls) -> typer.Typer:
        app = typer.Typer(
            help="UrbanMapper Tool CLI",
            add_completion=False,
            pretty_exceptions_show_locals=False,
            rich_markup_mode="markdown",
        )
        app.command(help="Quick init (HF-only, split, CRS).")(cls.init)
        app.command(help="Configure UM tool (env + params).")(cls.configure)
        app.command(help="Show UM status.")(cls.status)
        return app

    @classmethod
    def init(
        cls,
        enforce_hf_only: Annotated[
            bool, typer.Option("--enforce-hf-only/--no-enforce-hf-only")
        ] = True,
        default_split: Annotated[str | None, typer.Option("--default-split")] = None,
        default_crs: Annotated[str | None, typer.Option("--default-crs")] = "EPSG:4326",
    ) -> None:
        console.print(
            f"[green]✅ HF-only: {enforce_hf_only} | split={default_split} | crs={default_crs}[/green]"
        )
        console.print("Export and run:")
        console.print(
            f"    export MCP_URBANMAPPER_ENFORCE_HF_ONLY={'1' if enforce_hf_only else '0'}"
        )
        if default_split:
            console.print(f"    export MCP_URBANMAPPER_DEFAULT_SPLIT='{default_split}'")
        if default_crs:
            console.print(f"    export MCP_URBANMAPPER_DEFAULT_CRS='{default_crs}'")

    @classmethod
    def configure(
        cls,
        enforce_hf_only: Annotated[
            bool | None, typer.Option("--enforce-hf-only/--no-enforce-hf-only")
        ] = None,
        default_split: Annotated[str | None, typer.Option("--default-split")] = None,
        default_crs: Annotated[str | None, typer.Option("--default-crs")] = None,
        output: Annotated[str | None, typer.Option("--output", "-o")] = None,
        verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
    ) -> ToolConfig:
        env_vars = get_env_defaults()
        if enforce_hf_only is not None:
            env_vars["MCP_URBANMAPPER_ENFORCE_HF_ONLY"] = (
                "1" if enforce_hf_only else "0"
            )
        if default_split is not None:
            env_vars["MCP_URBANMAPPER_DEFAULT_SPLIT"] = default_split
        if default_crs is not None:
            env_vars["MCP_URBANMAPPER_DEFAULT_CRS"] = default_crs

        cfg: ToolConfig = {"env_vars": env_vars, "tool_params": {}}
        path = output or "urbanmapper_config.json"
        with open(path, "w") as f:
            json.dump(cfg, f, indent=2)

        console.print(f"[green]✅ Saved UM config to {path}[/green]")
        if verbose:
            console.print(
                Panel.fit(
                    json.dumps(cfg, indent=2),
                    title="[bold green]Configuration[/bold green]",
                )
            )
        return cfg

    @classmethod
    def status(cls, verbose: bool = False) -> None:
        import os

        env_defaults = get_env_defaults()
        status_lines = []
        for k, v in env_defaults.items():
            status_lines.append(f"{k}={os.getenv(k, v or '[default]')}")
        msg = "\n".join(status_lines)
        console.print(Panel.fit(msg, title="[bold green]UM status[/bold green]"))
