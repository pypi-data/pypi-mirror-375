# B/Y Colors

A Python package for working with colors, providing an intuitive interface for color manipulation, transformation, and variant generation. Based palette is blue and yellow, which gives the name of the package.

## Features

- Simple and intuitive color manipulation
- Support for RGB, RGBA, and HEX color formats
- Color brightness adjustment (relative and absolute)
- Opacity/transparency control
- Automatic dark and light variant generation
- Background color compositing for transparent colors

## Installation

Install using pip:

```bash
pip install bycolors
```

## Quick Start

```python
from bycolors import colors as byc

# Basic color usage
blue = byc.blue
yellow = byc.yellow

# Color variants
dark_blue = blue.dark
light_yellow = yellow.light

# Custom brightness
custom_blue = blue.brightness(0.7)  # 70% relative brightness
very_dark = blue.absolute_brightness(0.2)  # 20% absolute brightness

# Transparency
semi_transparent = blue.opacity(0.5)
fully_transparent = blue.transparent

# Color format conversion
# here for illustration blue is a perfect blue (#0000FF)
rgb_values = blue.rgb        # (0, 0, 1)
rgba_values = blue.rgba      # (0, 0, 1, 1)
hex_value = blue.hex         # "#0000FF"

# Custom background for transparent colors
blue_on_white = blue.opacity(0.5, background_color=(1, 1, 1)).rgb  # (0.5, 0.5, 1)
```

## Documentation

For detailed documentation, visit:
- [Python Package Documentation](https://colors.kyrylo.gr/python/)
- [Color Class Reference](https://colors.kyrylo.gr/python/color_class)
- [Color Map Reference](https://colors.kyrylo.gr/python/cmap)

## Contributing

Contributions are welcome! For any suggestions or issues:
1. Open an issue to discuss the proposed changes
2. Fork the repository
3. Create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
