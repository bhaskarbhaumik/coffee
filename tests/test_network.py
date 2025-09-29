"""Tests for the NetworkManager class and network-related functionality."""

import pytest
from unittest.mock import patch
from coffee.network import NetworkManager, NetworkInterface, get_network_panel


class TestNetworkInterface:
    """Tests for NetworkInterface dataclass."""
    
    def test_network_interface_creation(self):
        """Test NetworkInterface creation with required values."""
        interface = NetworkInterface(
            type="Ethernet",
            name="eth0", 
            ipv4="192.168.1.100",
            ipv6="",
            mac="aa:bb:cc:dd:ee:ff",
            order="1"
        )
        assert interface.type == "Ethernet"
        assert interface.name == "eth0"
        assert interface.ipv4 == "192.168.1.100"
        assert interface.ipv6 == ""
        assert interface.mac == "aa:bb:cc:dd:ee:ff"
        assert interface.order == "1"
    
    def test_network_interface_with_values(self, mock_network_interface):
        """Test NetworkInterface creation with specific values."""
        assert mock_network_interface.type == "Wi-Fi"
        assert mock_network_interface.name == "en0"
        assert mock_network_interface.ipv4 == "192.168.1.100"
        assert mock_network_interface.ipv6 == ""
        assert mock_network_interface.mac == "aa:bb:cc:dd:ee:ff"
        assert mock_network_interface.order == "1"


class TestNetworkManager:
    """Tests for NetworkManager class."""
    
    def test_network_manager_init(self):
        """Test NetworkManager initialization."""
        manager = NetworkManager()
        assert manager is not None
    
    @patch('coffee.network.subprocess.check_output')
    def test_get_network_panel_success(self, mock_subprocess):
        """Test successful get_network_panel execution."""
        # Mock JSON output from system_profiler
        mock_json_output = '''{
            "SPNetworkDataType": [
                {
                    "_name": "Wi-Fi",
                    "interface": "en0",
                    "IPv4": {"Addresses": ["192.168.1.100"]},
                    "IPv6": {"Addresses": []},
                    "Wi-Fi": {"MAC Address": "aa:bb:cc:dd:ee:ff"},
                    "spnetwork_service_order": 1
                }
            ]
        }'''
        mock_subprocess.return_value = mock_json_output
        
        manager = NetworkManager()
        panel = manager.get_network_panel()
        
        assert panel is not None
        assert hasattr(panel, 'title')


class TestGetNetworkPanel:
    """Tests for get_network_panel function."""
    
    @patch('coffee.network.subprocess.check_output')
    def test_get_network_panel_with_active_interfaces(self, mock_subprocess):
        """Test get_network_panel with active interfaces."""
        mock_json_output = '''{
            "SPNetworkDataType": [
                {
                    "_name": "Wi-Fi",
                    "interface": "en0",
                    "IPv4": {"Addresses": ["192.168.1.100"]},
                    "IPv6": {"Addresses": []},
                    "Wi-Fi": {"MAC Address": "aa:bb:cc:dd:ee:ff"},
                    "spnetwork_service_order": 1
                },
                {
                    "_name": "Ethernet",
                    "interface": "en1",
                    "IPv4": {"Addresses": []},
                    "IPv6": {"Addresses": []},
                    "Ethernet": {"MAC Address": "bb:cc:dd:ee:ff:aa"},
                    "spnetwork_service_order": 2
                }
            ]
        }'''
        mock_subprocess.return_value = mock_json_output
        
        panel = get_network_panel()
        
        assert panel is not None
        assert "Network Interfaces" in str(panel.title)
    
    @patch('coffee.network.subprocess.check_output')
    def test_get_network_panel_empty_data(self, mock_subprocess):
        """Test get_network_panel with empty data."""
        mock_json_output = '{"SPNetworkDataType": []}'
        mock_subprocess.return_value = mock_json_output
        
        panel = get_network_panel()
        
        assert panel is not None
        assert hasattr(panel, 'title')
    
    @patch('coffee.network.subprocess.check_output')
    def test_get_network_panel_subprocess_error(self, mock_subprocess):
        """Test get_network_panel handling subprocess errors."""
        mock_subprocess.side_effect = FileNotFoundError()
        
        with pytest.raises(SystemExit):
            get_network_panel()
    
    @patch('coffee.network.subprocess.check_output')
    def test_get_network_panel_json_error(self, mock_subprocess):
        """Test get_network_panel handling JSON parse errors."""
        mock_subprocess.return_value = "invalid json"
        
        with pytest.raises(SystemExit):
            get_network_panel()sts for the NetworkManager class and network-related functionality."""

import pytest
from unittest.mock import Mock, patch
from coffee.network import NetworkManager, NetworkInterface, get_network_panel


class TestNetworkInterface:
    """Tests for NetworkInterface dataclass."""
    
    def test_network_interface_creation(self):
        """Test NetworkInterface creation with required values."""
        interface = NetworkInterface(
            type="Ethernet",
            name="eth0", 
            ipv4="192.168.1.100",
            ipv6="",
            mac="aa:bb:cc:dd:ee:ff",
            order="1"
        )
        assert interface.type == "Ethernet"
        assert interface.name == "eth0"
        assert interface.ipv4 == "192.168.1.100"
        assert interface.ipv6 == ""
        assert interface.mac == "aa:bb:cc:dd:ee:ff"
        assert interface.order == "1"
    
    def test_network_interface_with_values(self, mock_network_interface):
        """Test NetworkInterface creation with specific values."""
        assert mock_network_interface.type == "Wi-Fi"
        assert mock_network_interface.name == "en0"
        assert mock_network_interface.ipv4 == "192.168.1.100"
        assert mock_network_interface.ipv6 == ""
        assert mock_network_interface.mac == "aa:bb:cc:dd:ee:ff"
        assert mock_network_interface.order == "1"


class TestNetworkManager:
    """Tests for NetworkManager class."""
    
    def test_network_manager_init(self):
        """Test NetworkManager initialization."""
        manager = NetworkManager()
        assert manager is not None
    
    @patch('coffee.network.subprocess.check_output')
    def test_get_network_panel_success(self, mock_subprocess):
        """Test successful get_network_panel execution."""
        # Mock JSON output from system_profiler
        mock_json_output = '''{
            "SPNetworkDataType": [
                {
                    "_name": "Wi-Fi",
                    "interface": "en0",
                    "IPv4": {"Addresses": ["192.168.1.100"]},
                    "IPv6": {"Addresses": []},
                    "Wi-Fi": {"MAC Address": "aa:bb:cc:dd:ee:ff"},
                    "spnetwork_service_order": 1
                }
            ]
        }'''
        mock_subprocess.return_value = mock_json_output
        
        manager = NetworkManager()
        panel = manager.get_network_panel()
        
        assert panel is not None
        assert hasattr(panel, 'title')


class TestGetNetworkPanel:
    """Tests for get_network_panel function."""
    
    @patch('coffee.network.subprocess.check_output')
    def test_get_network_panel_with_active_interfaces(self, mock_subprocess):
        """Test get_network_panel with active interfaces."""
        mock_json_output = '''{
            "SPNetworkDataType": [
                {
                    "_name": "Wi-Fi",
                    "interface": "en0",
                    "IPv4": {"Addresses": ["192.168.1.100"]},
                    "IPv6": {"Addresses": []},
                    "Wi-Fi": {"MAC Address": "aa:bb:cc:dd:ee:ff"},
                    "spnetwork_service_order": 1
                },
                {
                    "_name": "Ethernet",
                    "interface": "en1",
                    "IPv4": {"Addresses": []},
                    "IPv6": {"Addresses": []},
                    "Ethernet": {"MAC Address": "bb:cc:dd:ee:ff:aa"},
                    "spnetwork_service_order": 2
                }
            ]
        }'''
        mock_subprocess.return_value = mock_json_output
        
        panel = get_network_panel()
        
        assert panel is not None
        assert "Network Interfaces" in str(panel.title)
    
    @patch('coffee.network.subprocess.check_output')
    def test_get_network_panel_empty_data(self, mock_subprocess):
        """Test get_network_panel with empty data."""
        mock_json_output = '{"SPNetworkDataType": []}'
        mock_subprocess.return_value = mock_json_output
        
        panel = get_network_panel()
        
        assert panel is not None
        assert hasattr(panel, 'title')
    
    @patch('coffee.network.subprocess.check_output')
    def test_get_network_panel_subprocess_error(self, mock_subprocess):
        """Test get_network_panel handling subprocess errors."""
        mock_subprocess.side_effect = FileNotFoundError()
        
        with pytest.raises(SystemExit):
            get_network_panel()
    
    @patch('coffee.network.subprocess.check_output')
    def test_get_network_panel_json_error(self, mock_subprocess):
        """Test get_network_panel handling JSON parse errors."""
        mock_subprocess.return_value = "invalid json"
        
        with pytest.raises(SystemExit):
            get_network_panel()
        assert ethernet.ip_address is None
        assert ethernet.mac_address == "bb:cc:dd:ee:ff:aa"
    
    @patch('coffee.network.NetworkManager._run_system_profiler')
    def test_get_network_interfaces_success(self, mock_profiler):
        """Test getting network interfaces successfully."""
        mock_profiler.return_value = "Sample output"
        
        manager = NetworkManager()
        with patch.object(manager, '_parse_network_data') as mock_parse:
            mock_interfaces = [
                NetworkInterface("Wi-Fi", "Wi-Fi", "active"),
                NetworkInterface("Ethernet", "Ethernet", "inactive"),
            ]
            mock_parse.return_value = mock_interfaces
            
            result = manager.get_network_interfaces()
            
            assert result == mock_interfaces
            mock_profiler.assert_called_once()
            mock_parse.assert_called_once_with("Sample output")
    
    @patch('coffee.network.NetworkManager._run_system_profiler')
    def test_get_network_interfaces_failure(self, mock_profiler):
        """Test getting network interfaces when system_profiler fails."""
        mock_profiler.return_value = None
        
        manager = NetworkManager()
        result = manager.get_network_interfaces()
        
        assert result == []
    
    def test_get_active_interfaces(self):
        """Test filtering active interfaces."""
        interfaces = [
            NetworkInterface("Wi-Fi", "Wi-Fi", "active"),
            NetworkInterface("Ethernet", "Ethernet", "inactive"),
            NetworkInterface("Bluetooth", "Bluetooth", "active"),
        ]
        
        manager = NetworkManager()
        with patch.object(manager, 'get_network_interfaces', return_value=interfaces):
            active = manager.get_active_interfaces()
            
            assert len(active) == 2
            assert all(iface.status == "active" for iface in active)
            assert active[0].name == "Wi-Fi"
            assert active[1].name == "Bluetooth"
    
    def test_get_inactive_interfaces(self):
        """Test filtering inactive interfaces."""
        interfaces = [
            NetworkInterface("Wi-Fi", "Wi-Fi", "active"),
            NetworkInterface("Ethernet", "Ethernet", "inactive"),
            NetworkInterface("USB", "USB", "inactive"),
        ]
        
        manager = NetworkManager()
        with patch.object(manager, 'get_network_interfaces', return_value=interfaces):
            inactive = manager.get_inactive_interfaces()
            
            assert len(inactive) == 2
            assert all(iface.status != "active" for iface in inactive)
            assert inactive[0].name == "Ethernet"
            assert inactive[1].name == "USB"
    
    def test_get_interface_symbol(self):
        """Test getting appropriate symbols for interface types."""
        manager = NetworkManager()
        
        assert manager._get_interface_symbol("Wi-Fi") == "📶"
        assert manager._get_interface_symbol("Ethernet") == "🌐"
        assert manager._get_interface_symbol("Bluetooth") == "📲"
        assert manager._get_interface_symbol("USB") == "🔌"
        assert manager._get_interface_symbol("Thunderbolt") == "⚡"
        assert manager._get_interface_symbol("Unknown") == "🔗"
    
    def test_format_interface_row(self):
        """Test formatting interface data for table row."""
        interface = NetworkInterface(
            name="Wi-Fi",
            type="Wi-Fi",
            status="active",
            ip_address="192.168.1.100",
            mac_address="aa:bb:cc:dd:ee:ff",
            speed="100 Mbps",
        )
        
        manager = NetworkManager()
        row = manager._format_interface_row(interface)
        
        assert len(row) == 5
        assert "📶 Wi-Fi" in row[0]
        assert row[1] == "Wi-Fi"
        assert "ACTIVE" in row[2]
        assert row[3] == "192.168.1.100"
        assert "Speed: 100 Mbps" in row[4]
        assert "MAC: ee:ff" in row[4]  # Last 8 chars
    
    @patch('coffee.network.NetworkManager.get_network_interfaces')
    def test_create_network_table_no_interfaces(self, mock_get_interfaces):
        """Test creating network table with no interfaces."""
        mock_get_interfaces.return_value = []
        
        manager = NetworkManager()
        table = manager.create_network_table()
        
        assert table.title == "Network Interfaces"
        assert len(table.columns) == 5
    
    @patch('coffee.network.NetworkManager.get_network_interfaces')
    def test_create_network_table_with_interfaces(self, mock_get_interfaces):
        """Test creating network table with interfaces."""
        interfaces = [
            NetworkInterface("Wi-Fi", "Wi-Fi", "active", ip_address="192.168.1.100"),
            NetworkInterface("Ethernet", "Ethernet", "inactive"),
        ]
        mock_get_interfaces.return_value = interfaces
        
        manager = NetworkManager()
        table = manager.create_network_table()
        
        assert table.title == "Network Interfaces"
        assert len(table.columns) == 5
    
    @patch('coffee.network.NetworkManager.get_network_interfaces')
    def test_create_network_panel_no_interfaces(self, mock_get_interfaces):
        """Test creating network panel with no interfaces."""
        mock_get_interfaces.return_value = []
        
        manager = NetworkManager()
        panel = manager.create_network_panel()
        
        assert "No network interfaces found" in str(panel.renderable)
        assert panel.border_style == "red"
    
    @patch('coffee.network.NetworkManager.get_active_interfaces')
    @patch('coffee.network.NetworkManager.get_inactive_interfaces')
    @patch('coffee.network.NetworkManager.get_network_interfaces')
    def test_create_network_panel_with_interfaces(
        self, mock_get_all, mock_get_inactive, mock_get_active
    ):
        """Test creating network panel with interfaces."""
        active = [NetworkInterface("Wi-Fi", "Wi-Fi", "active", ip_address="192.168.1.100")]
        inactive = [NetworkInterface("Ethernet", "Ethernet", "inactive")]
        all_interfaces = active + inactive
        
        mock_get_all.return_value = all_interfaces
        mock_get_active.return_value = active
        mock_get_inactive.return_value = inactive
        
        manager = NetworkManager()
        panel = manager.create_network_panel()
        
        assert "Interface Summary" in str(panel.renderable)
        assert "Active: 1" in str(panel.renderable)
        assert "Inactive: 1" in str(panel.renderable)
        assert panel.border_style == "green"  # Has active interfaces
    
    def test_get_connection_summary(self):
        """Test getting connection summary."""
        interfaces = [
            NetworkInterface("Wi-Fi", "Wi-Fi", "active"),
            NetworkInterface("Ethernet", "Ethernet", "inactive"),
            NetworkInterface("Bluetooth", "Bluetooth", "active"),
        ]
        
        manager = NetworkManager()
        with patch.object(manager, 'get_network_interfaces', return_value=interfaces):
            summary = manager.get_connection_summary()
            
            assert summary["active"] == 2
            assert summary["inactive"] == 1
            assert summary["total"] == 3


class TestLegacyFunctions:
    """Tests for legacy compatibility functions."""
    
    @patch('coffee.network.NetworkManager')
    def test_get_network_panel_legacy(self, mock_manager_class):
        """Test legacy get_network_panel function."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_panel = Mock()
        mock_manager.create_network_panel.return_value = mock_panel
        
        result = get_network_panel()
        
        assert result == mock_panel
        mock_manager.create_network_panel.assert_called_once()