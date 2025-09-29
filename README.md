# ☕ Coffee Script - Keep Your System Awake with Style

A sophisticated Python CLI application that combines beautiful ASCII art time display with intelligent power management for macOS systems. Coffee Script prevents your Mac from sleeping while providing real-time system monitoring through elegant terminal interfaces.

## ✨ Features

### 🕐 Time & Uptime Display

- **Large ASCII Art Clock**: Eye-catching time display using custom block characters
- **Dual Timezone Support**: Shows local time alongside Indian Standard Time (IST)
- **System Uptime Tracking**: Beautiful uptime counter with days, hours, minutes, and seconds
- **Live Updates**: Real-time display with smooth 4Hz refresh rate
- **Memory Usage Monitoring**: Process memory consumption tracking

### 🔋 Power Management

- **Intelligent Sleep Prevention**: Uses macOS `caffeinate` to prevent system sleep
- **Power Settings Configuration**: Automatically configures optimal power management settings
- **Battery Status Monitoring**: Real-time battery percentage, charging status, and health metrics
- **Visual Battery Indicator**: Customizable battery bar with charging animations
- **AC Charger Detection**: Shows power adapter connection and wattage
- **Battery Health Analysis**: Displays cycle count, maximum capacity, and health status

### 🌐 Network Information

- **Network Interface Monitoring**: Shows all network interfaces (Wi-Fi, Ethernet, etc.)
- **IP Address Display**: IPv4 and IPv6 address information
- **Interface Status**: Active vs inactive interface highlighting
- **Service Order**: Network interface priority ordering

### 🎨 Visual Features

- **Rich Terminal UI**: Beautiful panels and tables using Rich library
- **Responsive Layout**: Automatically adapts to terminal size changes
- **Color-coded Information**: Intuitive color scheme for different data types
- **Unicode Icons**: Modern iconography throughout the interface
- **Graceful Error Handling**: Elegant error display with detailed stack traces

## 🛠 Installation

### Prerequisites

- **macOS**: This application is designed specifically for macOS systems
- **Python 3.13+**: Modern Python version with type hints support
- **Terminal**: Works best with terminals supporting true color

### Using uv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd coffee

# Install dependencies with uv
uv sync

# Run the application
uv run python main.py
```

### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd coffee

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -U psutil pytz rich rich-argparse-plus

# Run the application
python main.py
```

## 🚀 Usage

### Basic Usage

```bash
python main.py
```

### Command Line Options

```bash
python main.py --help     # Show help information
python main.py --version  # Display version information
```

### Environment Variables

- **`TZ`**: Override default timezone (default: America/New_York)

  ```bash
  TZ=Europe/London python main.py
  ```

### Controls

- **Any Key**: Press any key to gracefully exit the application
- **Ctrl+C**: Force quit (handled gracefully)

## 📁 Project Structure

```text
coffee/
├── main.py              # CLI entrypoint and main application logic
├── power.py             # Power management and battery monitoring
├── network.py           # Network interface information and display
├── pyproject.toml       # Project configuration and dependencies
├── uv.lock              # Locked dependencies for reproducible builds
├── README.md            # This documentation
├── AGENTS.md            # Development guidelines and coding standards
└── .venv/               # Virtual environment (not committed)
```

## 🔧 Technical Details

### Dependencies

- **`psutil`**: System and process utilities for monitoring
- **`pytz`**: Timezone handling and conversion
- **`rich`**: Terminal formatting and beautiful output
- **`rich-argparse-plus`**: Enhanced argument parsing with Rich integration

### macOS Integration

- **`pmset`**: Power management settings configuration
- **`caffeinate`**: System sleep prevention
- **`system_profiler`**: Hardware information retrieval

### Data Caching

- Battery information is cached for 5 minutes to reduce system calls
- Network information is cached for 1 hour
- Cache files stored in `~/.cache/system_profile/`

## 🔒 Security & Permissions

### Required Permissions

- **Terminal Access**: Full terminal control for display management
- **System Information**: Access to hardware and power information
- **Process Management**: Ability to spawn background processes

### Privilege Requirements

- **No sudo required**: Runs with user-level permissions
- **Safe Commands Only**: Uses read-only system utilities
- **Graceful Failures**: Handles permission errors elegantly

## 🧪 Development

### Code Style

- **Python 3.13+** with type hints required
- **PEP 8** compliance with 4-space indentation
- **`snake_case`** for functions and variables
- **`CapWords`** for classes
- **Comprehensive error handling** with Rich traceback

### Testing

```bash
# Testing framework (when added)
pytest -q
```

### Build Commands

```bash
# Setup development environment
uv sync

# Run with development dependencies
uv run python main.py

# Format code (when formatter is added)
uv run black .

# Type checking (when mypy is added)
uv run mypy .
```

### Adding Features

1. **Power Management**: Extend `power.py` for new battery features
2. **Network Monitoring**: Enhance `network.py` for additional network metrics
3. **Display Options**: Modify `main.py` for new visualization modes
4. **Cross-platform**: Add platform detection for non-macOS support

## 🐛 Troubleshooting

### Common Issues

#### "system_profiler command not found"

**Solution**: This application requires macOS. `system_profiler` is a macOS-specific utility.

#### "Permission denied" errors

**Solution**: Ensure the terminal has necessary permissions. No sudo required for normal operation.

#### Display corruption

**Solution**:

- Ensure terminal supports true color
- Try resizing the terminal window
- Check terminal font supports Unicode characters

#### Memory usage warnings

**Solution**: The application is lightweight but monitors its own memory usage. High usage may indicate a system issue.

### Platform Limitations

- **macOS Only**: Power management features require macOS
- **Terminal Dependent**: Requires terminal with Unicode and color support
- **System Access**: Needs access to system profiling utilities

## 📝 License

This project is licensed under the terms specified in the LICENSE file.

## 🤝 Contributing

1. **Follow Guidelines**: See `AGENTS.md` for detailed development guidelines
2. **Code Style**: Maintain PEP 8 compliance and type hints
3. **Testing**: Add tests for new features
4. **Documentation**: Update README for new functionality
5. **Commits**: Use conventional commit format

### Commit Message Format

```text
feat: add uptime formatter with zero-padding
fix: handle battery health edge cases
docs: update installation instructions
```

## 🔄 Version History

- **v0.1.0**: Initial release with basic time display and power management

## 📊 Performance

- **Startup Time**: < 1 second
- **Memory Usage**: ~15-25 MB typical
- **CPU Usage**: Minimal (<1% on modern Macs)
- **Update Frequency**: 4Hz refresh rate
- **Cache Efficiency**: 5-minute power data cache, 1-hour network cache

---

**Keep your Mac awake in style!** ☕✨
