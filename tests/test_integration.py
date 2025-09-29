"""Integration tests for the Coffee Script package."""

import pytest
from unittest.mock import Mock, patch
from coffee import main, PowerManager, NetworkManager


class TestPackageIntegration:
    """Tests for package-level integration."""
    
    def test_package_imports(self):
        """Test that all main components can be imported."""
        from coffee import (
            main,
            PowerManager,
            PowerMetrics,
            NetworkManager,
            NetworkInterface,
            get_power_data,
            get_power_visual,
            get_network_panel,
        )
        
        # Verify classes can be instantiated
        power_manager = PowerManager()
        network_manager = NetworkManager()
        
        assert power_manager is not None
        assert network_manager is not None
    
    def test_package_metadata(self):
        """Test package metadata accessibility."""
        import coffee
        
        assert hasattr(coffee, '__version__')
        assert hasattr(coffee, '__author__')
        assert hasattr(coffee, '__email__')
        assert coffee.__version__ == "0.1.0"
    
    @patch('coffee.main.subprocess.run')
    @patch('coffee.power.subprocess.run')
    @patch('coffee.network.subprocess.run')
    def test_cross_module_integration(self, mock_net_subprocess, mock_pow_subprocess, mock_main_subprocess):
        """Test integration between main, power, and network modules."""
        # Mock power data
        mock_power_result = Mock()
        mock_power_result.stdout = """
        AC Charger Information:
          Connected: Yes
          Wattage (W): 85
        Battery Information:
          Charge Remaining (mAh): 4500
          Full Charge Capacity (mAh): 5000
          Cycle Count: 150
          Condition: Normal
        """
        mock_pow_subprocess.return_value = mock_power_result
        
        # Mock network data
        mock_network_result = Mock()
        mock_network_result.stdout = """
        Network:
          Wi-Fi:
            Type: Wi-Fi
            IPv4 Addresses: 192.168.1.100
            Ethernet Address: aa:bb:cc:dd:ee:ff
        """
        mock_net_subprocess.return_value = mock_network_result
        
        # Test power manager integration
        power_manager = PowerManager()
        power_data = power_manager.get_power_data()
        assert power_data is not None
        assert power_data.ac_connected is True
        assert power_data.battery_charge == 4500
        
        # Test network manager integration
        network_manager = NetworkManager()
        interfaces = network_manager.get_network_interfaces()
        assert len(interfaces) > 0
        assert interfaces[0].name == "Wi-Fi"
        assert interfaces[0].ip_address == "192.168.1.100"
        
        # Test panel creation
        power_panel = power_manager.create_power_panel()
        network_panel = network_manager.create_network_panel()
        
        assert power_panel is not None
        assert network_panel is not None


class TestCommandLineInterface:
    """Tests for command-line interface functionality."""
    
    @patch('coffee.main.main')
    def test_main_function_callable(self, mock_main_func):
        """Test that main function can be called from package."""
        from coffee import main
        
        main()
        mock_main_func.assert_called_once()
    
    def test_cli_entry_point(self):
        """Test CLI entry point configuration."""
        # This would typically test the console script entry point
        # For now, just verify the main function exists and is callable
        from coffee.main import main
        
        assert callable(main)


class TestErrorHandling:
    """Tests for error handling across modules."""
    
    @patch('coffee.power.subprocess.run')
    def test_power_manager_error_handling(self, mock_subprocess):
        """Test power manager error handling."""
        mock_subprocess.side_effect = FileNotFoundError("system_profiler not found")
        
        power_manager = PowerManager()
        result = power_manager.get_power_data()
        
        # Should handle error gracefully and return None
        assert result is None
    
    @patch('coffee.network.subprocess.run')
    def test_network_manager_error_handling(self, mock_subprocess):
        """Test network manager error handling."""
        mock_subprocess.side_effect = FileNotFoundError("system_profiler not found")
        
        network_manager = NetworkManager()
        result = network_manager.get_network_interfaces()
        
        # Should handle error gracefully and return empty list
        assert result == []
    
    def test_safe_function_error_handling(self):
        """Test safe wrapper functions handle errors properly."""
        from coffee.main import get_power_visual_safe, get_network_panel_safe
        
        with patch('coffee.main.get_power_visual', side_effect=Exception("Test error")):
            result = get_power_visual_safe()
            assert result is not None
            assert hasattr(result, 'border_style')
        
        with patch('coffee.main.get_network_panel', side_effect=Exception("Test error")):
            result = get_network_panel_safe()
            assert result is not None
            assert hasattr(result, 'border_style')


class TestPerformance:
    """Tests for performance considerations."""
    
    @patch('coffee.power.time.time')
    @patch('coffee.power.PowerManager._run_system_profiler')
    def test_power_manager_caching(self, mock_profiler, mock_time):
        """Test that power manager caching works correctly."""
        mock_time.side_effect = [1000.0, 1100.0, 1500.0]  # Different timestamps
        mock_profiler.return_value = "Sample power data"
        
        power_manager = PowerManager()
        
        with patch.object(power_manager, '_parse_power_data') as mock_parse:
            from coffee.power import PowerMetrics
            mock_metrics = PowerMetrics()
            mock_parse.return_value = mock_metrics
            
            # First call should fetch data
            result1 = power_manager.get_power_data()
            assert mock_profiler.call_count == 1
            
            # Second call within cache period should use cache
            result2 = power_manager.get_power_data()
            assert mock_profiler.call_count == 1  # No additional call
            assert result1 == result2
            
            # Third call after cache expiry should fetch fresh data
            result3 = power_manager.get_power_data()
            assert mock_profiler.call_count == 2  # Additional call made
    
    def test_memory_usage(self):
        """Test that objects don't hold excessive references."""
        power_manager = PowerManager()
        network_manager = NetworkManager()
        
        # Basic check that objects can be created and don't immediately fail
        assert power_manager._cached_data is None
        assert network_manager is not None
        
        # Clean up references
        del power_manager
        del network_manager