import json
import logging
import os
from pathlib import Path

import typer
from beartype import beartype
from beartype.typing import Annotated, Any, Dict, List, Optional
from MCPStack.core.tool.cli.base import BaseToolCLI, ToolConfig
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mcpstack_jupyter.tools.jupyter.utils.config_loader import (
    load_cli_defaults,
    load_env_defaults,
    load_known_tools,
)

logger = logging.getLogger(__name__)
console = Console()


def _csv_list(value: Optional[str]) -> Optional[List[str]]:
    if value is None or value.strip() == "":
        return None
    return [p.strip() for p in value.split(",") if p.strip()]


@beartype
class JupyterCLI(BaseToolCLI):
    @classmethod
    def get_app(cls) -> typer.Typer:
        app = typer.Typer(
            help="Jupyter tool commands (Option A: reuse jupyter-mcp-server tools).",
            add_completion=False,
            pretty_exceptions_show_locals=False,
            rich_markup_mode="markdown",
        )
        app.command(help="Configure the Jupyter tool (Token,Provider,Kernel, etc.).")(
            cls.configure
        )
        app.command(
            help="Display the current status of the Jupyter tool (Validate with Original Library, etc."
        )(cls.status)
        return app

    @classmethod
    def configure(
        cls,
        provider: Annotated[
            Optional[str],
            typer.Option("--provider", help="Upstream provider", show_default=True),
        ] = None,
        document_url: Annotated[
            Optional[str],
            typer.Option("--document-url", help="e.g. http://127.0.0.1:8888"),
        ] = None,
        document_id: Annotated[
            Optional[str],
            typer.Option("--document-id", help="Notebook path, e.g. analysis.ipynb"),
        ] = None,
        token: Annotated[
            Optional[str],
            typer.Option(
                "--token",
                help="Convenience: sets both DOCUMENT_TOKEN and RUNTIME_TOKEN",
            ),
        ] = None,
        document_token: Annotated[
            Optional[str],
            typer.Option("--document-token", help="Override DOCUMENT_TOKEN"),
        ] = None,
        runtime_url: Annotated[
            Optional[str],
            typer.Option("--runtime-url", help="e.g. http://127.0.0.1:8888"),
        ] = None,
        runtime_id: Annotated[
            Optional[str],
            typer.Option("--runtime-id", help="Optional kernel id"),
        ] = None,
        runtime_token: Annotated[
            Optional[str],
            typer.Option("--runtime-token", help="Override RUNTIME_TOKEN"),
        ] = None,
        include: Annotated[
            Optional[str],
            typer.Option(
                "--include",
                help="Comma-separated list of tool names to expose "
                "(default: all known; see configuration/tools.yaml)",
            ),
        ] = None,
        output: Annotated[
            Optional[str],
            typer.Option("--output", "-o", help="Output path for ToolConfig JSON"),
        ] = None,
        verbose: Annotated[
            bool, typer.Option("--verbose", "-v", help="Print config dict")
        ] = False,
    ) -> ToolConfig:
        console.print("[turquoise4]💬 Configuring Jupyter tool...[/turquoise4]")

        env_defaults = load_env_defaults()
        cli_defaults = load_cli_defaults()
        tools_info = load_known_tools()
        known_tools: List[str] = tools_info.get("known_tools", [])

        provider = provider or env_defaults.get("provider", "jupyter")

        if document_url is None:
            document_url = typer.prompt(
                cli_defaults.get("prompts", {}).get("document_url", "Document URL"),
                default=env_defaults.get("document_url", "http://127.0.0.1:8888"),
            )
        if document_id is None:
            document_id = typer.prompt(
                cli_defaults.get("prompts", {}).get("document_id", "Notebook path"),
                default=env_defaults.get("document_id", "notebook.ipynb"),
            )
        if runtime_url is None:
            runtime_url = typer.prompt(
                cli_defaults.get("prompts", {}).get("runtime_url", "Runtime URL"),
                default=env_defaults.get("runtime_url") or document_url,
            )

        document_token = document_token or token or os.getenv("DOCUMENT_TOKEN")
        runtime_token = runtime_token or token or os.getenv("RUNTIME_TOKEN")

        if document_token and not runtime_token:
            runtime_token = document_token
        if runtime_token and not document_token:
            document_token = runtime_token

        if not document_token or not runtime_token:
            supplied = typer.prompt(
                "Token (used for both DOCUMENT_TOKEN and RUNTIME_TOKEN)"
            )
            while not supplied:
                supplied = typer.prompt(
                    "Token (used for both DOCUMENT_TOKEN and RUNTIME_TOKEN)"
                )
            document_token = document_token or supplied
            runtime_token = runtime_token or supplied

        env_vars: Dict[str, str] = {
            "PROVIDER": provider,
            "DOCUMENT_URL": document_url,
            "DOCUMENT_ID": document_id,
            "DOCUMENT_TOKEN": document_token,
            "RUNTIME_URL": runtime_url,
            "RUNTIME_ID": runtime_id or "",
            "RUNTIME_TOKEN": runtime_token,
        }

        console.print(
            "\n[turquoise4]💬 Additional env vars (key=value, Enter to finish):[/turquoise4]"
        )
        while True:
            kv = typer.prompt("", default="", show_default=False)
            if not kv:
                break
            if "=" in kv:
                k, v = kv.split("=", 1)
                env_vars[k.strip()] = v.strip()
            else:
                console.print("[red]Invalid: Use key=value[/red]")

        include_list = _csv_list(include)
        if include_list is not None:
            unknown = [n for n in include_list if n not in known_tools]
            if unknown:
                console.print(
                    f"[red]❌ Unknown tool names: {', '.join(unknown)}[/red]\n"
                    f"[yellow]Allowed: {', '.join(known_tools)}[/yellow]"
                )
                raise typer.Exit(code=1)

        tool_params: Dict[str, Any] = {"include": include_list}

        config_dict: ToolConfig = {"env_vars": env_vars, "tool_params": tool_params}

        out_name = (
            output or cli_defaults.get("output_filename") or "jupyter_config.json"
        )
        out_path = Path(out_name)
        out_path.write_text(json.dumps(config_dict, indent=4))
        console.print(f"[green]✅ Config dict saved to {out_path}[/green]")

        if verbose:
            console.print(
                Panel(
                    json.dumps(config_dict, indent=2),
                    title="[bold green]Configuration[/bold green]",
                    border_style="green",
                )
            )
        return config_dict

    @classmethod
    def status(cls, verbose: bool = False) -> None:
        try:
            keys = [
                "PROVIDER",
                "DOCUMENT_URL",
                "DOCUMENT_ID",
                "DOCUMENT_TOKEN",
                "RUNTIME_URL",
                "RUNTIME_ID",
                "RUNTIME_TOKEN",
            ]
            table = Table(title="[bold green]Jupyter Tool Status[/bold green]")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="magenta")
            for k in keys:
                val = os.getenv(k, "")
                if k.endswith("_TOKEN") and val:
                    val = val[:4] + "…" + val[-4:]
                table.add_row(k, val or "(unset)")
            console.print(table)

            import importlib

            try:
                server = importlib.import_module("jupyter_mcp_server.server")
                known = load_known_tools().get("known_tools", [])
                if verbose:
                    t = Table(
                        title="[bold green]Upstream Tool Availability[/bold green]"
                    )
                    t.add_column("Tool", style="cyan")
                    t.add_column("Available", style="magenta")
                    for n in known:
                        t.add_row(n, "yes" if hasattr(server, n) else "NO")
                    console.print(t)
                else:
                    missing = [n for n in known if not hasattr(server, n)]
                    if missing:
                        console.print(
                            f"[yellow]⚠️ Missing upstream tools: {', '.join(missing)}[/yellow]"
                        )
            except Exception as e:
                console.print(
                    f"[red]❌ Could not import jupyter_mcp_server.server: {e}[/red]"
                )

        except Exception as e:
            console.print(f"[red]❌ Error getting status: {e}[/red]")
            logger.error("Status failed: %s", e, exc_info=True)
