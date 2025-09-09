"""HUD Design System - Consistent styling utilities for CLI output.

This module provides a unified design system for HUD CLI commands,
ensuring consistent colors, formatting, and visual hierarchy across
all commands.

Color Palette:
- Gold (#c0960c): Primary brand color for headers and important elements
- Black: Standard text and underlined links
- Red: Errors and failures
- Green: Success messages
- Dim/Gray: Secondary information
"""

from __future__ import annotations

import logging
from typing import Any

import questionary
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# HUD Brand Colors
GOLD = "rgb(192,150,12)"  # #c0960c
RED = "red"
GREEN = "green"
DIM = "dim"


class HUDDesign:
    """Design system for HUD CLI output."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """Initialize the design system.

        Args:
            logger: Logger to check for log levels. If None, uses the root logger.
        """
        self._stdout_console = Console(stderr=False)
        self._stderr_console = Console(stderr=True)
        self._logger = logger or logging.getLogger()

    def header(self, title: str, icon: str = "🚀", stderr: bool = True) -> None:
        """Print a header panel with gold border.

        Args:
            title: The title text
            icon: Optional emoji icon
            stderr: If True, output to stderr (default), otherwise stdout
        """
        console = self._stderr_console if stderr else self._stdout_console
        console.print(Panel.fit(f"{icon} [bold]{title}[/bold]", border_style=GOLD))

    def section_title(self, title: str, stderr: bool = True) -> None:
        """Print a section title in gold.

        Args:
            title: The section title
            stderr: If True, output to stderr (default), otherwise stdout
        """
        console = self._stderr_console if stderr else self._stdout_console
        console.print(f"\n[bold {GOLD}]{title}[/bold {GOLD}]")

    def success(self, message: str, stderr: bool = True) -> None:
        """Print a success message.

        Args:
            message: The success message
            stderr: If True, output to stderr (default), otherwise stdout
        """
        console = self._stderr_console if stderr else self._stdout_console
        console.print(f"[{GREEN} not bold]✅ {message}[/{GREEN} not bold]")

    def error(self, message: str, stderr: bool = True) -> None:
        """Print an error message.

        Args:
            message: The error message
            stderr: If True, output to stderr (default), otherwise stdout
        """
        console = self._stderr_console if stderr else self._stdout_console
        console.print(f"[{RED} not bold]❌ {message}[/{RED} not bold]")

    def warning(self, message: str, stderr: bool = True) -> None:
        """Print a warning message.

        Args:
            message: The warning message
            stderr: If True, output to stderr (default), otherwise stdout
        """
        console = self._stderr_console if stderr else self._stdout_console
        console.print(f"[yellow]⚠️  {message}[/yellow]")

    def info(self, message: str, stderr: bool = True) -> None:
        """Print an info message.

        Args:
            message: The info message
            stderr: If True, output to stderr (default), otherwise stdout
        """
        console = self._stderr_console if stderr else self._stdout_console
        console.print(f"[default not bold]{message}[/default not bold]")

    def print(self, message: str, stderr: bool = True) -> None:
        """Print a message.

        Args:
            message: The message to print
            stderr: If True, output to stderr (default), otherwise stdout
        """
        console = self._stderr_console if stderr else self._stdout_console
        console.print(message)

    def dim_info(self, label: str, value: str, stderr: bool = True) -> None:
        """Print dimmed info with a label.

        Args:
            label: The label text
            value: The value text
            stderr: If True, output to stderr (default), otherwise stdout
        """
        console = self._stderr_console if stderr else self._stdout_console
        console.print(f"[{DIM}]{label}[/{DIM}] [default]{value}[/default]")

    def link(self, url: str, stderr: bool = True) -> None:
        """Print an underlined link.

        Args:
            url: The URL to display
            stderr: If True, output to stderr (default), otherwise stdout
        """
        console = self._stderr_console if stderr else self._stdout_console
        console.print(f"[default not bold underline]{url}[/default not bold underline]")

    def json_config(self, json_str: str, stderr: bool = True) -> None:
        """Print JSON configuration with light theme.

        Args:
            json_str: JSON string to display
            stderr: If True, output to stderr (default), otherwise stdout
        """
        # Just print the JSON as plain text to avoid any syntax coloring
        console = self._stderr_console if stderr else self._stdout_console
        console.print(f"[default not bold]{json_str}[/default not bold]")

    def key_value_table(
        self, data: dict[str, str], show_header: bool = False, stderr: bool = True
    ) -> None:
        """Print a key-value table.

        Args:
            data: Dictionary of key-value pairs
            show_header: Whether to show table header
            stderr: If True, output to stderr (default), otherwise stdout
        """
        table = Table(show_header=show_header, box=None, padding=(0, 1))
        table.add_column("Key", style=DIM, no_wrap=True)
        table.add_column("Value")

        for key, value in data.items():
            table.add_row(key, value)

        console = self._stderr_console if stderr else self._stdout_console
        console.print(table)

    def progress_message(self, message: str, stderr: bool = True) -> None:
        """Print a progress message.

        Args:
            message: The progress message
            stderr: If True, output to stderr (default), otherwise stdout
        """
        console = self._stderr_console if stderr else self._stdout_console
        console.print(f"[{DIM} not bold]{message}[/{DIM} not bold]")

    def phase(self, phase_num: int, title: str, stderr: bool = True) -> None:
        """Print a phase header (for debug command).

        Args:
            phase_num: Phase number
            title: Phase title
            stderr: If True, output to stderr (default), otherwise stdout
        """
        console = self._stderr_console if stderr else self._stdout_console
        console.print(f"\n{'=' * 80}", style=GOLD)
        console.print(f"[bold {GOLD}]PHASE {phase_num}: {title}[/bold {GOLD}]")
        console.print(f"{'=' * 80}", style=GOLD)

    def command(self, cmd: list[str], stderr: bool = True) -> None:
        """Print a command being executed.

        Args:
            cmd: Command parts as list
            stderr: If True, output to stderr (default), otherwise stdout
        """
        console = self._stderr_console if stderr else self._stdout_console
        console.print(f"[bold]$ {' '.join(cmd)}[/bold]")

    def hint(self, hint: str, stderr: bool = True) -> None:
        """Print a hint message.

        Args:
            hint: The hint text
            stderr: If True, output to stderr (default), otherwise stdout
        """
        console = self._stderr_console if stderr else self._stdout_console
        console.print(f"\n[yellow]💡 Hint: {hint}[/yellow]")

    def status_item(
        self,
        label: str,
        value: str,
        status: str = "success",
        primary: bool = False,
        stderr: bool = True,
    ) -> None:
        """Print a status item with indicator.

        Args:
            label: The label text
            value: The value text
            status: Status type - "success" (✓), "error" (✗), "warning" (⚠), "info" (•)
            primary: If True, highlight the value as primary
            stderr: If True, output to stderr (default), otherwise stdout
        """
        indicators = {
            "success": f"[{GREEN} not bold]✓[/{GREEN} not bold]",
            "error": f"[{RED} not bold]✗[/{RED} not bold]",
            "warning": "[yellow]⚠[/yellow]",
            "info": f"[{DIM}]•[/{DIM}]",
        }

        indicator = indicators.get(status, indicators["info"])
        console = self._stderr_console if stderr else self._stdout_console

        if primary:
            console.print(f"{indicator} {label}: [bold cyan]{value}[/bold cyan]")
        else:
            console.print(f"{indicator} {label}: {value}")

    def command_example(
        self, command: str, description: str | None = None, stderr: bool = True
    ) -> None:
        """Print a command example with cyan highlighting.

        Args:
            command: The command to show
            description: Optional description after the command
            stderr: If True, output to stderr (default), otherwise stdout
        """
        console = self._stderr_console if stderr else self._stdout_console
        if description:
            console.print(f"  [cyan]{command}[/cyan]  # {description}")
        else:
            console.print(f"  [cyan]{command}[/cyan]")

    # Exception rendering utilities
    def render_support_hint(self, stderr: bool = True) -> None:
        """Render a standard support message for users encountering issues."""
        support = (
            "If this looks like an issue with the sdk, please make a github issue at "
            "https://github.com/hud-evals/hud-python/issues"
        )
        self.info(support, stderr=stderr)

    def render_exception(self, error: BaseException, *, stderr: bool = True) -> None:
        """Render exceptions consistently using the HUD design system.

        - Shows exception type and message
        - Displays structured hints if present on the exception (e.g., HudException.hints)
        - Prints a link to open an issue for SDK problems
        """
        try:
            from hud.shared.exceptions import HudRequestError  # lazy import
        except Exception:
            # Keep type available for isinstance guards below without import-time dependency
            HudRequestError = tuple()  # type: ignore

        # Header with exception type
        ex_type = type(error).__name__
        message = getattr(error, "message", "") or str(error) or ex_type
        self.error(f"{ex_type}: {message}", stderr=stderr)

        # Specialized details for request errors
        if isinstance(error, HudRequestError):  # type: ignore[arg-type]
            details: dict[str, str] = {}
            status_code = getattr(error, "status_code", None)
            if status_code is not None:
                details["Status"] = str(status_code)
            response_text = getattr(error, "response_text", None)
            if response_text:
                # Limit very long responses
                trimmed = response_text[:500] + ("..." if len(response_text) > 500 else "")
                details["Response"] = trimmed
            response_json = getattr(error, "response_json", None)
            if response_json and not details.get("Response"):
                details["Response JSON"] = str(response_json)
            if details:
                self.key_value_table(details, show_header=False, stderr=stderr)

        # Structured hints, if available
        hints = getattr(error, "hints", None)
        if hints:
            try:
                from hud.shared.hints import render_hints  # lazy import

                render_hints(hints, design=self)
            except Exception as render_error:
                self.debug(f"Failed to render hints: {render_error}")

        # Standard support hint
        self.render_support_hint(stderr=stderr)

    @property
    def console(self) -> Console:
        """Get the stderr console for direct access when needed."""
        return self._stderr_console

    def set_verbose(self, verbose: bool) -> None:
        """Set the logging level based on verbose flag.

        Args:
            verbose: If True, show INFO level messages. If False, only show WARNING and above.
        """
        if verbose:
            self._logger.setLevel(logging.INFO)
        else:
            self._logger.setLevel(logging.WARNING)

    # Logging-aware methods that check logging levels before printing

    def debug(self, message: str, stderr: bool = True) -> None:
        """Print a debug message only if DEBUG logging is enabled.

        Args:
            message: The debug message
            stderr: If True, output to stderr (default), otherwise stdout
        """
        if self._logger.isEnabledFor(logging.DEBUG):
            self.dim_info("[DEBUG]", message, stderr=stderr)

    def info_log(self, message: str, stderr: bool = True) -> None:
        """Print an info message only if INFO logging is enabled.

        Args:
            message: The info message
            stderr: If True, output to stderr (default), otherwise stdout
        """
        if self._logger.isEnabledFor(logging.INFO):
            self.info(message, stderr=stderr)

    def progress_log(self, message: str, stderr: bool = True) -> None:
        """Print a progress message only if INFO logging is enabled.

        Args:
            message: The progress message
            stderr: If True, output to stderr (default), otherwise stdout
        """
        if self._logger.isEnabledFor(logging.INFO):
            self.progress_message(message, stderr=stderr)

    def success_log(self, message: str, stderr: bool = True) -> None:
        """Print a success message only if INFO logging is enabled.

        Args:
            message: The success message
            stderr: If True, output to stderr (default), otherwise stdout
        """
        if self._logger.isEnabledFor(logging.INFO):
            self.success(message, stderr=stderr)

    def warning_log(self, message: str, stderr: bool = True) -> None:
        """Print a warning message only if WARNING logging is enabled.

        Args:
            message: The warning message
            stderr: If True, output to stderr (default), otherwise stdout
        """
        if self._logger.isEnabledFor(logging.WARNING):
            self.warning(message, stderr=stderr)

    def error_log(self, message: str, stderr: bool = True) -> None:
        """Print an error message only if ERROR logging is enabled.

        Args:
            message: The error message
            stderr: If True, output to stderr (default), otherwise stdout
        """
        if self._logger.isEnabledFor(logging.ERROR):
            self.error(message, stderr=stderr)

    def select(
        self,
        message: str,
        choices: list[str | dict[str, Any]] | list[str],
        default: str | None = None,
    ) -> str:
        """Interactive selection with arrow key navigation.

        Args:
            message: The prompt message to display
            choices: List of choices. Can be strings or dicts with 'name' and 'value' keys
            default: Default selection (matches against choice name/string)

        Returns:
            The selected choice value
        """
        # Convert choices to questionary format
        q_choices = []

        for choice in choices:
            if isinstance(choice, dict):
                name = choice.get("name", str(choice.get("value", "")))
                value = choice.get("value", name)
                q_choices.append(questionary.Choice(title=name, value=value))
            else:
                q_choices.append(choice)

        result = questionary.select(
            message,
            choices=q_choices,
            instruction="(Use ↑/↓ arrows, Enter to select)",
        ).ask()

        # If no selection made (Ctrl+C or ESC), exit
        if result is None:
            raise typer.Exit(1)

        return result

    def format_tool_call(self, name: str, arguments: dict[str, Any] | None = None) -> str:
        """Format a tool call in compact HUD style.

        Args:
            name: Tool name
            arguments: Tool arguments dictionary

        Returns:
            Formatted string with Rich markup
        """
        import json

        args_str = ""
        if arguments:
            try:
                # Compact JSON representation
                args_str = json.dumps(arguments, separators=(",", ":"))
                if len(args_str) > 60:
                    args_str = args_str[:57] + "..."
            except (TypeError, ValueError):
                args_str = str(arguments)[:60]

        return f"[{GOLD}]→[/{GOLD}] [bold]{name}[/bold][{DIM}]({args_str})[/{DIM}]"

    def format_tool_result(self, content: str, is_error: bool = False) -> str:
        """Format a tool result in compact HUD style.

        Args:
            content: Result content (will be truncated if too long)
            is_error: Whether this is an error result

        Returns:
            Formatted string with Rich markup
        """
        # Truncate content if needed
        if len(content) > 80:
            content = content[:77] + "..."

        # Format with status using HUD colors
        if is_error:
            return f"  [{RED}]✗[/{RED}] [{DIM}]{content}[/{DIM}]"
        else:
            return f"  [{GREEN}]✓[/{GREEN}] {content}"


# Global design instance for convenience
design = HUDDesign()
