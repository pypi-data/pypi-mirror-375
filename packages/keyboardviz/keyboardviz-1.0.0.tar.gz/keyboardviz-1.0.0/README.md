# KeyboardViz

A minimal Python library for generating keyboard layout visualizations with custom key mappings.

## Installation

```bash
pip install keyboardviz
```

## Quick Start

```python
from keyboardviz import generate_keyboard

# Define your key mappings
mappings = {
    "w": "Pen", 
    "<Shift>w": "Laser", 
    "f": "Highlighter", 
    "<Alt>d": "Tool"
}

# Generate keyboard visualization
generate_keyboard(
    mappings, 
    export_svg="my_keyboard.svg", 
    export_png="my_keyboard.png"
)
```

## Key Mapping Format

- Normal keys: `"a": "Action"`
- Shift modifier: `"<Shift>a": "Shift Action"`
- Ctrl modifier: `"<Ctrl>a": "Ctrl Action"`
- Alt modifier: `"<Alt>a": "Alt Action"`

## Features

- SVG and PNG export
- Color-coded modifiers
- Customizable colors and dimensions
- Clean, minimal design

## Example Image

![docs/my_keyboard.svg](docs/my_keyboard.svg)

## License

MIT
