#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__: list[str] = ["Splash", "get_splash_panel"]

# System Imports
from pathlib import Path

from rich.panel import Panel


class Splash:
    """Display a splash ASCII art in a Rich panel."""

    def __init__(self, ascii_art_path: Path = None):
        """Initialize the Splash panel.

        Args:
            ascii_art_path: Path to the ASCII art file (default: ~/etc/coffee.aa)
        """
        if ascii_art_path is None:
            ascii_art_path = Path.home() / "etc" / "coffee.aa"
        self.ascii_art_path = ascii_art_path

    def get_splash_panel(self) -> Panel:
        """Get a panel containing the splash ASCII art.

        Returns:
            A Rich Panel with the splash ASCII art or error message
        """
        try:
            # Import theme here to avoid circular imports if needed
            from .theme import get_palette
            palette = get_palette()

            # Read the ASCII art file
            with open(self.ascii_art_path, "r", encoding="utf-8") as f:
                ascii_art = f.read().rstrip()

            # Return panel with the ASCII art
            return Panel(
                ascii_art,
                title=f"[{palette.text_highlight}]\uf0f4[/{palette.text_highlight}]  [{palette.accent_green}]Coffee[/{palette.accent_green}]",
                border_style=palette.border_primary,
                expand=False
            )
        except FileNotFoundError:
            # If ASCII art file not found, return a panel with fallback ASCII art
            fallback_art = (
                "      )  (    \n"
                "     (   ) )  \n"
                "      ) ( (   \n"
                "    _______)_ \n"
                " .-'---------|\n"
                "( C|/\/\/\/\/|\n"
                " '-./\/\/\/\/|\n"
                "   '_________'\n"
                "    '-------'"
            )
            return Panel(
                fallback_art,
                title="[yellow]\uf0f4[/yellow]  [yellow]Coffee[/yellow]",
                border_style="yellow",
                expand=False
            )
        except Exception as e:
            # Handle other errors gracefully
            return Panel(
                f"[dim red]Error loading ASCII art:\n{e}[/dim red]",
                title="[red]\uf071[/red]  [red]Splash Error[/red]",
                border_style="red",
                expand=False
            )


def get_splash_panel(ascii_art_path: Path = None) -> Panel:
    """Convenience function to get a splash panel.

    Args:
        ascii_art_path: Path to the ASCII art file (default: ~/etc/coffee-ascii-art.txt)

    Returns:
        A Rich Panel with the splash ASCII art
    """
    splash = Splash(ascii_art_path=ascii_art_path)
    return splash.get_splash_panel()


if __name__ == "__main__":
    """Test the splash module."""
    from rich.console import Console

    console = Console()
    try:
        panel = get_splash_panel()
        console.print(panel)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
