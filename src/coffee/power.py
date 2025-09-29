#!/usr/bin/env python3
"""Power management utilities for Coffee Script."""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from rich.panel import Panel
from rich.table import Table

# Configuration constants
BAR_CHARS: List[str] = [" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
CACHE_DIR = Path.home() / ".cache" / "system_profile"
CACHE_FILE = CACHE_DIR / "cached.system_profile.SPPowerDataType.json"
CACHE_TTL = 300  # 5 minutes
WIDTH_FACTOR = 10
MIN_HEIGHT = 1
MAX_HEIGHT = 4

# Styling constants
BATTERY_OUTLINE_COLOR = "#666666"
BATTERY_FILL_COLOR = "green on #333333"
ICON_STYLE = "#ffff00"
TITLE_STYLE = "#aaffaa"
BORDER_STYLE = "dim green"
UPDATED_TS_STYLE = "#666666"

cache_mtime = 0.0


class PowerManager:
    """Manages power-related operations and data retrieval."""

    def __init__(self) -> None:
        """Initialize PowerManager."""
        self.cache_dir: Path = CACHE_DIR
        self.cache_file: Path = CACHE_FILE
        self.cache_ttl: int = CACHE_TTL
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

    def is_cache_stale(self) -> bool:
        """Determine if cache file is stale.
        
        Returns:
            True if cache is stale or doesn't exist, False otherwise
        """
        global cache_mtime
        try:
            cache_mtime = self.cache_file.stat().st_mtime
            return (time.time() - cache_mtime) > self.cache_ttl
        except FileNotFoundError:
            return True

    def get_cache(self) -> Dict[str, Any]:
        """Get power data from cache file.
        
        Returns:
            Cached power data or empty dict if not available
        """
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def write_cache(self, power_info: Dict[str, Any]) -> None:
        """Write power data to cache file.
        
        Args:
            power_info: Power data to cache
            
        Raises:
            SystemExit: If unable to write cache file
        """
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(power_info, f)
        except Exception as e:
            print(f"Error writing cache: {e}")
            sys.exit(1)

    def get_power_info(self) -> Dict[str, Any]:
        """Get system_profiler (SPPowerDataType) output.
        
        Returns:
            Dictionary containing power information
            
        Raises:
            SystemExit: If system_profiler command fails
        """
        try:
            result = subprocess.run(
                ["system_profiler", "-json", "SPPowerDataType"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            pi = json.loads(result.stdout)
            pj: Dict[str, Any] = {}
            
            for p in pi.get("SPPowerDataType", []):
                name = p.get("_name")
                if name == "spbattery_information":
                    p.pop("_name", None)
                    pj["battery"] = p
                elif name == "sppower_information":
                    p.pop("_name", None)
                    pj["power"] = p
                elif name == "sppower_ac_charger_information":
                    p.pop("_name", None)
                    pj["ac_charger"] = p
                elif name == "sppower_hwconfig_information":
                    p.pop("_name", None)
                    pj["ups"] = p
            return pj
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            print(f"Error running system_profiler: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("Error: system_profiler command not found. Are you on macOS?")
            sys.exit(1)

    def get_power_data(self) -> Dict[str, Any]:
        """Get power source data (cached or fresh).
        
        Returns:
            Dictionary containing power data
        """
        global cache_mtime

        if self.is_cache_stale():
            power_info = self.get_power_info()
            self.write_cache(power_info)
            cache_mtime = time.time()
        else:
            power_info = self.get_cache()
        return power_info


def get_bar(percentage: int, height: int = 1) -> str:
    """Generate a visual battery percentage bar.
    
    Args:
        percentage: Battery percentage (0-100)
        height: Height of the bar in lines
        
    Returns:
        Formatted battery bar string with Rich markup
    """
    # Ensure percentage is within valid range
    percentage = max(0, min(100, percentage))
    
    if height < MIN_HEIGHT:
        height = MIN_HEIGHT
    elif height > MAX_HEIGHT:
        height = MAX_HEIGHT
        
    width = WIDTH_FACTOR * height
    cap_width = int(float(height - 1) * 2.0 / 3.0) + 1
    
    bat = f"  [{BATTERY_OUTLINE_COLOR}]╭{'─' * width}╮[/{BATTERY_OUTLINE_COLOR}]\n"
    
    w1 = int(percentage * width / 100)
    w2 = percentage % 10
    w3 = width - w1 - 1
    
    for i in range(height):
        if percentage == 100:
            bat += f"  [{BATTERY_OUTLINE_COLOR}]│[/{BATTERY_OUTLINE_COLOR}][{BATTERY_FILL_COLOR}]{'█' * width}[/{BATTERY_FILL_COLOR}][{BATTERY_OUTLINE_COLOR}]│{'█' * cap_width}[/{BATTERY_OUTLINE_COLOR}]\n"
        else:
            fill_char = BAR_CHARS[min(w2, len(BAR_CHARS) - 1)]
            bat += f"  [{BATTERY_OUTLINE_COLOR}]│[/{BATTERY_OUTLINE_COLOR}][{BATTERY_FILL_COLOR}]{'█' * w1}{fill_char}{' ' * w3}[/{BATTERY_FILL_COLOR}][{BATTERY_OUTLINE_COLOR}]│{'█' * cap_width}[/{BATTERY_OUTLINE_COLOR}]\n"
    
    bat += f"  [{BATTERY_OUTLINE_COLOR}]╰{'─' * width}╯[/{BATTERY_OUTLINE_COLOR}]"
    return bat


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
    except (KeyError, TypeError, AttributeError):
        return default


def get_power_visual(power_info: Dict[str, Any], height: int = 1) -> Panel:
    """Generate power status visual panel.
    
    Args:
        power_info: Dictionary containing power information
        height: Height for the battery bar
        
    Returns:
        Rich Panel containing formatted power information
    """
    global cache_mtime, BATTERY_FILL_COLOR
    
    # Safely extract battery data
    battery_percent = safe_get(
        power_info, "battery", "sppower_battery_charge_info", 
        "sppower_battery_state_of_charge", default=0
    )
    
    # Ensure battery_percent is an integer
    try:
        battery_percent = int(battery_percent)
    except (ValueError, TypeError):
        battery_percent = 0
    
    battery_charging = safe_get(
        power_info, "battery", "sppower_battery_charge_info", 
        "sppower_battery_is_charging", default="FALSE"
    ) == "TRUE"
    
    battery_warning = safe_get(
        power_info, "battery", "sppower_battery_charge_info", 
        "sppower_battery_at_warn_level", default="FALSE"
    ) == "TRUE"
    
    # Update battery fill color based on charging status
    if not battery_charging:
        BATTERY_FILL_COLOR = "white on #333333"
    else:
        BATTERY_FILL_COLOR = "green on #333333"
    
    battery_icon = "[red]\uf071[/red]" if battery_warning else "[green]\uf05a[/green]"
    battery_info = get_bar(battery_percent, height)
    
    if height > 1:
        battery_info += f"\n{battery_icon} Battery is charged at [yellow]{battery_percent}%[/yellow]"
        battery_info += f"\n{'[bold green]\U000f008f[/bold green]' if battery_charging else '[dim red]\U000f008c[/dim red]'} Battery is currently [yellow]{'charging' if battery_charging else 'discharging'}[/yellow]"
    else:
        battery_info += f"\n {battery_icon} [yellow]{battery_percent}%[/yellow] Charged"
        battery_info += f"\n {'[bold green]\U000f008f[/bold green]' if battery_charging else '[dim red]\U000f008c[/dim red]'} [yellow]{'Charging' if battery_charging else 'Discharging'}[/yellow]"

    l = 22
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cache_mtime))
    power_updated = f"{battery_info}\n[{BORDER_STYLE}]{'─' * l}[/{BORDER_STYLE}]\n"
    power_updated += f"[yellow]\ueb7c[/yellow] [bold]Last Updated[/bold]\n  [{UPDATED_TS_STYLE}]{ts}[/{UPDATED_TS_STYLE}]"

    # Battery health information
    battery_health_info_str = "[yellow]\uf0f1[/yellow] [bold]Battery Health[/bold]\n"
    health_status = safe_get(
        power_info, "battery", "sppower_battery_health_info", 
        "sppower_battery_health", default="Unknown"
    )
    health_status_display = (
        "[green]\U000f1211[/green] Good"
        if health_status == "Good"
        else f"[red]\U000f0083[/red] {health_status}"
    )
    battery_health_info_str += f"  [dim][blue]\U000f0091[/blue] Status........[/dim]{health_status_display}\n"
    
    max_capacity = safe_get(
        power_info, "battery", "sppower_battery_health_info", 
        "sppower_battery_health_maximum_capacity", default="N/A"
    )
    cycle_count = safe_get(
        power_info, "battery", "sppower_battery_health_info", 
        "sppower_battery_cycle_count", default="N/A"
    )
    
    battery_health_info_str += f"  [dim][blue]\U000f17e0[/blue] Max Capacity..[/dim][magenta]{max_capacity}[/magenta]\n"
    battery_health_info_str += f"  [dim][blue]\U000f1834[/blue] Cycle Count...[/dim][magenta]{cycle_count}[/magenta]"

    # AC charger information
    charger_connected = safe_get(
        power_info, "ac_charger", "sppower_battery_charger_connected", default="FALSE"
    ) == "TRUE"
    charger_status = (
        "[green]\U000f06a5[/green] Yes"
        if charger_connected
        else "[red]\U000f06a6[/red] No"
    )
    ac_charger_info = "[yellow]\ueb2d[/yellow] [bold]AC Charger[/bold]\n"
    ac_charger_info += f"  [dim][blue]\U000f0425[/blue] Connected?..[/dim] {charger_status}\n"
    
    charger_watts = safe_get(
        power_info, "ac_charger", "sppower_ac_charger_watts", default="N/A"
    )
    ac_charger_info += f"  [dim][blue]\uf0e7[/blue] Wattage.....[/dim] [magenta]{charger_watts} Watts[/magenta]"

    # Create table
    battery_table = Table(
        show_header=False,
        show_lines=False,
        show_edge=False,
        expand=False,
        border_style=BORDER_STYLE,
    )
    battery_table.add_column("Battery Info", overflow="none", justify="left")
    battery_table.add_column("Power Source", overflow="none", justify="left")

    l = 26
    hr = f"[{BORDER_STYLE}]{'─' * l}[/{BORDER_STYLE}]"
    power_info_str = f"{battery_health_info_str}\n{hr}\n{ac_charger_info}"
    battery_table.add_row(power_updated, power_info_str)

    return Panel(
        battery_table,
        title=f"[{ICON_STYLE}]\uf242[/{ICON_STYLE}]  [{TITLE_STYLE}]Battery Status[/{TITLE_STYLE}]",
        border_style=BORDER_STYLE,
        padding=(0, 1),
        expand=False,
    )


# Convenience functions for backwards compatibility
def is_mac() -> bool:
    """Check if system is macOS."""
    return PowerManager.is_mac()


def get_power_data() -> Dict[str, Any]:
    """Get power data using PowerManager."""
    pm = PowerManager()
    return pm.get_power_data()


if __name__ == "__main__":
    """Test the power module."""
    from rich.console import Console
    
    console = Console()
    try:
        power_data = get_power_data()
        panel = get_power_visual(power_data)
        console.print(panel)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")