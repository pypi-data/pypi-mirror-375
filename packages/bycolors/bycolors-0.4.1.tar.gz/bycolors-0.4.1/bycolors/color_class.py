from typing import TypedDict


class _PALETTE_TYPE(TypedDict):
    """Type definition for color palettes.

    Attributes:
        main (str): The main color value
        dark (str): Optional darker variant of the color
        light (str): Optional lighter variant of the color
    """

    main: str
    dark: str
    light: str


_RGB_TYPE = tuple[int, int, int] | tuple[int, int, int, int]


def rgb_to_hex(rgb: _RGB_TYPE) -> str:
    return "#" + "".join(f"{int(255*c):02X}" for c in rgb)


def get_brightness(rgb: _RGB_TYPE) -> float:
    return sum(rgb) / 3


def rgb_to_rgba(rgb: _RGB_TYPE) -> _RGB_TYPE:
    """Convert a RGB color to a RGBA color."""
    return (rgb + (1,)) if len(rgb) == 3 else rgb


def hex_to_rgb(hex: str) -> _RGB_TYPE:
    """Convert a hex color to a RGB color."""
    if hex.startswith("#"):
        hex = hex[1:]
    if len(hex) == 3:
        return tuple(int(hex[i] * 2, 16) / 255 for i in (0, 1, 2))
    elif len(hex) == 4:
        return tuple(int(hex[i : i + 2], 16) / 255 for i in (0, 1, 2, 3))
    elif len(hex) == 6:
        return tuple(int(hex[i : i + 2], 16) / 255 for i in (0, 2, 4))
    elif len(hex) == 8:
        return tuple(int(hex[i : i + 2], 16) / 255 for i in (0, 2, 4, 6))
    else:
        raise ValueError(f"Invalid hex color: {hex}")


def check_rgba(rgba: _RGB_TYPE) -> bool:
    if len(rgba) == 3:
        rgba = rgba + (1,)

    if len(rgba) != 4:
        return False

    return all(not (c < 0 or c > 1) for c in rgba)


def raise_if_rgba_is_invalid(rgba: _RGB_TYPE) -> _RGB_TYPE:
    if not check_rgba(rgba):
        raise ValueError(f"Invalid rgba color: {rgba}")
    return rgba


def change_brightness_relatively(rgba: _RGB_TYPE, brightness: float) -> _RGB_TYPE:
    """Change the brightness of a color.

    Args:
        rgb (_RGB_TYPE): The color to change.
        brightness (float): The final brightness of the color.
            From 0 to 1. where 0 is black and 1 is white and 0.5 is the original color.

    Returns:
        _RGB_TYPE: The color with the new brightness.
    """
    # Ensure brightness is between 0 and 1
    brightness = max(0, min(1, brightness))
    rgb = rgba[:3]

    # Calculate relative brightness compared to current brightness
    # current_brightness = get_brightness(rgb)
    if brightness < 0.5:
        # Darken: interpolate between black (0,0,0) and current color
        factor = 2 * brightness
        new_rgb = tuple(c * factor for c in rgb[:3])
    else:
        # Lighten: interpolate between current color and white (255,255,255)
        factor = 2 * (brightness - 0.5)
        new_rgb = tuple(c + (1 - c) * factor for c in rgb[:3])

    # Preserve alpha if it exists
    if len(rgba) == 4:
        return new_rgb + (rgba[3],)
    return new_rgb


def change_brightness_absolutely(rgba: _RGB_TYPE, brightness: float) -> _RGB_TYPE:
    """Change the brightness of a color.

    Args:
        rgb (_RGB_TYPE): The color to change.
        brightness (float): The final brightness of the color.
            From 0 to 1, where 0 is black and 1 is white.

    Returns:
        _RGB_TYPE: The color with the new brightness.
    """
    # Ensure brightness is between 0 and 1
    brightness = max(0, min(1, brightness))
    rgb = rgba[:3]

    # Scale each RGB component to match target brightness
    # Average of RGB components should equal target brightness * 255
    current_brightness = get_brightness(rgb)
    if current_brightness == 0:
        # Handle black color case
        new_rgb = tuple(brightness for _ in range(3))
    else:
        # Scale RGB values to achieve target brightness
        scale = (brightness * 3) / sum(rgb)
        new_rgb = tuple(min(1, c * scale) for c in rgb)

    # Preserve alpha if it exists
    if len(rgba) == 4:
        return new_rgb + (rgba[3],)
    return new_rgb


def change_alpha(rgb: _RGB_TYPE, alpha: float) -> _RGB_TYPE:
    """Change the alpha of a color.

    Args:
        rgb (_RGB_TYPE): The color to change.
        alpha (float): The final alpha of the color.
    """
    return rgb[:3] + (alpha,)


_POSSIBLE_COLOR_INIT_TYPES = (
    _PALETTE_TYPE | str | tuple[int, int, int] | tuple[int, int, int, int]
)


def convert_to_rgb(
    color: str | tuple[int, int, int] | tuple[int, int, int, int] | dict,
) -> _RGB_TYPE:
    if isinstance(color, str):
        return raise_if_rgba_is_invalid(hex_to_rgb(color))
    elif isinstance(color, tuple):
        return raise_if_rgba_is_invalid(color)
    elif isinstance(color, dict):
        return raise_if_rgba_is_invalid(convert_to_rgb(color["main"]))
    elif color is None:
        return (1, 1, 1)
    else:
        raise ValueError(f"Invalid color: {color}")


def convert_to_palette(palette: _POSSIBLE_COLOR_INIT_TYPES) -> _PALETTE_TYPE:
    if isinstance(palette, dict):
        for key, value in palette.items():
            palette[key] = convert_to_rgb(value)
        return palette

    return {"main": convert_to_rgb(palette)}


class ColorClass(tuple):
    """A class representing a color with various manipulation capabilities.

    The ColorClass extends tuple to represent colors in RGB or RGBA format while providing
    methods for color manipulation like brightness adjustment, opacity changes, and color
    variant access (dark/light).

    Args:
        palette (_PALETTE_TYPE | str | tuple[int, int, int] | tuple[int, int, int, int] | None):
            The color value, can be a hex string, RGB/RGBA tuple, or a palette dictionary
            with 'main', 'dark', and 'light' variants.
        background_color (_RGB_TYPE | None): The background color used for alpha compositing.
            Defaults to white (1, 1, 1).

    Examples:
        >>> blue = ColorClass("#0000FF")
        >>> semi_transparent = blue.opacity(0.5)
        >>> darker_blue = blue.brightness(0.35)
        >>> rgb_values = blue.rgb  # (0, 0, 1)
    """

    def __new__(cls, palette: _POSSIBLE_COLOR_INIT_TYPES | None = None, **kwargs):
        main_color = convert_to_rgb(palette)
        return super().__new__(cls, main_color)

    def __init__(
        self,
        palette: _POSSIBLE_COLOR_INIT_TYPES | None = None,
        background_color: _RGB_TYPE | None = None,
    ):
        self.palette = convert_to_palette(palette)
        self.main_color = self.palette["main"]
        self._background_color = (
            convert_to_rgb(background_color) if background_color else (1, 1, 1)
        )

    @property
    def dark(self):
        """Returns a darker variant of the color.

        If a dark variant is defined in the palette, returns that.
        Otherwise, returns a color with 35% brightness of the original.

        Returns:
            ColorClass: A new color instance with darker values.
        """
        if "dark" in self.palette:
            return self._new_color(self.palette["dark"])
        else:
            return self.brightness(0.35)

    @property
    def light(self):
        """Returns a lighter variant of the color.

        If a light variant is defined in the palette, returns that.
        Otherwise, returns a color with 65% brightness of the original.

        Returns:
            ColorClass: A new color instance with lighter values.
        """
        if "light" in self.palette:
            return self._new_color(self.palette["light"])
        else:
            return self.brightness(0.65)

    @property
    def main(self):
        """Returns the main color instance.

        Returns:
            ColorClass: The current color instance.
        """
        return self

    @property
    def hex(self):
        """Returns the color in hexadecimal format.

        Returns:
            str: Color in hex format (e.g., "#FF0000" for red).
        """
        return rgb_to_hex(self.rgb)

    @property
    def rgba(self):
        """Returns the color as RGBA values.

        Returns:
            tuple[float, float, float, float]: Color as RGBA values between 0 and 1.
        """
        return rgb_to_rgba(self.main_color)

    @property
    def rgb(self):
        """Returns the color as RGB values, handling alpha compositing if needed.

        If the color has alpha < 1, performs alpha compositing with the background color.

        Returns:
            tuple[float, float, float]: Color as RGB values between 0 and 1.
        """
        if len(self.main_color) > 3 and self.main_color[3] < 1.0:
            alpha = self.main_color[3]
            rgb = self.main_color[:3]
            return tuple(
                c * alpha + (1 - alpha) * self._background_color[i]
                for i, c in enumerate(rgb)
            )
        return self.main_color[:3]

    def alpha(self, alpha: float, background_color: _RGB_TYPE | None = None):
        """Alias for opacity method.

        Args:
            alpha (float): Alpha value between 0 and 1.
            background_color (_RGB_TYPE | None): Optional background color for compositing.

        Returns:
            ColorClass: New color instance with modified alpha.
        """
        return self.opacity(alpha, background_color)

    def opacity(self, opacity: float, background_color: _RGB_TYPE | None = None):
        """Creates a new color with modified opacity.

        Args:
            opacity (float): Opacity value between 0 and 1.
            background_color (_RGB_TYPE | None): Optional background color for compositing.

        Returns:
            ColorClass: New color instance with modified opacity.
        """
        return self._new_color(
            change_alpha(self.main_color, opacity), background_color=background_color
        )

    def brightness(self, brightness: float):
        """Changes the brightness of the color relatively.

        Args:
            brightness (float): Target brightness between 0 and 1.
                Values < 0.5 darken the color, values > 0.5 lighten it.

        Returns:
            ColorClass: New color instance with modified brightness.
        """
        return self._new_color(
            change_brightness_relatively(self.main_color, brightness)
        )

    def absolute_brightness(self, brightness: float):
        """Changes the brightness of the color to an absolute value.

        Args:
            brightness (float): Target brightness between 0 and 1.
                0 is black, 1 is white.

        Returns:
            ColorClass: New color instance with modified brightness.
        """
        return self._new_color(
            change_brightness_absolutely(self.main_color, brightness)
        )

    @property
    def transparent(self):
        """Returns a fully transparent version of the color.

        Returns:
            ColorClass: New color instance with zero opacity.
        """
        return self._new_color(change_alpha(self.main_color, 0))

    def _new_color(self, color: _RGB_TYPE, background_color: _RGB_TYPE | None = None):
        """Creates a new color instance with the same configuration.

        Args:
            color (_RGB_TYPE): The new color values.
            background_color (_RGB_TYPE | None): Optional background color for compositing.

        Returns:
            ColorClass: New color instance.
        """
        if background_color is None:
            background_color = self._background_color
        return self.__class__(color, background_color=background_color)
