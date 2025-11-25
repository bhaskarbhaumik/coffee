#!/usr/bin/env python3
"""Computer information utilities for Coffee Script."""

import re
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any

from rich.panel import Panel
from rich.table import Table

from .theme import get_palette

# Configuration constants
CACHE_DIR = Path.home() / ".cache" / "system_profile"
CACHE_FILE = CACHE_DIR / "cached.system_profile.computer_info.json"

cache_mtime = 0.0


class ComputerManager:
    """Manages computer information operations and data retrieval."""

    def __init__(self) -> None:
        """Initialize ComputerManager."""
        self.cache_dir: Path = CACHE_DIR
        self.cache_file: Path = CACHE_FILE
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def is_mac() -> bool:
        """Check if the system is macOS.

        Returns:
            True if running on macOS, False otherwise
        """
        return sys.platform == "darwin"

    def get_cache(self) -> Dict[str, Any]:
        """Get computer data from cache file.

        Returns:
            Cached computer data or empty dict if not available
        """
        global cache_mtime
        try:
            cache_mtime = self.cache_file.stat().st_mtime
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def write_cache(self, computer_info: Dict[str, Any]) -> None:
        """Write computer data to cache file.

        Args:
            computer_info: Computer data to cache

        Raises:
            SystemExit: If unable to write cache file
        """
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(computer_info, f, indent=2)
        except Exception as e:
            print(f"Error writing cache: {e}")
            sys.exit(1)

    def get_computer_info(self) -> Dict[str, Any]:
        """Get system_profiler output for computer information.

        Returns:
            Dictionary containing computer information

        Raises:
            SystemExit: If system_profiler command fails
        """
        try:
            result = subprocess.run(
                ["system_profiler", "-json", "SPHardwareDataType", "SPMemoryDataType",
                 "SPStorageDataType", "SPSoftwareDataType"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            print(f"Error running system_profiler: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("Error: system_profiler command not found. Are you on macOS?")
            sys.exit(1)

    def regenerate_cache(self) -> Dict[str, Any]:
        """Regenerate the cache file with fresh computer information.

        Returns:
            Dictionary containing computer data
        """
        global cache_mtime
        computer_info = self.get_computer_info()
        self.write_cache(computer_info)
        cache_mtime = time.time()
        return computer_info


def safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary values.

    Args:
        data: Dictionary to traverse
        *keys: Keys to traverse in order
        default: Default value if any key is missing

    Returns:
        Value at the nested key path or default
    """
    try:
        current = data
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError, AttributeError, IndexError):
        return default


def get_computer_panel(computer_info: Dict[str, Any] = None) -> Panel:
    """Generate computer information panel.

    Args:
        computer_info: Dictionary containing computer information

    Returns:
        Rich Panel containing formatted computer information
    """
    global cache_mtime
    palette = get_palette()

    # If no computer_info provided, try to get from cache
    if computer_info is None:
        cm = ComputerManager()
        computer_info = cm.get_cache()

    # Extract hardware information
    hardware_data = safe_get(computer_info, "SPHardwareDataType", 0, default={})
    machine_model = safe_get(hardware_data, "machine_model", default="Unknown")
    machine_name = safe_get(hardware_data, "machine_name", default="Unknown")
    model_number = safe_get(hardware_data, "model_number", default="N/A")
    serial_number = safe_get(hardware_data, "serial_number", default="N/A")
    boot_rom_version = safe_get(hardware_data, "boot_rom_version", default="N/A")
    chip_type = safe_get(hardware_data, "chip_type", default="N/A")
    number_processors = safe_get(hardware_data, "number_processors", default="N/A")
    packages = safe_get(hardware_data, "packages", default=1)

    # Parse CPU info (e.g., "proc 12:8:4" means 12 total, 8 performance, 4 efficiency)
    cpu_info = str(number_processors)
    import re
    match = re.search(r'proc\s+(\d+):(\d+):(\d+)', cpu_info)
    if match:
        total, perf, eff = match.groups()
        cpu_display = f"{total} [󱐋 {perf} + 󱗁 {eff}]"
    else:
        cpu_display = cpu_info

    # Extract memory information
    physical_memory = safe_get(hardware_data, "physical_memory", default="N/A")
    memory_type = "Unknown"
    memory_data = safe_get(computer_info, "SPMemoryDataType", default=[])
    if memory_data and len(memory_data) > 0:
        memory_type = safe_get(memory_data[0], "dimm_type", default="Unknown")

    # Extract software information
    software_data = safe_get(computer_info, "SPSoftwareDataType", 0, default={})
    os_version = safe_get(software_data, "os_version", default="N/A")
    kernel_version = safe_get(software_data, "kernel_version", default="N/A")
    boot_volume = safe_get(software_data, "boot_volume", default="N/A")
    host_name = safe_get(software_data, "local_host_name", default="N/A")
    user_name = safe_get(software_data, "user_name", default="N/A")
    user_name = re.sub(r"\s+\(.*$", "", str(user_name))
    uptime = safe_get(software_data, "uptime", default="N/A")

    # Extract current user
    import os
    login_name = os.getenv("USER", "N/A")

    # Extract storage information
    storage_data = safe_get(computer_info, "SPStorageDataType", default=[])
    disk_type = "Unknown"
    disk_filesystem = "Unknown"
    total_size = 0
    free_size = 0

    if storage_data and len(storage_data) > 0:
        storage_item = storage_data[0]
        # Get disk type from physical_drive
        physical_drive = safe_get(storage_item, "physical_drive", default={})
        disk_type = safe_get(physical_drive, "medium_type", default="Unknown")
        if disk_type != "Unknown":
            disk_type = disk_type.upper()

        disk_filesystem = safe_get(storage_item, "file_system", default="Unknown")

        # Get size information in bytes
        size_bytes = safe_get(storage_item, "size_in_bytes", default=0)
        free_bytes = safe_get(storage_item, "free_space_in_bytes", default=0)

        # Convert bytes to GB
        if size_bytes:
            total_size = size_bytes / (1024 ** 3)
        if free_bytes:
            free_size = free_bytes / (1024 ** 3)

    # Calculate disk usage percentage
    if total_size > 0:
        used_percentage = ((total_size - free_size) / total_size) * 100
        bar_length = 24
        filled = int(bar_length * used_percentage / 100)
        disk_bar = "█" * filled + "░" * (bar_length - filled)
    else:
        disk_bar = "░" * 24
        used_percentage = 0

    # Create table with two columns
    table = Table(
        show_header=False,
        show_lines=False,
        show_edge=False,
        expand=False,
        border_style=palette.border_primary,
        padding=(0, 1),
    )
    table.add_column("Left", overflow="none", justify="left")
    table.add_column("Right", overflow="none", justify="left")

    # Build the content
    left_content = (
        f"[{palette.accent_blue}][/{palette.accent_blue}]  {machine_name} [{palette.text_dim}][{machine_model}][/{palette.text_dim}]\n"
        f"[{palette.accent_blue}]󰻾[/{palette.accent_blue}]  [dim]Model....[/dim] [{palette.accent_magenta}]{model_number}[/{palette.accent_magenta}]\n"
        f"[{palette.accent_blue}][/{palette.accent_blue}]  [dim]Serial...[/dim] [{palette.accent_magenta}]{serial_number}[/{palette.accent_magenta}]\n"
        f"[{palette.accent_blue}][/{palette.accent_blue}]  [dim]Firmware.[/dim] [{palette.accent_magenta}]{boot_rom_version}[/{palette.accent_magenta}]\n"
        f"[{palette.accent_blue}]󱤓[/{palette.accent_blue}]  [dim]Chip.....[/dim] [{palette.accent_magenta}]{chip_type}[/{palette.accent_magenta}]\n"
        f"[{palette.accent_blue}][/{palette.accent_blue}]  [dim]CPU......[/dim] [{palette.accent_magenta}]{cpu_display}[/{palette.accent_magenta}]\n"
        f"[{palette.accent_blue}]󰚗[/{palette.accent_blue}]  [dim]Kernel...[/dim] [{palette.accent_magenta}]{kernel_version}[/{palette.accent_magenta}]\n"
        f"[{palette.accent_blue}][/{palette.accent_blue}]  [dim]OS.......[/dim] [{palette.accent_magenta}]{os_version}[/{palette.accent_magenta}]"
    )

    right_content = (
        f"[{palette.accent_blue}]󰍛[/{palette.accent_blue}]  [dim]Memory.[/dim] [{palette.accent_magenta}]{physical_memory} ({memory_type})[/{palette.accent_magenta}]\n"
        f"[{palette.accent_blue}][/{palette.accent_blue}]  [dim]Host...[/dim] [{palette.accent_magenta}]{host_name}[/{palette.accent_magenta}]\n"
        f"[{palette.accent_blue}][/{palette.accent_blue}]  [dim]User...[/dim] [{palette.accent_magenta}]{user_name}[/{palette.accent_magenta}]\n"
        f"[{palette.accent_blue}]󰍂[/{palette.accent_blue}]  [dim]Login..[/dim] [{palette.accent_magenta}]{login_name}[/{palette.accent_magenta}]\n"
        f"[{palette.accent_blue}]󰆼[/{palette.accent_blue}]  [dim]Disk...[/dim] [{palette.accent_magenta}]{disk_type} ({disk_filesystem})[/{palette.accent_magenta}]\n"
        f"[{palette.accent_blue}]󰪩[/{palette.accent_blue}]  [dim]Total..[/dim] [{palette.accent_magenta}]{total_size:.2f} GB[/{palette.accent_magenta}]\n"
        f"[{palette.accent_blue}]󱘤[/{palette.accent_blue}]  [dim]Free...[/dim] [{palette.accent_magenta}]{free_size:.2f} GB[/{palette.accent_magenta}]\n"
        f"[{palette.accent_blue}]{disk_bar}[/{palette.accent_blue}]"
    )

    table.add_row(left_content, right_content)

    return Panel(
        table,
        title=f"[{palette.text_highlight}]\uf0a6[/{palette.text_highlight}]  [{palette.accent_green}]Computer Info[/{palette.accent_green}]",
        border_style=palette.border_primary,
        expand=False,
    )


# Convenience functions
def is_mac() -> bool:
    """Check if system is macOS."""
    return ComputerManager.is_mac()


def regenerate_computer_cache() -> Dict[str, Any]:
    """Regenerate computer info cache using ComputerManager."""
    cm = ComputerManager()
    return cm.regenerate_cache()


if __name__ == "__main__":
    """Test the computer module."""
    from rich.console import Console

    console = Console()
    try:
        # Regenerate cache
        computer_data = regenerate_computer_cache()
        panel = get_computer_panel(computer_data)
        console.print(panel)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
