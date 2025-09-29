#!/usr/bin/env python3
"""
Coffee Script - Keep your system awake with style
A Python script that combines ASCII time display with power management
"""

import os
import re
import signal
import subprocess
import sys
import termios
import threading
import time
import tty
from argparse import ArgumentParser
from datetime import datetime
from typing import Dict, List, Optional

import psutil
import pytz
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.traceback import install
from rich_argparse_plus import RichHelpFormatterPlus

from .power import PowerManager, get_power_visual, get_power_data
from .network import NetworkManager, get_network_panel

# Constants
__version__ = "0.1.0"

SECONDS_PER_YEAR = 31_536_000
REFRESH_PER_SECOND = 4
SLEEP_INTERVAL = 0.4
DEFAULT_TZ = "America/New_York"
DATE_FORMAT = "%A, %B %d, %Y"
TIME_FORMAT = "%I:%M:%S %p"
SPACE_2 = "  "
SPACE_5 = "     "

# ASCII art digits for time display
DIGITS_5: Dict[str, List[str]] = {
    "0": ["▄▄▄▄▄", "█   █", "█   █", "█▄▄▄█", SPACE_5],
    "1": ["  ▄  ", " ▀█  ", "  █  ", "▄▄█▄▄", SPACE_5],
    "2": ["▄▄▄▄▄", "    █", "█▀▀▀▀", "█▄▄▄▄", SPACE_5],
    "3": ["▄▄▄▄▄", "    █", "▀▀▀▀█", "▄▄▄▄█", SPACE_5],
    "4": ["▄   ▄", "█   █", "▀▀▀▀█", "    █", SPACE_5],
    "5": ["▄▄▄▄▄", "█    ", "▀▀▀▀█", "▄▄▄▄█", SPACE_5],
    "6": ["▄▄▄▄▄", "█    ", "█▀▀▀█", "█▄▄▄█", SPACE_5],
    "7": ["▄▄▄▄▄", "    █", "    █", "    █", SPACE_5],
    "8": ["▄▄▄▄▄", "█   █", "█▀▀▀█", "█▄▄▄█", SPACE_5],
    "9": ["▄▄▄▄▄", "█   █", "▀▀▀▀█", "▄▄▄▄█", SPACE_5],
    "A": [SPACE_5, "▄▄▄▄ ", "█  █ ", "█▄▄█▄", SPACE_5],
    "M": [SPACE_5, "▄▄ ▄▄", "█ █ █", "█ █ █", SPACE_5],
    "P": [SPACE_5, "▄▄▄▄▄", "█   █", "█▄▄▄█", "█    "],
    "-": [SPACE_5, SPACE_5, "▄▄▄▄▄", SPACE_5, SPACE_5],
    "+": [SPACE_5, "  ▄  ", "▄▄█▄▄", "  █  ", SPACE_5],
    ":": [" ", "▄", " ", "▀", " "],
    " ": [SPACE_2, SPACE_2, SPACE_2, SPACE_2, SPACE_2],
}

BOOT_TIME = psutil.boot_time()
XLOG = "/usr/local/sbin/xlog"
UPTIME_HDR = "————————  U p t i m e  ———————"
UPTIME_STR = "days   hours  minutes  seconds"

PMSET_COMMANDS = [
    [XLOG, "pmset", "-a", "sleep", "0"],
    [XLOG, "pmset", "-a", "disksleep", "0"],
    [XLOG, "pmset", "-a", "displaysleep", "0"],
    [XLOG, "pmset", "-a", "womp", "1"],
    [XLOG, "pmset", "-a", "ring", "0"],
    [XLOG, "pmset", "-a", "powernap", "0"],
]

CONSOLE = Console(color_system="truecolor", force_interactive=True, force_terminal=True)
ERROR_CONSOLE = Console(
    stderr=True, color_system="truecolor", force_interactive=False, force_terminal=True
)

STOP_EVENT = threading.Event()


def n2s(n: int, d: int) -> str:
    """Convert a number `n` to a zero-padded string of `d` width with styling.
    
    Args:
        n: The number to format
        d: The desired width for zero-padding
        
    Returns:
        A formatted string with Rich markup for styling
    """
    padded = f"{n:0{d}d}"
    m = re.match(r"^(0*)($|[1-9]\d*$)", padded)
    if not m:
        # Fallback if regex fails
        return f"[bold cyan]{padded}[/bold cyan]"
    s = f"[#666666]{m.group(1)}[/#666666]" if m.group(1) else ""
    s += f"[bold cyan]{m.group(2)}[/bold cyan]" if m.group(2) else ""
    return s


def get_uptime_str(up_for: int) -> str:
    """Get a formatted uptime string from elapsed seconds.
    
    Args:
        up_for: Number of seconds since system boot
        
    Returns:
        Formatted uptime string with Rich markup
    """
    days = int(up_for // 86400)
    hours = int((up_for % 86400) // 3600)
    minutes = int((up_for % 3600) // 60)
    seconds = int(up_for % 60)
    return f"{n2s(days, 4)}     {n2s(hours, 2)}      {n2s(minutes, 2)}       {n2s(seconds, 2)}  "


def wait_for_keypress() -> None:
    """Wait for a keypress to stop the program."""
    try:
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            sys.stdin.read(1)  # Read a single character
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        STOP_EVENT.set()
    except Exception as e:
        ERROR_CONSOLE.print(
            f"[bold red]⚠️  Error while waiting for keypress: {e}[/bold red]",
            soft_wrap=True,
        )
        ERROR_CONSOLE.print_exception()
        STOP_EVENT.set()


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def configure_power_settings() -> None:
    """Configure macOS power management settings."""
    if sys.platform != "darwin":
        print("⚠️  Power management settings only work on macOS")
        return

    for cmd in PMSET_COMMANDS:
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            ERROR_CONSOLE.print(
                f"[bold red]⚠️  Failed to execute command {cmd}: {e}[/bold red]",
                soft_wrap=True,
            )
            ERROR_CONSOLE.print_exception()
        except FileNotFoundError as e:
            ERROR_CONSOLE.print(
                f"[bold red]⚠️  Command not found: {cmd[0]} - {e}[/bold red]",
                soft_wrap=True,
            )
            ERROR_CONSOLE.print_exception()
        except Exception as e:
            ERROR_CONSOLE.print(
                f"[bold red]⚠️  Unexpected error while configuring power settings: {e}[/bold red]",
                soft_wrap=True,
            )
            ERROR_CONSOLE.print_exception()


def start_caffeinate() -> Optional[subprocess.Popen]:
    """Start the caffeinate process to prevent system sleep.
    
    Returns:
        The subprocess.Popen object if successful, None otherwise
    """
    if sys.platform == "darwin":
        try:
            return subprocess.Popen(
                ["caffeinate", "-dimsu", "-t", str(SECONDS_PER_YEAR)]
            )
        except subprocess.CalledProcessError as e:
            ERROR_CONSOLE.print(
                f"[bold red]⚠️  Failed to start caffeinate: {e}[/bold red]",
                soft_wrap=True,
            )
            ERROR_CONSOLE.print_exception()
        except FileNotFoundError as e:
            ERROR_CONSOLE.print(
                f"[bold red]⚠️  caffeinate command not found: {e}[/bold red]",
                soft_wrap=True,
            )
            ERROR_CONSOLE.print_exception()
        except Exception as e:
            ERROR_CONSOLE.print(
                f"[bold red]⚠️  Unexpected error while starting caffeinate: {e}[/bold red]",
                soft_wrap=True,
            )
            ERROR_CONSOLE.print_exception()
    else:
        print("⚠️  caffeinate only works on macOS")
    return None


def handle_interrupt(signum: int, frame) -> None:
    """Handle interrupt signals gracefully.
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    print("Interrupt received, shutting down...")
    STOP_EVENT.set()


def get_power_visual_safe() -> Panel:
    """Safely get the power visual panel.
    
    Returns:
        A Rich Panel with power information or error message
    """
    try:
        return get_power_visual(get_power_data())
    except Exception as e:
        ERROR_CONSOLE.print(f"⚠️  Error while fetching power visual: {e}")
        return Panel("⚠️  Error fetching power data", border_style="red")


def get_network_panel_safe() -> Panel:
    """Safely get the network panel.
    
    Returns:
        A Rich Panel with network information or error message
    """
    try:
        return get_network_panel()
    except Exception as e:
        ERROR_CONSOLE.print(f"⚠️  Error while fetching network panel: {e}")
        return Panel("⚠️  Error fetching network data", border_style="red")


def generate_ascii_time(time_str: str) -> str:
    """Generate ASCII art representation of time string.
    
    Args:
        time_str: Time string to convert to ASCII art
        
    Returns:
        Multi-line ASCII art string
    """
    rows = []
    for i in range(5):
        line_segments = [" "]
        for char_val in time_str:
            digit_pattern = DIGITS_5.get(char_val, DIGITS_5[" "])
            if i < len(digit_pattern):
                line_segments.append(digit_pattern[i])
            else:
                line_segments.append(" ")
            line_segments.append(" ")
        rows.append("".join(line_segments))
    return "\n".join(rows)


def main() -> None:
    """Main function to run the coffee script."""
    try:
        threading.Thread(target=wait_for_keypress, daemon=True).start()
        tz: str = os.environ.get("TZ", DEFAULT_TZ)

        configure_power_settings()
        caffeinate_process = start_caffeinate()

        CONSOLE.clear()
        panel_power = get_power_visual_safe()
        panel_network = get_network_panel_safe()
        beats = 0
        ct = time.time()
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024**2
        last_power_update = ct
        last_network_update = ct

        with Live(console=CONSOLE, refresh_per_second=REFRESH_PER_SECOND) as live:
            prev_width, prev_height = (
                CONSOLE.size.width,
                CONSOLE.size.height,
            )  # Track previous dimensions
            
            while not STOP_EVENT.is_set():
                try:
                    if beats % REFRESH_PER_SECOND == 0:
                        ct = time.time()
                        process = psutil.Process(os.getpid())
                        memory_mb = process.memory_info().rss / 1024**2
                        # Detect screen dimension changes
                        curr_width, curr_height = CONSOLE.size.width, CONSOLE.size.height
                        if (curr_width, curr_height) != (prev_width, prev_height):
                            CONSOLE.clear()
                            prev_width, prev_height = curr_width, curr_height

                    now = datetime.now(pytz.timezone(tz))
                    ist_now = now.astimezone(pytz.timezone("Asia/Kolkata"))
                    ist_str = ist_now.strftime(TIME_FORMAT)
                    ist_dt_str = ist_now.strftime(DATE_FORMAT)
                    time_str = now.strftime(TIME_FORMAT)
                    up_for = ct - BOOT_TIME

                    big_time = generate_ascii_time(time_str)
                    date_str = now.strftime(DATE_FORMAT)
                    uptime = get_uptime_str(up_for)
                    
                    panel_time = Panel(
                        (
                            f"{big_time}\n"
                            f"[dim green]{UPTIME_HDR}  ——————  I S T  🇮🇳  —————[/dim green]\n"
                            f"[cyan]{uptime}[/cyan]       [#ffffff]{ist_str}[/#ffffff]\n"
                            f"[#666666]{UPTIME_STR}[/#666666]  [#ffff00]{ist_dt_str}[/#ffff00]"
                        ),
                        expand=False,
                        border_style="dim green",
                        title=f"\uf0f4  [#ffff00]{date_str}[/#ffff00]",
                        title_align="center",
                        subtitle=f"[#666666]\U000f035b {memory_mb:.2f} MB[/#666666] — [#666666]\U000f124a {tz}[/#666666]",
                        subtitle_align="right",
                    )

                    if ct - last_power_update >= 300:
                        last_power_update = ct
                        panel_power = get_power_visual_safe()

                    if ct - last_network_update >= 3600:
                        last_network_update = ct
                        panel_network = get_network_panel_safe()

                    cols = Columns([panel_network, panel_power, panel_time])
                    live.update(Align.right(cols), refresh=True)
                    time.sleep(SLEEP_INTERVAL)
                    beats += 1
                except Exception as e:
                    ERROR_CONSOLE.print(
                        f"[bold red]⚠️  Error in main loop: {e}[/bold red]",
                        soft_wrap=True,
                    )
                    ERROR_CONSOLE.print_exception()
                    STOP_EVENT.set()
    except Exception as e:
        ERROR_CONSOLE.print(
            f"[bold red]⚠️  Unexpected error in main: {e}[/bold red]", soft_wrap=True
        )
        ERROR_CONSOLE.print_exception()
    finally:
        # Clean up caffeinate process
        if 'caffeinate_process' in locals() and caffeinate_process:
            try:
                caffeinate_process.terminate()
            except:
                pass
        ERROR_CONSOLE.clear()


if __name__ == "__main__":
    # Enable rich traceback for better error visualization
    install(show_locals=True)

    # Register signal handlers
    signal.signal(signal.SIGINT, handle_interrupt)
    signal.signal(signal.SIGTERM, handle_interrupt)

    parser = ArgumentParser(
        description="Coffee Script - Keep your system awake with style.",
        allow_abbrev=True,
        exit_on_error=True,
        formatter_class=RichHelpFormatterPlus,
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    
    args = parser.parse_args()
    try:
        main()
    except Exception as e:
        ERROR_CONSOLE.print(
            f"[bold red]An unexpected error occurred: {e}[/bold red]", soft_wrap=True
        )
        ERROR_CONSOLE.print_exception()