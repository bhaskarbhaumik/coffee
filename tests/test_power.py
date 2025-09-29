"""Tests for the PowerManager class and power-related functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from coffee.power import PowerManager, PowerMetrics, get_power_data, get_power_visual


class TestPowerMetrics:
    """Tests for PowerMetrics dataclass."""
    
    def test_power_metrics_creation(self):
        """Test PowerMetrics creation with default values."""
        metrics = PowerMetrics()
        assert metrics.ac_connected is False
        assert metrics.battery_present is False
        assert metrics.battery_charge == 0
        assert metrics.battery_capacity == 0
        assert metrics.is_charging is False
        assert metrics.time_remaining is None
        assert metrics.cycle_count == 0
        assert metrics.condition == "Unknown"
        assert metrics.wattage is None
    
    def test_power_metrics_with_values(self, mock_power_metrics):
        """Test PowerMetrics creation with specific values."""
        assert mock_power_metrics.ac_connected is True
        assert mock_power_metrics.battery_present is True
        assert mock_power_metrics.battery_charge == 4500
        assert mock_power_metrics.battery_capacity == 5000
        assert mock_power_metrics.is_charging is False
        assert mock_power_metrics.cycle_count == 150
        assert mock_power_metrics.condition == "Normal"
        assert mock_power_metrics.wattage == 85


class TestPowerManager:
    """Tests for PowerManager class."""
    
    def test_power_manager_init(self):
        """Test PowerManager initialization."""
        manager = PowerManager()
        assert manager.cache_duration == 300
        assert manager._last_update == 0.0
        assert manager._cached_data is None
    
    @patch('coffee.power.subprocess.run')
    def test_run_system_profiler_success(self, mock_subprocess):
        """Test successful system_profiler execution."""
        mock_result = Mock()
        mock_result.stdout = "Sample output"
        mock_subprocess.return_value = mock_result
        
        manager = PowerManager()
        result = manager._run_system_profiler()
        
        assert result == "Sample output"
        mock_subprocess.assert_called_once_with(
            ["system_profiler", "SPPowerDataType"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    
    @patch('coffee.power.subprocess.run')
    def test_run_system_profiler_failure(self, mock_subprocess):
        """Test system_profiler execution failure."""
        mock_subprocess.side_effect = FileNotFoundError()
        
        manager = PowerManager()
        result = manager._run_system_profiler()
        
        assert result is None
    
    def test_parse_power_data(self, mock_system_profiler_power_output):
        """Test parsing of system_profiler power output."""
        manager = PowerManager()
        metrics = manager._parse_power_data(mock_system_profiler_power_output)
        
        assert isinstance(metrics, PowerMetrics)
        assert metrics.ac_connected is True
        assert metrics.battery_present is True
        assert metrics.battery_charge == 4500
        assert metrics.battery_capacity == 5000
        assert metrics.is_charging is False
        assert metrics.cycle_count == 150
        assert metrics.condition == "Normal"
        assert metrics.wattage == 85
    
    @patch('coffee.power.PowerManager._run_system_profiler')
    def test_get_power_data_no_cache(self, mock_profiler):
        """Test getting power data without cache."""
        mock_profiler.return_value = "Sample output"
        
        manager = PowerManager()
        with patch.object(manager, '_parse_power_data') as mock_parse:
            mock_metrics = PowerMetrics()
            mock_parse.return_value = mock_metrics
            
            result = manager.get_power_data()
            
            assert result == mock_metrics
            assert manager._cached_data == mock_metrics
            mock_profiler.assert_called_once()
            mock_parse.assert_called_once_with("Sample output")
    
    @patch('coffee.power.time.time')
    @patch('coffee.power.PowerManager._run_system_profiler')
    def test_get_power_data_with_cache(self, mock_profiler, mock_time):
        """Test getting power data with valid cache."""
        mock_time.return_value = 1000.0
        mock_metrics = PowerMetrics()
        
        manager = PowerManager()
        manager._cached_data = mock_metrics
        manager._last_update = 800.0  # 200 seconds ago, within cache duration
        
        result = manager.get_power_data()
        
        assert result == mock_metrics
        mock_profiler.assert_not_called()
    
    def test_get_battery_percentage(self, mock_power_metrics):
        """Test battery percentage calculation."""
        manager = PowerManager()
        percentage = manager.get_battery_percentage(mock_power_metrics)
        
        assert percentage == 90  # 4500/5000 * 100
    
    def test_get_battery_percentage_no_battery(self):
        """Test battery percentage with no battery present."""
        metrics = PowerMetrics(battery_present=False)
        manager = PowerManager()
        percentage = manager.get_battery_percentage(metrics)
        
        assert percentage == 0
    
    def test_get_battery_symbol_charging(self):
        """Test battery symbol when charging."""
        manager = PowerManager()
        symbol = manager.get_battery_symbol(50, is_charging=True)
        
        assert symbol == "󰂄"  # charging symbol
    
    def test_get_battery_symbol_levels(self):
        """Test battery symbols for different levels."""
        manager = PowerManager()
        
        assert manager.get_battery_symbol(100) == "󰁹"  # full
        assert manager.get_battery_symbol(90) == "󰂂"   # 90%
        assert manager.get_battery_symbol(50) == "󰁾"   # 50%
        assert manager.get_battery_symbol(10) == "󰁺"   # 10%
        assert manager.get_battery_symbol(2) == "󰂎"    # empty
    
    def test_generate_battery_bar(self):
        """Test battery bar generation."""
        manager = PowerManager()
        
        # Test full battery (green)
        bar = manager.generate_battery_bar(100, width=10)
        assert "green" in bar
        assert "100%" in bar
        
        # Test medium battery (yellow)
        bar = manager.generate_battery_bar(30, width=10)
        assert "yellow" in bar
        assert " 30%" in bar
        
        # Test low battery (red)
        bar = manager.generate_battery_bar(10, width=10)
        assert "red" in bar
        assert " 10%" in bar
    
    @patch('coffee.power.PowerManager.get_power_data')
    def test_create_power_panel_no_data(self, mock_get_data):
        """Test panel creation when no power data available."""
        mock_get_data.return_value = None
        
        manager = PowerManager()
        panel = manager.create_power_panel()
        
        assert "Power data unavailable" in str(panel.renderable)
        assert panel.border_style == "red"
    
    @patch('coffee.power.PowerManager.get_power_data')
    @patch('coffee.power.PowerManager.get_battery_percentage')
    def test_create_power_panel_with_data(self, mock_percentage, mock_get_data, mock_power_metrics):
        """Test panel creation with valid power data."""
        mock_get_data.return_value = mock_power_metrics
        mock_percentage.return_value = 90
        
        manager = PowerManager()
        panel = manager.create_power_panel()
        
        assert "AC Power Connected" in str(panel.renderable)
        assert "Battery Status" in str(panel.renderable)
        assert panel.border_style == "green"


class TestLegacyFunctions:
    """Tests for legacy compatibility functions."""
    
    @patch('coffee.power.PowerManager')
    def test_get_power_data_legacy(self, mock_manager_class):
        """Test legacy get_power_data function."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        mock_metrics = PowerMetrics(
            ac_connected=True,
            battery_present=True,
            battery_charge=4000,
            battery_capacity=5000,
        )
        mock_manager.get_power_data.return_value = mock_metrics
        
        result = get_power_data()
        
        assert result is not None
        assert result["ac_connected"] is True
        assert result["battery_present"] is True
        assert result["battery_charge"] == 4000
        assert result["battery_capacity"] == 5000
    
    @patch('coffee.power.PowerManager')
    def test_get_power_visual_legacy(self, mock_manager_class):
        """Test legacy get_power_visual function."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_panel = Mock()
        mock_manager.create_power_panel.return_value = mock_panel
        
        result = get_power_visual()
        
        assert result == mock_panel
        mock_manager.create_power_panel.assert_called_once()