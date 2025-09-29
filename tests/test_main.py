"""Tests for the main module and CLI functionality."""

import pytest
import signal
import time
from unittest.mock import Mock, patch, MagicMock
from coffee.main import (
    n2s,
    get_uptime_str,
    generate_ascii_time,
    configure_power_settings,
    start_caffeinate,
    handle_interrupt,
    get_power_visual_safe,
    get_network_panel_safe,
    DIGITS_5,
    STOP_EVENT,
)


class TestUtilityFunctions:
    """Tests for utility functions in main module."""
    
    def test_n2s_formatting(self):
        """Test number to string formatting function."""
        # Test with leading zeros
        result = n2s(42, 4)
        assert "[#666666]00[/#666666]" in result
        assert "[bold cyan]42[/bold cyan]" in result
        
        # Test without leading zeros
        result = n2s(1234, 4)
        assert "[bold cyan]1234[/bold cyan]" in result
        assert "[#666666]" not in result
        
        # Test single digit
        result = n2s(5, 2)
        assert "[#666666]0[/#666666]" in result
        assert "[bold cyan]5[/bold cyan]" in result
    
    def test_get_uptime_str(self):
        """Test uptime string formatting."""
        # Test various uptime values
        uptime_seconds = 90061  # 1 day, 1 hour, 1 minute, 1 second
        result = get_uptime_str(uptime_seconds)
        
        # Check that the result contains formatted time components
        assert "0001" in result  # 1 day
        assert "01" in result    # 1 hour
        
        # Test zero uptime
        result = get_uptime_str(0)
        assert "0000" in result  # 0 days
    
    def test_generate_ascii_time(self):
        """Test ASCII time generation."""
        time_str = "12:34"
        result = generate_ascii_time(time_str)
        
        # Check that result is multi-line
        lines = result.split('\n')
        assert len(lines) == 5  # ASCII digits are 5 lines tall
        
        # Check that each character has been processed
        for char in time_str:
            if char in DIGITS_5:
                # Each line should contain some representation of the character
                assert any(len(line) > 1 for line in lines)
    
    def test_generate_ascii_time_unknown_chars(self):
        """Test ASCII time generation with unknown characters."""
        time_str = "X"  # Unknown character
        result = generate_ascii_time(time_str)
        
        lines = result.split('\n')
        assert len(lines) == 5
        # Should use space pattern for unknown characters


class TestSystemIntegration:
    """Tests for system integration functions."""
    
    @patch('coffee.main.subprocess.run')
    @patch('coffee.main.sys.platform', 'darwin')
    def test_configure_power_settings_success(self, mock_subprocess):
        """Test successful power settings configuration on macOS."""
        mock_subprocess.return_value = Mock()
        
        configure_power_settings()
        
        # Should call subprocess.run multiple times for different pmset commands
        assert mock_subprocess.call_count > 0
    
    @patch('coffee.main.subprocess.run')
    @patch('coffee.main.sys.platform', 'linux')
    def test_configure_power_settings_non_macos(self, mock_subprocess):
        """Test power settings configuration on non-macOS platform."""
        configure_power_settings()
        
        # Should not call subprocess on non-macOS
        mock_subprocess.assert_not_called()
    
    @patch('coffee.main.subprocess.run')
    def test_configure_power_settings_failure(self, mock_subprocess):
        """Test power settings configuration with subprocess failure."""
        from subprocess import CalledProcessError
        mock_subprocess.side_effect = CalledProcessError(1, "pmset")
        
        # Should not raise exception, just handle error gracefully
        configure_power_settings()
    
    @patch('coffee.main.subprocess.Popen')
    @patch('coffee.main.sys.platform', 'darwin')
    def test_start_caffeinate_success(self, mock_popen):
        """Test successful caffeinate process start on macOS."""
        mock_process = Mock()
        mock_popen.return_value = mock_process
        
        result = start_caffeinate()
        
        assert result == mock_process
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        assert "caffeinate" in args
        assert "-dimsu" in args
    
    @patch('coffee.main.subprocess.Popen')
    @patch('coffee.main.sys.platform', 'linux')
    def test_start_caffeinate_non_macos(self, mock_popen):
        """Test caffeinate process start on non-macOS platform."""
        result = start_caffeinate()
        
        assert result is None
        mock_popen.assert_not_called()
    
    @patch('coffee.main.subprocess.Popen')
    def test_start_caffeinate_failure(self, mock_popen):
        """Test caffeinate process start failure."""
        mock_popen.side_effect = FileNotFoundError()
        
        result = start_caffeinate()
        
        assert result is None


class TestSignalHandling:
    """Tests for signal handling functionality."""
    
    def test_handle_interrupt(self):
        """Test interrupt signal handler."""
        # Reset STOP_EVENT before test
        STOP_EVENT.clear()
        
        handle_interrupt(signal.SIGINT, None)
        
        # Should set the stop event
        assert STOP_EVENT.is_set()
        
        # Clean up
        STOP_EVENT.clear()


class TestSafeFunctions:
    """Tests for safe wrapper functions."""
    
    @patch('coffee.main.get_power_visual')
    @patch('coffee.main.get_power_data')
    def test_get_power_visual_safe_success(self, mock_get_data, mock_get_visual):
        """Test safe power visual function with successful call."""
        mock_panel = Mock()
        mock_get_visual.return_value = mock_panel
        mock_get_data.return_value = {"battery_present": True}
        
        result = get_power_visual_safe()
        
        assert result == mock_panel
        mock_get_data.assert_called_once()
        mock_get_visual.assert_called_once()
    
    @patch('coffee.main.get_power_visual')
    @patch('coffee.main.get_power_data')
    def test_get_power_visual_safe_exception(self, mock_get_data, mock_get_visual):
        """Test safe power visual function with exception."""
        mock_get_visual.side_effect = Exception("Test error")
        mock_get_data.return_value = {}
        
        result = get_power_visual_safe()
        
        # Should return error panel instead of raising exception
        assert result is not None
        assert hasattr(result, 'border_style')
        assert result.border_style == "red"
    
    @patch('coffee.main.get_network_panel')
    def test_get_network_panel_safe_success(self, mock_get_panel):
        """Test safe network panel function with successful call."""
        mock_panel = Mock()
        mock_get_panel.return_value = mock_panel
        
        result = get_network_panel_safe()
        
        assert result == mock_panel
        mock_get_panel.assert_called_once()
    
    @patch('coffee.main.get_network_panel')
    def test_get_network_panel_safe_exception(self, mock_get_panel):
        """Test safe network panel function with exception."""
        mock_get_panel.side_effect = Exception("Test error")
        
        result = get_network_panel_safe()
        
        # Should return error panel instead of raising exception
        assert result is not None
        assert hasattr(result, 'border_style')
        assert result.border_style == "red"


class TestMainFunction:
    """Tests for main function integration."""
    
    @patch('coffee.main.threading.Thread')
    @patch('coffee.main.configure_power_settings')
    @patch('coffee.main.start_caffeinate')
    @patch('coffee.main.CONSOLE.clear')
    @patch('coffee.main.Live')
    @patch('coffee.main.STOP_EVENT')
    def test_main_function_setup(
        self,
        mock_stop_event,
        mock_live,
        mock_clear,
        mock_start_caffeinate,
        mock_configure,
        mock_thread,
    ):
        """Test main function setup and initialization."""
        # Mock STOP_EVENT to be set immediately to exit the loop
        mock_stop_event.is_set.return_value = True
        mock_caffeinate_process = Mock()
        mock_start_caffeinate.return_value = mock_caffeinate_process
        
        # Mock Live context manager
        mock_live_instance = Mock()
        mock_live.return_value.__enter__ = Mock(return_value=mock_live_instance)
        mock_live.return_value.__exit__ = Mock(return_value=None)
        
        from coffee.main import main
        
        # Should not raise exception
        main()
        
        # Verify setup functions were called
        mock_thread.assert_called_once()
        mock_configure.assert_called_once()
        mock_start_caffeinate.assert_called_once()
        mock_clear.assert_called_once()


class TestConstants:
    """Tests for module constants and configuration."""
    
    def test_digits_5_completeness(self):
        """Test that DIGITS_5 contains all required characters."""
        required_chars = "0123456789AMP:+- "
        
        for char in required_chars:
            assert char in DIGITS_5, f"Missing digit pattern for '{char}'"
            assert len(DIGITS_5[char]) == 5, f"Digit pattern for '{char}' should have 5 lines"
    
    def test_refresh_constants(self):
        """Test refresh and timing constants."""
        from coffee.main import REFRESH_PER_SECOND, SLEEP_INTERVAL
        
        assert REFRESH_PER_SECOND > 0
        assert SLEEP_INTERVAL > 0
        assert SLEEP_INTERVAL == 1.0 / REFRESH_PER_SECOND