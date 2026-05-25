#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network Management Module for Coffee Script
Provides network interface monitoring and status display
"""

import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .theme import get_palette


@dataclass
class NetworkInterface:
    """Data class for network interface information."""
    
    type: str
    name: str
    ipv4: str
    ipv6: str
    mac: str
    order: str


class NetworkManager:
    """Manages network interface monitoring and status reporting."""
    
    def __init__(self) -> None:
        """Initialize the NetworkManager."""
        pass
    
    def get_network_panel(self, details: str = "terse") -> Panel:
        """Get network panel using the original implementation."""
        return get_network_panel(details=details)

def get_network_panel(details: str = "terse") -> Panel:
    """
    Fetch network interface data from system_profiler (JSON), parse out
    Interface Type, Name, IPv4, IPv6, MAC, and Order, then display in a Rich table.

    details="all":   Active interfaces (non-empty IPv4) appear first in normal text,
                     followed by inactive interfaces (dim).
    details="terse": Always shows Wi-Fi (with 'n/a' if no IPv4) plus all other
                     interfaces with a valid IPv4. Pads to at least 6 table rows.
    """
    palette = get_palette()

    try:
        # 1) Fetch JSON data from system_profiler
        sp_output = subprocess.check_output(
            ["system_profiler", "SPNetworkDataType", "-json"],
            text=True,
            stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        print("Error: system_profiler command not found. Are you on macOS?")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running system_profiler: {e}")
        sys.exit(1)
    
    # 2) Parse the JSON output into a Python dict
    try:
        data = json.loads(sp_output)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from system_profiler: {e}")
        sys.exit(1)
    
    # "SPNetworkDataType" should be a list of interface entries
    interfaces = data.get("SPNetworkDataType", [])

    # 3) Build a list of interface info
    interfaces_info = []
    for iface in interfaces:
        interface_type = iface.get("_name", "Unknown")  # e.g. "Wi-Fi"
        interface_name = iface.get("interface", "N/A")  # e.g. "en0"

        # Gather IPv4 addresses
        ipv4_info = iface.get("IPv4", {})
        ipv4_addresses = ipv4_info.get("Addresses", [])
        ipv4_str = ", ".join(ipv4_addresses) if ipv4_addresses else ""

        # Gather IPv6 addresses
        ipv6_info = iface.get("IPv6", {})
        ipv6_addresses = ipv6_info.get("Addresses", [])
        ipv6_str = ", ".join(ipv6_addresses) if ipv6_addresses else ""

        # Attempt to fetch MAC address (try "Ethernet", fallback to "Wi-Fi")
        mac_address = (
            iface.get("Ethernet", {}).get("MAC Address") or
            iface.get("Wi-Fi", {}).get("MAC Address") or
            "N/A"
        )

        # Grab the service order if available
        service_order = iface.get("spnetwork_service_order", "N/A")

        interfaces_info.append({
            "type": interface_type,
            "name": interface_name,
            "ipv4": ipv4_str,
            "ipv6": ipv6_str,
            "mac": mac_address,
            "order": service_order,
        })

    # 4) Separate active (non-empty IPv4) vs. inactive (empty IPv4)
    active_interfaces = []
    inactive_interfaces = []
    interfaces_info.sort(key=lambda x: x["order"])
    for info in interfaces_info:
        if info["ipv4"]:
            active_interfaces.append(info)
        else:
            inactive_interfaces.append(info)

    # 5) Create a Rich table
    table = Table(
        collapse_padding=True,
        padding=[0, 1],
        pad_edge=False,
        show_header=True,
        show_footer=False,
        show_edge=False,
        show_lines=False,
        row_styles=[palette.table_row_even, palette.table_row_odd],
        box=box.MINIMAL,
        border_style=palette.border_secondary
    )

    table.add_column("Interface Type", style=palette.accent_cyan, no_wrap=True)
    table.add_column("Interface", style=palette.accent_magenta, no_wrap=True, justify="center")
    table.add_column("IPv4 Address", style=palette.accent_green, no_wrap=True, justify="center")

    # 6) Add rows based on detail level
    MIN_ROWS = 6

    if details == "all":
        row_num = 1
        num_rows = len(active_interfaces)
        for info in active_interfaces:
            table.add_row(
                info["type"],
                info["name"],
                info["ipv4"],
                style="none",
                end_section=(row_num == num_rows)
            )
            row_num += 1

        for info in inactive_interfaces:
            table.add_row(
                info["type"],
                info["name"],
                info["ipv4"],
                style="dim"
            )
    else:  # terse
        wifi = next((i for i in interfaces_info if i["type"] == "Wi-Fi"), None)

        terse_rows = []
        # Wi-Fi always first; show "n/a" when it has no IPv4
        if wifi is not None:
            terse_rows.append({**wifi, "ipv4": wifi["ipv4"] or "n/a"})
        # All other active interfaces (Wi-Fi already included if it was active)
        for info in active_interfaces:
            if wifi is not None and info["name"] == wifi["name"]:
                continue
            terse_rows.append(info)

        num_rows = len(terse_rows)
        for idx, info in enumerate(terse_rows):
            table.add_row(
                info["type"],
                info["name"],
                info["ipv4"],
                end_section=(idx == num_rows - 1 and num_rows >= MIN_ROWS)
            )

        # Pad to minimum row count
        for _ in range(max(0, MIN_ROWS - num_rows)):
            table.add_row("", "", "")

    # 7) Print the table
    return Panel(
        table,
        title=f"[{palette.text_highlight}]\U000f06f3[/{palette.text_highlight}]  [{palette.accent_green}]Network Interfaces[/{palette.accent_green}]",
        border_style=palette.border_primary,
        expand=False
    )


# Main function
if __name__ == "__main__":
    console = Console()
    console.print(get_network_panel())