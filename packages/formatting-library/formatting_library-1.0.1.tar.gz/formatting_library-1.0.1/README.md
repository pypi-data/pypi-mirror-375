# Kundaliel's Formatting Library

[![PyPI version](https://badge.fury.io/py/formatting-library.svg)](https://badge.fury.io/py/formatting-library)
[![Python versions](https://img.shields.io/pypi/pyversions/formatting-library.svg)](https://pypi.org/project/formatting-library/)

A Python library for terminal text formatting, colors, and ASCII art rendering.

## Features

- RGB color support for foreground and background
- Rainbow text effects
- Image to ASCII art conversion
- Animated/slow printing
- Text color codes
- Terminal cursor control and manipulation

## Installation

```bash
pip install terminal-formatter
```

## Quick Start

```python
from terminal_formatter import rainbow_text, slow_print, img_to_ascii

# Rainbow text
print(rainbow_text("Hello, World!"))

# Slow printing with custom speed
slow_print("This text appears slowly...", speed=20)

# Convert image to ASCII art
ascii_art = img_to_ascii("path/to/image.jpg")
print(ascii_art)
```

## Documentation

### Color Functions

```python
from terminal_formatter import rgb_fore, rgb_back, RGB, RESET

# Using RGB values directly
print(f"{rgb_fore([255, 0, 0])}Red text{RESET}")

# Using RGB class
red = RGB(255, 0, 0)
print(f"{red.to_foreground()}Red text{RESET}")

# Background colors
print(f"{rgb_back([0, 255, 0])}Green background{RESET}")
```

### Rainbow Text

```python
from terminal_formatter import rainbow_text

# Foreground rainbow
print(rainbow_text("This text has rainbow colors!"))

# Background rainbow
print(rainbow_text("Rainbow background!", background=True))
```

### Terminal Control

```python
from terminal_formatter import clear_screen, set_cursor_position, Terminal

# Clear the screen
clear_screen()

# Move cursor to specific position
set_cursor_position(10, 5)  # Move cursor to row 10, column 5

# Replace current line
Terminal.replace_current_line("New text on this line")
```

### Text Formatting

```python
from terminal_formatter import align, substitute

# Text alignment
text = "Hello World"
print(align(text, 20, "center"))   # Center align in 20 characters
print(align(text, 20, "right"))    # Right align
print(align(text, 20, "left"))     # Left align

# Text substitution
original = "Hello World"
modified = substitute(original, "Python", 6)  # Replace from position 6
print(modified)  # Output: "Hello Python"
```

### Slow Printing

```python
from terminal_formatter import slow_print, PrintOptions, RGB

# Basic slow print
slow_print("This appears character by character!")

# Custom options
options = PrintOptions(
    speed=15.0,  # Characters per second
    text_color=[255, 100, 50],  # Orange text
    background_color=[0, 0, 0],  # Black background
    newline_delay=1.0  # Pause at newlines
)
slow_print("Customized slow text!", options)
```

### Text Color Codes

```python
from terminal_formatter import formatted

# Use text color codes
text = "&cRed &aGreen &9Blue &lBold &nUnderline &rReset"
print(formatted(text))

# Available codes:
# &0-&f: Colors (0=black, f=white, etc.)
# &l: Bold
# &n: Underline  
# &o: Italic
# &r: Reset
```

### Image to ASCII Art

```python
from terminal_formatter import img_to_ascii

# Convert any image to colorful ASCII art
ascii_art = img_to_ascii("photo.jpg")
print(ascii_art)

# Works with various image formats: JPG, PNG, GIF, etc.
```

### Print Boxes

```python
from terminal_formatter import ccb_gen

# Create decorative text boxes
ccb_gen("Important Message")
# Output:
# # ================= #
# # Important Message #
# # ================= #
```

## Advanced Usage

### Custom RGB Colors

```python
from terminal_formatter import RGB, ColorFuncs

# Create RGB color objects
red = RGB(255, 0, 0)
green = RGB(0, 255, 0)
blue = RGB(0, 0, 255)

# Use in dual colors (background + foreground)
print(f"{red.to_dual(blue)}Red background, blue text{RESET}")

# Static methods
print(f"{ColorFuncs.rgb_fore([128, 64, 192])}Custom purple{RESET}")
```

### Terminal Manipulation

```python
from terminal_formatter import Terminal

# Terminal control
Terminal.scroll_cursor(-3)  # Move cursor up 3 lines
Terminal.replace_line(5, "New content for line 5")
Terminal.set_cursor_position(1, 1)  # Top-left corner
```

## Color Reference

### Rainbow Colors
The built-in rainbow uses these RGB values:
- Light Red: `(255, 179, 179)`
- Light Orange: `(255, 217, 179)`
- Light Yellow: `(255, 255, 179)`
- Light Green: `(179, 255, 179)`
- Light Blue: `(179, 179, 255)`
- Light Purple: `(217, 179, 255)`

### Text Color Codes
- `&0` - Black
- `&1` - Dark Blue
- `&2` - Dark Green
- `&3` - Dark Aqua
- `&4` - Dark Red
- `&5` - Dark Purple
- `&6` - Gold
- `&7` - Gray
- `&8` - Dark Gray
- `&9` - Blue
- `&a` - Green
- `&b` - Aqua
- `&c` - Red
- `&d` - Light Purple
- `&e` - Yellow
- `&f` - White
- `&l` - Bold
- `&n` - Underline
- `&o` - Italic
- `&r` - Reset

## Requirements

- Python 3.8+
- Pillow (for image processing)

## Examples

### Create a Colorful Banner

```python
from terminal_formatter import rainbow_text, ccb_gen, clear_screen

clear_screen()
ccb_gen("WELCOME")
print()
print(rainbow_text("- Terminal Formatter Demo -"))
print(rainbow_text("=" * 50))
```

### Animated Greeting

```python
from terminal_formatter import slow_print, PrintOptions, clear_screen

clear_screen()
options = PrintOptions(speed=10, text_color=[0, 255, 0])
slow_print("Hello! Welcome to Terminal Formatter!", options)
```

### Image Gallery

```python
from terminal_formatter import img_to_ascii
import os

for filename in os.listdir("images/"):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        print(f"\n--- {filename} ---")
        print(img_to_ascii(f"images/{filename}"))
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.