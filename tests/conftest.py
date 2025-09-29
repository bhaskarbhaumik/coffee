"""Test configuration and fixtures for Coffee Script tests."""

import pytest
from unittest.mock import Mock, patch
from coffee.power import PowerMetrics
from coffee.network import NetworkInterface


@pytest.fixture
def mock_power_metrics():
    """Fixture providing sample PowerMetrics data."""
    return PowerMetrics(
        ac_connected=True,
        battery_present=True,
        battery_charge=4500,
        battery_capacity=5000,
        is_charging=False,
        cycle_count=150,
        condition="Normal",
        wattage=85,
    )


@pytest.fixture
def mock_network_interface():
    """Fixture providing sample NetworkInterface data."""
    return NetworkInterface(
        type="Wi-Fi",
        name="en0",
        ipv4="192.168.1.100",
        ipv6="",
        mac="aa:bb:cc:dd:ee:ff",
        order="1",
    )


@pytest.fixture
def mock_system_profiler_power_output():
    """Fixture providing mock system_profiler power output."""
    return """
    AC Charger Information:
      
      Connected: Yes
      ID: 0x0100
      Wattage (W): 85
      
    Battery Information:
      
      Model Information:
          Manufacturer: DP
          Device Name: bq20z451
          Pack Lot Code: 0
          PCB Lot Code: 0
          Firmware Version: 201
          Hardware Revision: 2
          Cell Revision: 102
      Charge Information:
          Charge Remaining (mAh): 4500
          Fully Charged: No
          Charging: No
          Full Charge Capacity (mAh): 5000
      Health Information:
          Cycle Count: 150
          Condition: Normal
    """


@pytest.fixture
def mock_system_profiler_network_output():
    """Fixture providing mock system_profiler network output."""
    return """
    Network:

      Wi-Fi:

          Type: Wi-Fi
          IPv4 Addresses: 192.168.1.100
          Subnet Masks: 255.255.255.0
          Router: 192.168.1.1
          DNS Server: 8.8.8.8
          DNS Server: 8.8.4.4
          Ethernet Address: aa:bb:cc:dd:ee:ff

      Ethernet:

          Type: Ethernet
          IPv4 Addresses: 
          Subnet Masks: 
          Router: 
          Ethernet Address: bb:cc:dd:ee:ff:aa
    """