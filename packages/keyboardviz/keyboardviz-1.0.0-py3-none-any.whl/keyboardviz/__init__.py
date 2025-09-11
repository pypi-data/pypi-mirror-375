"""
Keyboard Mapping Visualization Library

A clean, modular library for generating keyboard layout visualizations
with customizable key mappings and styling options.
"""

from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass
import svgwrite
import cairosvg


class ColorScheme(Enum):
    """Color scheme options for different key states."""

    BLANK = "blank"
    NORMAL = "normal"
    SHIFTED = "shifted"
    CONTROLLED = "controlled"
    ALT = "alt"
    BACKGROUND = "background"
    KEYBOARD = "keyboard"
    BORDER = "border"


@dataclass
class KeyDimensions:
    """Key dimensions and spacing configuration."""

    width: int = 60
    height: int = 60
    gap: int = 6
    corner_radius: int = 6


@dataclass
class Colors:
    """Color configuration for the keyboard."""

    blank: str = "#f8f9fa"  # Light gray-white
    normal: str = "#e3f2fd"  # Light blue
    shifted: str = "#e8f5e8"  # Light green
    controlled: str = "#fff3e0"  # Light orange
    alt: str = "#fce4ec"  # Light pink
    background: str = "#ffffff"  # Pure white
    keyboard: str = "#e0e0e0"  # Light gray border
    border: str = "#bdbdbd"  # Medium gray borders
    text: str = "#212121"  # Dark gray
    key_label: str = "#424242"  # Dark gray for key labels
    text_outline: str = "#ffffff"  # White outline for contrast
    text_normal: str = "#1565c0"  # Strong blue
    text_shifted: str = "#2e7d32"  # Strong green
    text_controlled: str = "#ef6c00"  # Strong orange
    text_alt: str = "#7b1fa2"  # Strong purple


class KeyType(Enum):
    """Types of key mappings."""

    NORMAL = "normal"
    SHIFTED = "shifted"
    CONTROLLED = "controlled"
    ALT = "alt"


class KeyboardMapper:
    """Main class for generating keyboard visualizations."""

    def __init__(
        self,
        dimensions: Optional[KeyDimensions] = None,
        colors: Optional[Colors] = None,
    ):
        self.dimensions = dimensions or KeyDimensions()
        self.colors = colors or Colors()
        self._default_layout = self._get_default_layout()

    def _get_default_layout(self) -> List[List[str]]:
        """Get the default QWERTY keyboard layout."""
        return [
            [
                "Esc",
                "F1",
                "F2",
                "F3",
                "F4",
                "F5",
                "F6",
                "F7",
                "F8",
                "F9",
                "F10",
                "F11",
                "F12",
            ],
            [
                "`",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "0",
                "-",
                "=",
                "Backspace",
            ],
            ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
            ["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter"],
            ["Shift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift"],
            ["Ctrl", "Win", "Alt", "Space", "Alt", "Menu", "Ctrl"],
        ]

    def _parse_key_mapping(self, key: str) -> Tuple[str, KeyType]:
        """Parse a key mapping to extract the base key and modifiers."""
        if key.startswith("<Shift>"):
            return key[7:], KeyType.SHIFTED
        elif key.startswith("<Ctrl>"):
            base_key = key[6:] if key.startswith("<Ctrl>") else key[9:]
            return base_key, KeyType.CONTROLLED
        elif key.startswith("<Alt>"):
            return key[5:], KeyType.ALT
        else:
            return key, KeyType.NORMAL

    def _get_key_colors(self, key: str, mappings: Dict[str, str]) -> List[str]:
        """Get all colors for a key based on its mappings (for gradient)."""
        key_upper = key.upper()
        mappings_upper = {k.upper(): v for k, v in mappings.items()}
        has_normal = key_upper in mappings_upper
        has_shifted = f"<SHIFT>{key_upper}" in mappings_upper
        has_ctrl = f"<CTRL>{key_upper}" in mappings_upper
        has_alt = f"<ALT>{key_upper}" in mappings_upper

        colors = []
        # Add colors in priority order for gradient
        if has_normal:
            colors.append(self.colors.normal)
        if has_shifted:
            colors.append(self.colors.shifted)
        if has_ctrl:
            colors.append(self.colors.controlled)
        if has_alt:
            colors.append(self.colors.alt)

        # Return blank if no mappings
        return colors if colors else [self.colors.blank]

    def _get_key_mappings_for_key(
        self, key: str, mappings: Dict[str, str]
    ) -> List[Tuple[str, KeyType]]:
        """Get all mappings for a specific key."""
        key_mappings = []
        key_upper = key.upper()
        mappings_upper = {k.upper(): v for k, v in mappings.items()}
        mapping_checks = [
            (key_upper, KeyType.NORMAL),
            (f"<SHIFT>{key_upper}", KeyType.SHIFTED),
            (f"<CTRL>{key_upper}", KeyType.CONTROLLED),
            (f"<ALT>{key_upper}", KeyType.ALT),
        ]
        for mapping_key, key_type in mapping_checks:
            if mapping_key in mappings_upper:
                key_mappings.append((mappings_upper[mapping_key], key_type))
        return key_mappings

    def _create_gradient_definition(
        self, dwg: svgwrite.Drawing, colors: List[str], gradient_id: str
    ) -> str:
        """Create a gradient definition for a key with multiple modifier colors."""
        if len(colors) == 1:
            # Single color, no gradient needed
            return colors[0]

        # Create linear gradient with sharp transitions (no feathering)
        gradient = dwg.defs.add(
            dwg.linearGradient(
                id=gradient_id, start=(0, 0), end=(1, 0)  # Horizontal gradient
            )
        )

        # Add color stops with sharp transitions - each color gets equal space
        for i, color in enumerate(colors):
            # Calculate the start and end positions for this color band
            band_width = 1.0 / len(colors)
            start_offset = i * band_width
            end_offset = (i + 1) * band_width

            # Add sharp start of this color band
            if i > 0:
                gradient.add_stop_color(offset=start_offset, color=colors[i - 1])
            gradient.add_stop_color(offset=start_offset, color=color)

            # Add sharp end of this color band (except for last color)
            if i < len(colors) - 1:
                gradient.add_stop_color(offset=end_offset, color=color)

        return f"url(#{gradient_id})"

    def _add_outlined_text(
        self,
        dwg: svgwrite.Drawing,
        text: str,
        x: float,
        y: float,
        font_size: int,
        fill_color: str,
        font_weight: str = "normal",
        stroke_color: str = "white",
        stroke_width: float = 2,
    ) -> None:
        """Add text with outline for better contrast."""
        # Add text outline (stroke)
        dwg.add(
            dwg.text(
                text,
                insert=(x, y),
                text_anchor="middle",
                font_size=font_size,
                font_family="Arial, sans-serif",
                fill="none",
                stroke=stroke_color,
                stroke_width=stroke_width,
                font_weight=font_weight,
            )
        )
        # Add text fill on top
        dwg.add(
            dwg.text(
                text,
                insert=(x, y),
                text_anchor="middle",
                font_size=font_size,
                font_family="Arial, sans-serif",
                fill=fill_color,
                font_weight=font_weight,
            )
        )

    def _create_key_element(
        self, dwg: svgwrite.Drawing, x: int, y: int, key: str, mappings: Dict[str, str]
    ) -> None:
        """Create a single key element with its mappings."""
        dims = self.dimensions

        # Get key colors for gradient
        key_colors = self._get_key_colors(key, mappings)

        # Create gradient or use single color
        gradient_id = f"gradient_{key}_{x}_{y}".replace(" ", "_")
        key_fill = self._create_gradient_definition(dwg, key_colors, gradient_id)

        # Create key rectangle
        key_rect = dwg.rect(
            insert=(x, y),
            size=(dims.width, dims.height),
            rx=dims.corner_radius,
            ry=dims.corner_radius,
            fill=key_fill,
            stroke=self.colors.border,
            stroke_width=1,
        )
        dwg.add(key_rect)

        # Always show the original key label at the top with outline
        self._add_outlined_text(
            dwg,
            key,
            x + dims.width / 2,
            y + 15,
            font_size=10,
            fill_color=self.colors.key_label,
            font_weight="bold",
            stroke_color=self.colors.text_outline,
            stroke_width=2,
        )

        # Get all mappings for this key
        key_mappings = self._get_key_mappings_for_key(key, mappings)

        if key_mappings:
            # Show mapped functions below the key label
            y_offset = 25
            line_height = 12
            max_lines = 3

            for i, (mapping, key_type) in enumerate(key_mappings[:max_lines]):
                if i >= max_lines:
                    break

                # Truncate long mappings
                display_text = mapping[:8] + "..." if len(mapping) > 8 else mapping

                # Color code by modifier
                text_color = {
                    KeyType.NORMAL: self.colors.text_normal,
                    KeyType.SHIFTED: self.colors.text_shifted,
                    KeyType.CONTROLLED: self.colors.text_controlled,
                    KeyType.ALT: self.colors.text_alt,
                }.get(key_type, self.colors.text_normal)

                # Add outlined text for better contrast
                self._add_outlined_text(
                    dwg,
                    display_text,
                    x + dims.width / 2,
                    y + y_offset,
                    font_size=9,
                    fill_color=text_color,
                    font_weight="normal",
                    stroke_color=self.colors.text_outline,
                    stroke_width=1.5,
                )
                y_offset += line_height

    def generate_keyboard(
        self,
        mappings: Dict[str, str],
        layout: Optional[List[List[str]]] = None,
        title: Optional[str] = None,
        export_svg: Optional[str] = None,
        export_png: Optional[str] = None,
        png_scale: int = 1200,
    ) -> svgwrite.Drawing:
        """
        Generate a keyboard visualization with the given mappings.

        Args:
            mappings: Dictionary mapping keys to their functions
            layout: Custom keyboard layout (uses default QWERTY if None)
            title: Optional title to display in bottom right corner
            export_svg: Optional SVG filename to export to
            export_png: Optional PNG filename to export to
            png_scale: Width of PNG output in pixels (if exporting PNG)

        Returns:
            SVG Drawing object
        """
        if layout is None:
            layout = self._default_layout

        dims = self.dimensions

        # Calculate canvas dimensions
        max_keys_per_row = max(len(row) for row in layout)
        canvas_width = max_keys_per_row * (dims.width + dims.gap) + dims.gap
        canvas_height = len(layout) * (dims.height + dims.gap) + dims.gap

        # Create SVG
        dwg = svgwrite.Drawing(size=(canvas_width, canvas_height))

        # Add keyboard background
        dwg.add(
            dwg.rect(
                insert=(0, 0),
                size=(canvas_width, canvas_height),
                rx=12,
                ry=12,
                fill=self.colors.background,
                stroke=self.colors.keyboard,
                stroke_width=2,
            )
        )

        # Add legend
        self._add_legend(dwg, canvas_width - 60, 10)

        # Add title in bottom right corner if provided
        if title:
            self._add_title(dwg, title, canvas_width - 10, canvas_height - 10)

        # Generate keys
        for row_idx, row in enumerate(layout):
            for col_idx, key in enumerate(row):
                x = dims.gap + col_idx * (dims.width + dims.gap)
                y = dims.gap + row_idx * (dims.height + dims.gap)

                self._create_key_element(dwg, x, y, key, mappings)

        # Export SVG if requested
        if export_svg:
            dwg.saveas(export_svg)

        # Export PNG if requested
        if export_png:
            # Create a temporary SVG string
            svg_string = dwg.tostring()
            cairosvg.svg2png(
                bytestring=svg_string.encode("utf-8"),
                write_to=export_png,
                output_width=png_scale,
            )

        return dwg

    def _add_legend(self, dwg: svgwrite.Drawing, x: int, y: int) -> None:
        """Add a color legend to the keyboard."""
        legend_items = [
            ("Normal", self.colors.normal, self.colors.text_normal),
            ("Shift", self.colors.shifted, self.colors.text_shifted),
            ("Ctrl", self.colors.controlled, self.colors.text_controlled),
            ("Alt", self.colors.alt, self.colors.text_alt),
        ]

        for i, (label, color, text_color) in enumerate(legend_items):
            legend_x = x
            legend_y = y + i * 15

            # Color box
            dwg.add(
                dwg.rect(
                    insert=(legend_x, legend_y),
                    size=(12, 12),
                    fill=color,
                    stroke=self.colors.border,
                )
            )

            # Label
            dwg.add(
                dwg.text(
                    label,
                    insert=(legend_x + 16, legend_y + 9),
                    font_size=10,
                    font_family="Arial, sans-serif",
                    fill=text_color,
                )
            )

    def _add_title(self, dwg: svgwrite.Drawing, title: str, x: int, y: int) -> None:
        """Add a title to the keyboard in the bottom right corner."""
        # Add text outline (stroke) - right aligned
        dwg.add(
            dwg.text(
                title,
                insert=(x, y),
                text_anchor="end",
                font_size=14,
                font_family="Arial, sans-serif",
                fill="none",
                stroke=self.colors.text_outline,
                stroke_width=2,
                font_weight="bold",
            )
        )
        # Add text fill on top - right aligned
        dwg.add(
            dwg.text(
                title,
                insert=(x, y),
                text_anchor="end",
                font_size=14,
                font_family="Arial, sans-serif",
                fill=self.colors.key_label,
                font_weight="bold",
            )
        )


def generate_keyboard(
    mappings: Dict[str, str],
    layout: Optional[List[List[str]]] = None,
    title: Optional[str] = None,
    export_svg: Optional[str] = None,
    export_png: Optional[str] = None,
    png_scale: int = 1200,
    custom_colors: Optional[Colors] = None,
    custom_dimensions: Optional[KeyDimensions] = None,
) -> svgwrite.Drawing:
    """
    Convenience function to generate a keyboard visualization.

    Args:
        mappings: Dictionary mapping keys to their functions
                 Example: {"a": "Pen", "<Shift>a": "Laser Pen"}
        layout: Custom keyboard layout (uses default QWERTY if None)
        title: Optional title to display in bottom right corner
        export_svg: Optional SVG filename to export to
        export_png: Optional PNG filename to export to
        png_scale: Width of PNG output in pixels (if exporting PNG)
        custom_colors: Custom color scheme
        custom_dimensions: Custom key dimensions

    Returns:
        SVG Drawing object
    """
    keyboard_mapper = KeyboardMapper(custom_dimensions, custom_colors)
    return keyboard_mapper.generate_keyboard(
        mappings=mappings,
        layout=layout,
        title=title,
        export_svg=export_svg,
        export_png=export_png,
        png_scale=png_scale,
    )


# Example usage
if __name__ == "__main__":
    # Example mappings
    example_mappings = {
        "a": "Pen",
        "<Shift>a": "Laser Pen",
        "b": "Brush",
        "<Ctrl>b": "Bold",
        "c": "Copy",
        "<Ctrl>c": "Copy",
        "<Shift>c": "Color Picker",
        "z": "Undo",
        "<Ctrl>z": "Undo",
        "<Shift>z": "Redo",
    }

    # Generate keyboard visualization
    mapper = KeyboardMapper()
    svg_drawing = mapper.generate_keyboard(
        mappings=example_mappings,
        export_svg="keyboard_mapping.svg",
        export_png="keyboard_mapping.png",
    )

    print("Generated keyboard_mapping.svg and keyboard_mapping.png")
