#!/usr/bin/env python3
# # Copyright (c) {{ year }} {{ author }}
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

# # Copyright (c) 2025 Aaron Sachs
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Command-line interface for the SuperOps Python client library.

This module provides a comprehensive CLI for interacting with the SuperOps API,
including commands for testing connectivity, managing clients and tickets,
executing scripts, and performing raw GraphQL queries.

The CLI follows Unix philosophy principles:
- Do one thing well
- Work with other programs via pipes
- Use text streams as universal interface
- Optimize for common use cases
- Provide meaningful exit codes
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import click
import httpx
from rich.console import Console
from rich.json import JSON
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

try:
    from . import SuperOpsClient, SuperOpsConfig, SuperOpsError, create_client, get_version
except ImportError:
    # Handle case where we're running from source without full package
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from client import SuperOpsClient
    from config import SuperOpsConfig
    from exceptions import SuperOpsError

    def get_version():
        return "0.1.0"

    def create_client(*args, **kwargs):
        return SuperOpsClient(*args, **kwargs)


# Initialize rich console for beautiful output
console = Console(stderr=True)  # Use stderr for UI, stdout for data


class CLIError(Exception):
    """Base exception for CLI-specific errors."""

    def __init__(self, message: str, exit_code: int = 1, suggestions: Optional[List[str]] = None):
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.suggestions = suggestions or []


class OutputFormatter:
    """Handles formatting output for different contexts."""

    @staticmethod
    def is_pipe_mode() -> bool:
        """Check if output is being piped or redirected."""
        return not sys.stdout.isatty()

    @staticmethod
    def is_interactive() -> bool:
        """Check if running in interactive mode."""
        return sys.stdin.isatty() and sys.stdout.isatty() and not os.getenv("CI")

    @classmethod
    def output(cls, data: Any, format_type: str = "auto", color: bool = True) -> None:
        """Output data in the appropriate format."""
        if cls.is_pipe_mode() or format_type == "json":
            # Machine-readable format for piping
            if isinstance(data, (dict, list)):
                print(json.dumps(data, indent=None, separators=(",", ":")))
            else:
                print(str(data))
        elif format_type == "table" and isinstance(data, list) and data:
            # Table format for human consumption
            cls._output_table(data, color)
        else:
            # Pretty format for human consumption
            cls._output_pretty(data, color)

    @classmethod
    def _output_table(cls, data: List[Dict[str, Any]], color: bool) -> None:
        """Output data as a table."""
        if not data:
            return

        table = Table(show_header=True, header_style="bold magenta")

        # Use keys from first item for columns
        keys = list(data[0].keys())
        for key in keys:
            table.add_column(key.replace("_", " ").title())

        for item in data:
            row = []
            for key in keys:
                value = item.get(key, "")
                # Truncate long values
                if isinstance(value, str) and len(value) > 50:
                    value = value[:47] + "..."
                row.append(str(value))
            table.add_row(*row)

        console.print(table)

    @classmethod
    def _output_pretty(cls, data: Any, color: bool) -> None:
        """Output data in pretty format."""
        if isinstance(data, (dict, list)):
            console.print(JSON(json.dumps(data, indent=2)))
        else:
            console.print(str(data))

    @classmethod
    def error(cls, message: str, suggestions: Optional[List[str]] = None) -> None:
        """Output error message with suggestions."""
        console.print(f"[red]Error: {message}[/red]")
        if suggestions:
            console.print("\n[yellow]Suggestions:[/yellow]")
            for suggestion in suggestions:
                console.print(f"  • {suggestion}")

    @classmethod
    def success(cls, message: str) -> None:
        """Output success message."""
        if not cls.is_pipe_mode():
            console.print(f"[green]✓ {message}[/green]")


def setup_logging(debug: bool = False, verbose: bool = False) -> None:
    """Setup logging with rich handler."""
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )

    # Quiet down noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_config() -> SuperOpsConfig:
    """Get configuration from environment variables or config file."""
    try:
        # Try to load from environment first
        config = SuperOpsConfig.from_env()
        return config
    except Exception as e:
        # Try to load from config file
        config_paths = [
            Path.home() / ".config" / "superops" / "config.json",
            Path.home() / ".superops" / "config.json",
            Path.cwd() / "superops.config.json",
            Path.cwd() / ".superops.json",
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        config_data = json.load(f)
                    return SuperOpsConfig(**config_data)
                except Exception:
                    continue

        # If no config found, show helpful error
        raise CLIError(
            "No SuperOps configuration found",
            exit_code=2,
            suggestions=[
                "Set SUPEROPS_API_KEY environment variable",
                "Set SUPEROPS_BASE_URL environment variable (optional)",
                f"Create config file at {config_paths[0]}",
                "Run 'superops-cli config init' to create a config file",
            ],
        )


def handle_exceptions(func):
    """Decorator to handle exceptions and provide helpful error messages."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CLIError as e:
            OutputFormatter.error(e.message, e.suggestions)
            sys.exit(e.exit_code)
        except SuperOpsError as e:
            OutputFormatter.error(f"SuperOps API Error: {e}")
            sys.exit(1)
        except httpx.TimeoutException:
            OutputFormatter.error(
                "Request timed out",
                suggestions=[
                    "Check your internet connection",
                    "Verify the API endpoint is reachable",
                    "Try increasing timeout with --timeout option",
                ],
            )
            sys.exit(1)
        except httpx.ConnectError:
            OutputFormatter.error(
                "Failed to connect to SuperOps API",
                suggestions=[
                    "Check your internet connection",
                    "Verify the API endpoint URL",
                    "Check if API endpoint is accessible",
                ],
            )
            sys.exit(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            sys.exit(130)
        except Exception as e:
            if "--debug" in sys.argv:
                console.print_exception()
            else:
                OutputFormatter.error(f"Unexpected error: {e}")
            sys.exit(1)

    return wrapper


# CLI Group setup
@click.group(name="superops-cli")
@click.version_option(version=get_version(), prog_name="superops-cli")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--no-color", is_flag=True, help="Disable colored output")
@click.option(
    "--format", type=click.Choice(["auto", "json", "table"]), default="auto", help="Output format"
)
@click.option("--timeout", type=float, default=30.0, help="Request timeout in seconds")
@click.pass_context
def cli(ctx, debug, verbose, no_color, format, timeout):
    """SuperOps CLI - Command-line interface for the SuperOps API.

    This tool provides commands for managing SuperOps resources including
    clients, tickets, scripts, and more. It supports both interactive use
    and pipeline integration.

    Examples:
        superops-cli test-connection
        superops-cli list-clients --format json | jq '.items[].name'
        superops-cli create-ticket --title "Issue" --client-id 123
    """
    # Disable colors if requested or if piping
    if no_color or OutputFormatter.is_pipe_mode():
        console._color_system = None

    # Setup logging
    setup_logging(debug, verbose)

    # Store context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    ctx.obj["verbose"] = verbose
    ctx.obj["format"] = format
    ctx.obj["timeout"] = timeout


@cli.command()
@click.pass_context
def test_connection(ctx):
    """Test API connectivity and authentication."""

    async def _test():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=OutputFormatter.is_pipe_mode(),
        ) as progress:
            task = progress.add_task("Testing connection...", total=None)

            try:
                config = get_config()
                config.timeout = ctx.obj["timeout"]

                async with SuperOpsClient(config) as client:
                    connection_info = await client.test_connection()

                    if connection_info.get("connected"):
                        progress.update(task, description="✓ Connection successful")
                        OutputFormatter.success("Connection test passed")
                        OutputFormatter.output(connection_info, ctx.obj["format"])
                    else:
                        raise CLIError("Connection test failed")

            except Exception as e:
                progress.update(task, description="✗ Connection failed")
                raise e

    asyncio.run(_test())


@cli.command()
@click.option("--page", type=int, default=1, help="Page number")
@click.option("--page-size", type=int, default=50, help="Items per page")
@click.option(
    "--status",
    type=click.Choice(["active", "inactive", "suspended"]),
    help="Filter by client status",
)
@click.option("--name", help="Filter by client name (partial match)")
@click.pass_context
def list_clients(ctx, page, page_size, status, name):
    """List all clients with optional filtering."""

    async def _list():
        config = get_config()
        config.timeout = ctx.obj["timeout"]

        async with SuperOpsClient(config) as client:
            filters = {}
            if status:
                filters["status"] = status
            if name:
                filters["name"] = name

            result = await client.clients.list(
                page=page, page_size=page_size, filters=filters if filters else None
            )

            if ctx.obj["format"] == "table":
                # Format data for table display
                table_data = []
                for item in result["items"]:
                    table_data.append(
                        {
                            "id": item.id,
                            "name": item.name,
                            "email": getattr(item, "email", ""),
                            "status": getattr(item, "status", ""),
                            "created": (
                                getattr(item, "created_at", "")[:10]
                                if hasattr(item, "created_at")
                                else ""
                            ),
                        }
                    )
                OutputFormatter.output(table_data, "table")
            else:
                OutputFormatter.output(result, ctx.obj["format"])

    asyncio.run(_list())


@cli.command()
@click.option("--page", type=int, default=1, help="Page number")
@click.option("--page-size", type=int, default=50, help="Items per page")
@click.option(
    "--status",
    type=click.Choice(["open", "in_progress", "resolved", "closed"]),
    help="Filter by ticket status",
)
@click.option(
    "--priority",
    type=click.Choice(["low", "medium", "high", "critical"]),
    help="Filter by ticket priority",
)
@click.option("--assignee", help="Filter by assignee ID")
@click.option("--client", help="Filter by client ID")
@click.option("--created-after", help="Filter by creation date (YYYY-MM-DD)")
@click.option("--created-before", help="Filter by creation date (YYYY-MM-DD)")
@click.pass_context
def list_tickets(
    ctx, page, page_size, status, priority, assignee, client, created_after, created_before
):
    """List tickets with filtering options."""

    async def _list():
        config = get_config()
        config.timeout = ctx.obj["timeout"]

        async with SuperOpsClient(config) as client_instance:
            filters = {}
            if status:
                filters["status"] = status
            if priority:
                filters["priority"] = priority
            if assignee:
                filters["assignee_id"] = assignee
            if client:
                filters["client_id"] = client
            if created_after:
                try:
                    datetime.strptime(created_after, "%Y-%m-%d")
                    filters["created_after"] = created_after
                except ValueError:
                    raise CLIError("Invalid date format. Use YYYY-MM-DD")
            if created_before:
                try:
                    datetime.strptime(created_before, "%Y-%m-%d")
                    filters["created_before"] = created_before
                except ValueError:
                    raise CLIError("Invalid date format. Use YYYY-MM-DD")

            result = await client_instance.tickets.list(
                page=page, page_size=page_size, filters=filters if filters else None
            )

            if ctx.obj["format"] == "table":
                # Format data for table display
                table_data = []
                for item in result["items"]:
                    table_data.append(
                        {
                            "id": item.id,
                            "title": getattr(item, "title", "")[:50],
                            "status": getattr(item, "status", ""),
                            "priority": getattr(item, "priority", ""),
                            "assignee": getattr(item, "assignee_name", ""),
                            "created": (
                                getattr(item, "created_at", "")[:10]
                                if hasattr(item, "created_at")
                                else ""
                            ),
                        }
                    )
                OutputFormatter.output(table_data, "table")
            else:
                OutputFormatter.output(result, ctx.obj["format"])

    asyncio.run(_list())


@cli.command()
@click.option("--title", required=True, help="Ticket title")
@click.option("--description", help="Ticket description")
@click.option("--client-id", required=True, help="Client ID for the ticket")
@click.option(
    "--priority",
    type=click.Choice(["low", "medium", "high", "critical"]),
    default="medium",
    help="Ticket priority",
)
@click.option("--assignee", help="Assignee user ID")
@click.option("--tags", help="Comma-separated list of tags")
@click.option("--due-date", help="Due date (YYYY-MM-DD)")
@click.pass_context
def create_ticket(ctx, title, description, client_id, priority, assignee, tags, due_date):
    """Create a new ticket."""

    async def _create():
        config = get_config()
        config.timeout = ctx.obj["timeout"]

        ticket_data = {"title": title, "client_id": client_id, "priority": priority.upper()}

        if description:
            ticket_data["description"] = description
        if assignee:
            ticket_data["assignee_id"] = assignee
        if tags:
            ticket_data["tags"] = [tag.strip() for tag in tags.split(",")]
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
                ticket_data["due_date"] = due_date
            except ValueError:
                raise CLIError("Invalid date format. Use YYYY-MM-DD")

        async with SuperOpsClient(config) as client:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                disable=OutputFormatter.is_pipe_mode(),
            ) as progress:
                task = progress.add_task("Creating ticket...", total=None)

                try:
                    result = await client.tickets.create(ticket_data)
                    progress.update(task, description="✓ Ticket created")
                    OutputFormatter.success(f"Created ticket with ID: {result.id}")
                    OutputFormatter.output(result.__dict__, ctx.obj["format"])
                except Exception as e:
                    progress.update(task, description="✗ Ticket creation failed")
                    raise e

    asyncio.run(_create())


@cli.command()
@click.option("--script-id", required=True, help="Script ID to execute")
@click.option("--assets", help="Comma-separated list of asset IDs")
@click.option("--sites", help="Comma-separated list of site IDs")
@click.option("--clients", help="Comma-separated list of client IDs")
@click.option("--parameters", help="Script parameters as JSON string")
@click.option("--timeout", type=int, help="Execution timeout in seconds")
@click.option("--wait", is_flag=True, help="Wait for execution to complete")
@click.pass_context
def execute_script(ctx, script_id, assets, sites, clients, parameters, timeout, wait):
    """Execute a script on specified targets."""
    if not any([assets, sites, clients]):
        raise CLIError(
            "At least one target must be specified",
            suggestions=["Use --assets, --sites, or --clients to specify targets"],
        )

    async def _execute():
        config = get_config()
        config.timeout = ctx.obj["timeout"]

        execution_params = {}

        if assets:
            execution_params["target_assets"] = [a.strip() for a in assets.split(",")]
        if sites:
            execution_params["target_sites"] = [s.strip() for s in sites.split(",")]
        if clients:
            execution_params["target_clients"] = [c.strip() for c in clients.split(",")]
        if parameters:
            try:
                execution_params["parameters"] = json.loads(parameters)
            except json.JSONDecodeError:
                raise CLIError("Invalid JSON in parameters")
        if timeout:
            execution_params["timeout_seconds"] = timeout

        async with SuperOpsClient(config) as client:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                disable=OutputFormatter.is_pipe_mode(),
            ) as progress:
                task = progress.add_task("Executing script...", total=None)

                try:
                    result = await client.scripts.execute_script(script_id, **execution_params)
                    progress.update(task, description="✓ Script execution started")

                    if wait:
                        progress.update(task, description="⏳ Waiting for completion...")
                        # Poll for completion (simplified implementation)
                        while True:
                            status = await client.scripts.get_execution_status(result.id)
                            if status.status in ["completed", "failed", "cancelled"]:
                                break
                            await asyncio.sleep(2)

                        progress.update(task, description=f"✓ Script execution {status.status}")
                        OutputFormatter.output(status.__dict__, ctx.obj["format"])
                    else:
                        OutputFormatter.success(f"Script execution started with ID: {result.id}")
                        OutputFormatter.output(result.__dict__, ctx.obj["format"])

                except Exception as e:
                    progress.update(task, description="✗ Script execution failed")
                    raise e

    asyncio.run(_execute())


@cli.command()
@click.option("--query", required=True, help="GraphQL query string")
@click.option("--variables", help="Query variables as JSON string")
@click.option("--operation-name", help="GraphQL operation name")
@click.pass_context
def query(ctx, query, variables, operation_name):
    """Execute a raw GraphQL query."""

    async def _query():
        config = get_config()
        config.timeout = ctx.obj["timeout"]

        query_variables = {}
        if variables:
            try:
                query_variables = json.loads(variables)
            except json.JSONDecodeError:
                raise CLIError("Invalid JSON in variables")

        async with SuperOpsClient(config) as client:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                disable=OutputFormatter.is_pipe_mode(),
            ) as progress:
                task = progress.add_task("Executing query...", total=None)

                try:
                    result = await client.execute_query(
                        query, query_variables, operation_name=operation_name
                    )
                    progress.update(task, description="✓ Query executed")
                    OutputFormatter.output(result, ctx.obj["format"])
                except Exception as e:
                    progress.update(task, description="✗ Query failed")
                    raise e

    asyncio.run(_query())


# Configuration management subcommand
@cli.group()
def config():
    """Configuration management commands."""
    pass


@config.command()
@click.option("--api-key", prompt=True, hide_input=True, help="SuperOps API key")
@click.option("--base-url", default="https://api.superops.com/v1", help="API base URL")
@click.option("--global", "global_config", is_flag=True, help="Create global config")
def init(api_key, base_url, global_config):
    """Initialize SuperOps configuration."""
    config_data = {"api_key": api_key, "base_url": base_url, "timeout": 30.0, "debug": False}

    if global_config:
        config_dir = Path.home() / ".config" / "superops"
        config_path = config_dir / "config.json"
    else:
        config_path = Path.cwd() / "superops.config.json"

    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=2)

    OutputFormatter.success(f"Configuration saved to {config_path}")


@config.command()
@handle_exceptions
def show():
    """Show current configuration."""
    try:
        config = get_config()
        # Don't show the API key for security
        config_dict = config.model_dump()
        config_dict["api_key"] = "***" if config_dict["api_key"] else None
        OutputFormatter.output(config_dict, "json")
    except CLIError:
        OutputFormatter.error("No configuration found")


# Shell completion setup
def setup_completion():
    """Setup shell completion."""
    import os

    shell = os.environ.get("SHELL", "").split("/")[-1]

    if shell == "bash":
        completion_script = """
_superops_cli_completion() {
    local IFS=$'\\n'
    COMPREPLY=( $(env COMP_WORDS="${COMP_WORDS[*]}" \\
                     COMP_CWORD=$COMP_CWORD \\
                     _SUPEROPS_CLI_COMPLETE=complete $1) )
    return 0
}

complete -F _superops_cli_completion -o default superops-cli
"""
    elif shell == "zsh":
        completion_script = """
#compdef superops-cli

_superops_cli_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[superops-cli] )) && return 1

    response=("${(@f)$( env COMP_WORDS="${words[*]}" \\
                        COMP_CWORD=$((CURRENT-1)) \\
                        _SUPEROPS_CLI_COMPLETE="complete_zsh" \\
                        superops-cli )}")

    for key in ${response}; do
        completions+=("$key")
    done

    _describe 'values' completions
}

compdef _superops_cli_completion superops-cli
"""
    else:
        return None

    return completion_script


@cli.command(hidden=True)
def install_completion():
    """Install shell completion."""
    completion_script = setup_completion()
    if not completion_script:
        OutputFormatter.error("Shell completion not supported for your shell")
        return

    shell = os.environ.get("SHELL", "").split("/")[-1]

    if shell == "bash":
        completion_dir = Path.home() / ".bash_completion.d"
        completion_file = completion_dir / "superops-cli"
    else:  # zsh
        completion_dir = Path.home() / ".zsh" / "completions"
        completion_file = completion_dir / "_superops-cli"

    completion_dir.mkdir(parents=True, exist_ok=True)

    with open(completion_file, "w") as f:
        f.write(completion_script)

    OutputFormatter.success(f"Shell completion installed to {completion_file}")
    console.print(f"[yellow]Please restart your shell or run:[/yellow]")
    console.print(f"  source {completion_file}")


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        if "--debug" in sys.argv:
            console.print_exception()
        else:
            OutputFormatter.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
