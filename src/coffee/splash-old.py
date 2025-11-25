#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__: list[str] = ["InlineImage", "WithInlineImages", "Splash", "get_splash_panel"]

# System Imports
import base64
import math
from pathlib import Path

from rich.control import Control
from rich.measure import Measurement
from rich.panel import Panel
from rich.segment import Segment
from rich.style import Style


STR_NA: str = "[italic gray23]Not available[/italic gray23]"
STR_NEVER: str = "[italic gray23]Never[/italic gray23]"


# ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
# The credit for the following 2 Python classes goes to: Ron Frederick <ronf@timeheart.net>
#     1. InlineImage() → Create renderable image with this class
#     2. WithInlineImages() → Wrapper class to embed the above images into other renderables and print to console.
# Credit:
#       Author: Ron Frederick
#     󰇮  Email: ronf@timeheart.net
#     󰖟  Website: https://github.com/ronf
#       Reference: https://github.com/Textualize/rich/discussions/384#discussioncomment-3620356
#       Web Archive: https://web.archive.org/web/20230413124424/https://github.com/Textualize/rich/discussions/384#discussioncomment-3620356
#
class InlineImage:
    def __init__(self, data, width, height, **kwargs):
        def _b64(value):
            return base64.b64encode(value).decode("ascii")

        if "name" in kwargs:
            kwargs["name"] = _b64(kwargs["name"].encode("utf-8"))
        self._data = _b64(data)
        self._width = width
        self._height = height
        self._kwargs = kwargs

    def __rich_console__(self, console, options):
        width = self._width or options.max_width
        height = self._height or options.max_height
        aspect_ratio = width / height
        if width > options.max_width:
            width = options.max_width
            height = math.ceil(width / aspect_ratio)
        if height > options.max_height:
            height = options.max_height
            width = math.ceil(height * aspect_ratio)
        kwargs = dict(self._kwargs, inline=1, width=width, height=height)
        args = ";".join(f"{k}={v}" for k, v in kwargs.items())
        ctrl = f"\x1b]1337;File={args}:{self._data}\a"
        style = Style.from_meta({"img": (ctrl, width, height)})
        yield Segment("\xa0" + height * "\n", style=style)

    def __rich_measure__(self, console, options):
        width = self._width or options.max_width
        return Measurement(width, width)


class WithInlineImages:
    def __init__(self, renderable):
        self._renderable = renderable

    def __rich_measure__(self, console, options):
        """Delegate measurement to the wrapped renderable."""
        # Check if the renderable has __rich_measure__, otherwise use default
        if hasattr(self._renderable, '__rich_measure__'):
            return self._renderable.__rich_measure__(console, options)
        # Fallback to measuring by rendering
        from rich.measure import Measurement
        return Measurement.get(console, options, self._renderable)

    def __rich_console__(self, console, options):
        images = []
        lines = console.render_lines(
            self._renderable, options, pad=False, new_lines=True
        )

        # Convert to list so we can trim trailing empty lines
        lines = list(lines)

        # Trim trailing empty lines (lines that only contain whitespace/newlines)
        while lines and all(
            seg.text.strip() == "" and "img" not in ((seg.style.meta if seg.style else None) or {})
            for seg in lines[-1]
        ):
            lines.pop()

        row = len(lines)
        for line in lines:
            column = 0
            for segment in line:
                try:
                    ctrl, width, height = segment.style.meta["img"]
                    images.append((column, row, ctrl, width, height))
                except (AttributeError, KeyError):
                    pass
                column += segment.cell_length
            yield from line
            row -= 1
        row = 0
        column = 0
        for x, y, ctrl, width, height in images:
            yield Control.move(x - column, row - y)
            yield Segment(ctrl, control=True)
            column = x + width
            row = y - height + 1
        yield Control.move(-column, row)
# ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


class Splash:
    """Display a splash image in a Rich panel."""

    def __init__(self, image_path: Path = None, width: int = 40, height: int = 10):
        """Initialize the Splash panel.

        Args:
            image_path: Path to the image file (default: ~/etc/hot-coffee.gif)
            width: Width of the image in characters
            height: Height of the image in lines
        """
        if image_path is None:
            image_path = Path.home() / "etc" / "coffee.gif"
        self.image_path = image_path
        self.width = width
        self.height = height

    def get_splash_panel(self) -> Panel:
        """Get a panel containing the splash image.

        Returns:
            A Rich Panel with the splash image or error message
        """
        try:
            # Import theme here to avoid circular imports if needed
            from .theme import get_palette
            palette = get_palette()

            # Read the image file
            with open(self.image_path, "rb") as img_file:
                img_data = img_file.read()

            # Create inline image
            inline_image = InlineImage(img_data, width=self.width, height=self.height)

            # Wrap the image with WithInlineImages
            wrapped_image = WithInlineImages(inline_image)

            # Return panel with the image
            return Panel(
                wrapped_image,
                title=f"[{palette.text_highlight}]\uf0f4[/{palette.text_highlight}]  [{palette.accent_green}]Coffee Splash[/{palette.accent_green}]",
                border_style=palette.border_primary,
                expand=False
            )
        except FileNotFoundError:
            # If image file not found, return a panel with an error message
            return Panel(
                f"[dim]Image not found:\n{self.image_path}[/dim]",
                title="[yellow]\uf071[/yellow]  [yellow]Splash[/yellow]",
                border_style="yellow",
                expand=False
            )
        except Exception as e:
            # Handle other errors gracefully
            return Panel(
                f"[dim red]Error loading image:\n{e}[/dim red]",
                title="[red]\uf071[/red]  [red]Splash Error[/red]",
                border_style="red",
                expand=False
            )


def get_splash_panel(image_path: Path = None, width: int = 40, height: int = 20) -> Panel:
    """Convenience function to get a splash panel.

    Args:
        image_path: Path to the image file (default: ~/etc/hot-coffee.gif)
        width: Width of the image in characters
        height: Height of the image in lines

    Returns:
        A Rich Panel with the splash image
    """
    splash = Splash(image_path=image_path, width=width, height=height)
    return splash.get_splash_panel()


# ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

## USAGE EXAMPLE (for reference only, not to be included in the module):
##
# from rich.console import Console
# from rich.text import Text
# console = Console()
# with open("path_to_image.png", "rb") as img_file:
#     img_data = img_file.read()
# inline_image = InlineImage(img_data, width=40, height=20)
# text_with_image = Text("Here is an inline image:\n")
# text_with_image.append(inline_image)
# wrapped = WithInlineImages(text_with_image)
# console.print(wrapped)
#────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    """Test the splash module."""
    from rich.console import Console

    console = Console()
    try:
        panel = get_splash_panel()
        console.print(panel)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
