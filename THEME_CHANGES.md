# Theme System Refactoring Summary

## Overview
This refactoring centralizes all color information in a theme system that automatically detects and adapts to the terminal's light/dark mode.

## Changes Made

### 1. New File: `src/coffee/theme.py`
A comprehensive theme management system with:

#### Features:
- **Automatic theme detection** using multiple methods:
  - `COLORFGBG` environment variable
  - macOS system preferences (`defaults read -g AppleInterfaceStyle`)
  - Custom environment variables (`DARK_MODE`, `LIGHT_MODE`)
  - Defaults to dark theme if detection fails

- **Dynamic theme change listener**:
  - Monitors system theme changes every 5 seconds
  - Automatically regenerates all UI panels when theme changes
  - Seamlessly switches between light and dark mode at runtime
  - No manual intervention required

- **Color palettes** for both light and dark themes:
  - Text colors (primary, secondary, dim, highlight)
  - Accent colors (cyan, green, yellow, magenta, red, blue)
  - Background colors (primary, secondary, tertiary)
  - UI element colors (borders, status indicators)
  - Battery-specific colors

- **Improved contrast** in light theme:
  - Dark text on light backgrounds for better readability
  - Carefully chosen color values for high contrast

#### Dark Theme Colors:
- Background: `#1a1a1a`, `#2a2a2a`, `#202030`
- Text: `#ffffff` (primary), `#cccccc` (secondary), `#666666` (dim)
- Highlight: `#ffff00`
- Borders: `dim green`, `#336633`
- Table rows: `on grey11` (even), `on grey19` (odd)

#### Light Theme Colors:
- Background: `#ffffff`, `#f5f5f5`, `#e8e8e8`
- Text: `#000000` (primary), `#333333` (secondary), `#999999` (dim)
- Highlight: `#0066cc`
- Borders: `#006633`, `#339966`
- Higher contrast accent colors (e.g., `#006699` instead of `cyan`)
- Table rows: `on grey93` (even), `on grey85` (odd)

### 2. Modified: `src/coffee/main.py`
- Added imports: `from .theme import get_palette, refresh_theme`
- Updated `n2s()` function to use palette colors
- Replaced all hardcoded colors in the main panel with theme-based colors
- Panel borders, titles, and text now adapt to the theme
- **Added dynamic theme change detection** (src/coffee/main.py:295, 316-325):
  - Checks for theme changes every 5 seconds in the main event loop
  - Automatically regenerates power and network panels when theme changes
  - Clears screen and refreshes display for clean transition
  - Seamlessly updates all UI elements to match new theme

### 3. Modified: `src/coffee/power.py`
- Added import: `from .theme import get_palette`
- Removed hardcoded styling constants
- Updated `get_bar()` function to accept `is_charging` parameter and use theme colors
- Updated `get_power_visual()` function to use palette colors throughout
- Battery indicators, health info, and charger status now use themed colors

### 4. Modified: `src/coffee/network.py`
- Added import: `from .theme import get_palette`
- Removed hardcoded color variables
- Updated table styling to use palette colors
- **Fixed table row backgrounds**: Now uses theme-aware `table_row_even` and `table_row_odd` colors
  - Dark theme: Uses `grey11` and `grey19` for subtle contrast on dark backgrounds
  - Light theme: Uses `grey93` and `grey85` for subtle contrast on light backgrounds
- Network interface display now fully adapts to the theme with visible alternating row backgrounds

## Usage

### Automatic Detection
The theme system automatically detects your terminal's light/dark mode and applies the appropriate colors.

### Dynamic Theme Switching
The application automatically monitors for system theme changes and updates the UI in real-time:
- Theme changes are checked every 5 seconds
- When a change is detected, all panels are regenerated with the new theme
- The transition is seamless - no restart required
- Works on macOS when switching between light/dark appearance in System Settings

### Force a Specific Theme
You can force a specific theme in code:
```python
from coffee.theme import set_theme

# Force light theme
set_theme('light')

# Force dark theme
set_theme('dark')
```

### Access Color Palette
```python
from coffee.theme import get_palette

palette = get_palette()
color = palette.text_primary
```

### Detect and Handle Theme Changes
```python
from coffee.theme import check_theme_change, refresh_theme

# Check if theme has changed (doesn't update)
if check_theme_change():
    print("Theme has changed!")

# Refresh theme if it has changed (updates palette)
if refresh_theme():
    print("Theme was updated!")
    # Regenerate your UI components here
```

### Theme Manager API
```python
from coffee.theme import get_theme

theme = get_theme()

# Check current theme
current = theme.current_theme_name  # Returns "light" or "dark"

# Check if theme changed
if theme.has_theme_changed():
    print("System theme changed")

# Refresh theme
if theme.refresh_theme():
    print("Theme palette updated")
```

## Benefits

1. **Centralized Management**: All colors are now defined in one place
2. **Better Accessibility**: Light mode has improved contrast for better readability
3. **Automatic Adaptation**: Respects system/terminal theme preferences
4. **Dynamic Theme Switching**: Automatically updates UI when system theme changes (no restart needed)
5. **Real-time Responsiveness**: Changes detected every 5 seconds for near-instant updates
6. **Maintainability**: Easy to modify colors across the entire application
7. **Consistency**: Ensures consistent color usage throughout the codebase

## Testing

The theme system has been tested with:
- ✅ COLORFGBG environment variable detection
- ✅ Forced theme selection (light/dark)
- ✅ All palette colors defined and accessible
- ✅ Contrast differences between light and dark themes
- ✅ Dynamic theme change detection
- ✅ Theme refresh functionality
- ✅ Multiple theme switches in sequence
- ✅ Forced themes correctly ignore system changes
- ✅ Global convenience functions
- ✅ Table row background colors adapt to theme
- ✅ Syntax validation of all modified files

## Migration Notes

- All existing functionality is preserved
- No changes to the public API
- The application will automatically use the appropriate theme based on terminal settings
- Users on dark terminals will see the familiar dark theme
- Users on light terminals will see an optimized light theme with better contrast
