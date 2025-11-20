#!/usr/bin/env python3
"""
Theme Management Module for Coffee Script
Provides centralized color management with light/dark mode detection
"""

import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class ColorPalette:
    """Color palette for a theme variant (light or dark)."""

    # Text colors
    text_primary: str
    text_secondary: str
    text_dim: str
    text_highlight: str

    # Accent colors
    accent_cyan: str
    accent_green: str
    accent_yellow: str
    accent_magenta: str
    accent_red: str
    accent_blue: str

    # Background colors
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str

    # UI element colors
    border_primary: str
    border_secondary: str

    # Status colors
    status_success: str
    status_warning: str
    status_error: str
    status_info: str

    # Battery specific
    battery_outline: str
    battery_fill_charging: str
    battery_fill_discharging: str
    battery_background: str

    # Table specific
    table_row_even: str
    table_row_odd: str


# Dark theme palette (original colors, optimized for dark terminals)
DARK_THEME = ColorPalette(
    # Text colors
    text_primary="#ffffff",
    text_secondary="#cccccc",
    text_dim="#666666",
    text_highlight="#ffff00",

    # Accent colors
    accent_cyan="bold cyan",
    accent_green="green",
    accent_yellow="yellow",
    accent_magenta="magenta",
    accent_red="red",
    accent_blue="blue",

    # Background colors
    bg_primary="#1a1a1a",
    bg_secondary="#2a2a2a",
    bg_tertiary="#202030",

    # UI element colors
    border_primary="dim green",
    border_secondary="#336633",

    # Status colors
    status_success="green",
    status_warning="yellow",
    status_error="red",
    status_info="cyan",

    # Battery specific
    battery_outline="#666666",
    battery_fill_charging="green on #333333",
    battery_fill_discharging="white on #333333",
    battery_background="#333333",

    # Table specific (subtle alternating backgrounds for dark terminals)
    table_row_even="on grey11",  # Very dark gray
    table_row_odd="on grey19",   # Slightly lighter dark gray
)


# Light theme palette (optimized for light terminals with high contrast)
LIGHT_THEME = ColorPalette(
    # Text colors
    text_primary="#000000",
    text_secondary="#333333",
    text_dim="#999999",
    text_highlight="#0066cc",

    # Accent colors
    accent_cyan="bold #006699",
    accent_green="#006600",
    accent_yellow="#996600",
    accent_magenta="#990099",
    accent_red="#cc0000",
    accent_blue="#0066cc",

    # Background colors
    bg_primary="#ffffff",
    bg_secondary="#f5f5f5",
    bg_tertiary="#e8e8e8",

    # UI element colors
    border_primary="#006633",
    border_secondary="#339966",

    # Status colors
    status_success="#006600",
    status_warning="#cc6600",
    status_error="#cc0000",
    status_info="#0066cc",

    # Battery specific
    battery_outline="#666666",
    battery_fill_charging="#006600 on #cccccc",
    battery_fill_discharging="#333333 on #cccccc",
    battery_background="#cccccc",

    # Table specific (subtle alternating backgrounds for light terminals)
    table_row_even="on grey93",  # Very light gray
    table_row_odd="on grey85",   # Slightly darker light gray
)


class ThemeManager:
    """Manages theme selection and provides access to themed colors."""

    def __init__(self, force_theme: Optional[str] = None):
        """
        Initialize the ThemeManager.

        Args:
            force_theme: Force a specific theme ("light" or "dark").
                        If None, auto-detect from terminal.
        """
        self._force_theme = force_theme
        self._current_theme = None  # Track current theme
        self._palette = self._select_palette()
        self._current_theme = self._detect_terminal_theme() if not force_theme else force_theme

    def _detect_terminal_theme(self) -> str:
        """
        Detect if the terminal is using a light or dark theme.

        Returns:
            "light" or "dark"
        """
        # Method 1: Check COLORFGBG environment variable (set by some terminals)
        # Format is typically "foreground;background" where 0-6 is dark, 7-15 is light
        colorfgbg = os.environ.get("COLORFGBG", "")
        if colorfgbg:
            parts = colorfgbg.split(";")
            if len(parts) >= 2:
                try:
                    bg_color = int(parts[-1])
                    # Background colors 0-6 are dark, 7-15 are light
                    if bg_color >= 7:
                        return "light"
                    else:
                        return "dark"
                except ValueError:
                    pass

        # Method 2: Check macOS appearance setting (macOS only)
        if sys.platform == "darwin":
            try:
                result = subprocess.run(
                    ["defaults", "read", "-g", "AppleInterfaceStyle"],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                # If the command succeeds, it means dark mode is enabled
                if result.returncode == 0 and "Dark" in result.stdout:
                    return "dark"
                else:
                    # Command failed or returned non-Dark, assume light mode
                    return "light"
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                pass

        # Method 3: Check common environment variables
        if os.environ.get("DARK_MODE") == "1":
            return "dark"
        if os.environ.get("LIGHT_MODE") == "1":
            return "light"

        # Default to dark theme (most terminals use dark backgrounds)
        return "dark"

    def _select_palette(self) -> ColorPalette:
        """Select the appropriate color palette based on theme detection."""
        if self._force_theme:
            theme = self._force_theme.lower()
        else:
            theme = self._detect_terminal_theme()

        if theme == "light":
            return LIGHT_THEME
        else:
            return DARK_THEME

    def has_theme_changed(self) -> bool:
        """
        Check if the system theme has changed since last check.

        Returns:
            True if theme has changed, False otherwise
        """
        # Don't check if theme is forced
        if self._force_theme:
            return False

        detected_theme = self._detect_terminal_theme()
        return detected_theme != self._current_theme

    def refresh_theme(self) -> bool:
        """
        Refresh the theme by re-detecting and updating the palette.

        Returns:
            True if theme was changed, False if it remained the same
        """
        if self._force_theme:
            return False

        old_theme = self._current_theme
        new_theme = self._detect_terminal_theme()

        if old_theme != new_theme:
            self._current_theme = new_theme
            self._palette = self._select_palette()
            return True

        return False

    @property
    def current_theme_name(self) -> str:
        """Get the current theme name ('light' or 'dark')."""
        return self._current_theme

    @property
    def palette(self) -> ColorPalette:
        """Get the current color palette."""
        return self._palette

    @property
    def is_light_theme(self) -> bool:
        """Check if the current theme is light."""
        return self._palette == LIGHT_THEME

    @property
    def is_dark_theme(self) -> bool:
        """Check if the current theme is dark."""
        return self._palette == DARK_THEME

    def get_styled_text(self, text: str, color: str) -> str:
        """
        Get text with Rich markup styling.

        Args:
            text: The text to style
            color: The color from the palette

        Returns:
            Formatted string with Rich markup
        """
        return f"[{color}]{text}[/{color}]"


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme() -> ThemeManager:
    """
    Get the global theme manager instance.

    Returns:
        ThemeManager instance
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def set_theme(theme: str) -> None:
    """
    Force a specific theme.

    Args:
        theme: "light" or "dark"
    """
    global _theme_manager
    _theme_manager = ThemeManager(force_theme=theme)


def check_theme_change() -> bool:
    """
    Check if the system theme has changed.

    Returns:
        True if theme has changed, False otherwise
    """
    return get_theme().has_theme_changed()


def refresh_theme() -> bool:
    """
    Refresh the theme if it has changed.

    Returns:
        True if theme was changed and refreshed, False otherwise
    """
    return get_theme().refresh_theme()


def get_palette() -> ColorPalette:
    """
    Get the current color palette.

    Returns:
        ColorPalette instance
    """
    return get_theme().palette


# Convenience functions for common styling patterns
def style_number(text: str, is_zero_padded: bool = False) -> str:
    """Style a number with appropriate colors."""
    palette = get_palette()
    if is_zero_padded:
        return f"[{palette.text_dim}]{text}[/{palette.text_dim}]"
    else:
        return f"[{palette.accent_cyan}]{text}[/{palette.accent_cyan}]"


def style_header(text: str) -> str:
    """Style a header text."""
    palette = get_palette()
    return f"[dim {palette.accent_green}]{text}[/dim {palette.accent_green}]"


def style_highlight(text: str) -> str:
    """Style highlighted text."""
    palette = get_palette()
    return f"[{palette.text_highlight}]{text}[/{palette.text_highlight}]"


if __name__ == "__main__":
    """Test the theme module."""
    from rich.console import Console

    console = Console()
    theme = get_theme()

    console.print("\n[bold]Theme Detection Results:[/bold]")
    console.print(f"Detected theme: {'Light' if theme.is_light_theme else 'Dark'}")
    console.print(f"\n[bold]Color Palette:[/bold]")

    palette = theme.palette
    console.print(f"Primary text: [{palette.text_primary}]Sample text[/{palette.text_primary}]")
    console.print(f"Secondary text: [{palette.text_secondary}]Sample text[/{palette.text_secondary}]")
    console.print(f"Dim text: [{palette.text_dim}]Sample text[/{palette.text_dim}]")
    console.print(f"Highlight text: [{palette.text_highlight}]Sample text[/{palette.text_highlight}]")
    console.print(f"Cyan accent: [{palette.accent_cyan}]Sample text[/{palette.accent_cyan}]")
    console.print(f"Green accent: [{palette.accent_green}]Sample text[/{palette.accent_green}]")
    console.print(f"Yellow accent: [{palette.accent_yellow}]Sample text[/{palette.accent_yellow}]")
    console.print(f"Border: [{palette.border_primary}]━━━━━━━━━━[/{palette.border_primary}]")
