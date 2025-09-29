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

# Global styling constants to match original implementation
icon_style: str = "#ffff00"
title_style: str = "#aaffaa"
border_style: str = "#336633"


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
    
    def get_network_panel(self) -> Panel:
        """Get network panel using the original implementation."""
        return get_network_panel()

def get_network_panel() -> Panel:
    """
    Fetch network interface data from system_profiler (JSON), parse out
    Interface Type, Name, IPv4, IPv6, MAC, and Order, then display in a Rich table.
    Active interfaces (non-empty IPv4) appear first in normal text,
    followed by inactive interfaces (dim).
    """
    global icon_style, title_style, border_style

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
        row_styles=["on #2a2a2a", "on #202030"], 
        box=box.MINIMAL, 
        border_style=border_style
    )

    table.add_column("Interface Type", style="cyan", no_wrap=True)
    table.add_column("Interface", style="magenta", no_wrap=True, justify="center")
    table.add_column("IPv4 Address", style="green", no_wrap=True, justify="center")

    # 6) Add rows to the table: active first (normal), then inactive (dim)
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

    # 7) Print the table
    return Panel(
        table, 
        title=f"[#ffff00]\U000f06f3[/#ffff00]  [bright_green]Network Interfaces[/bright_green]", 
        border_style="dim green", 
        expand=False
    )


# Main function
if __name__ == "__main__":
    console = Console()
    console.print(get_network_panel())