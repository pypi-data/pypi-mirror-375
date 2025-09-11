from typing import TYPE_CHECKING

from .color_class import ColorClass, _POSSIBLE_COLOR_INIT_TYPES
from . import cmap


if TYPE_CHECKING:
    from matplotlib.colors import LinearSegmentedColormap


class ClassPropertyDescriptor:
    """A descriptor that makes a property work at the class level."""

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()


def classproperty(func):
    """Decorator to create a class-level property."""
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)
    return ClassPropertyDescriptor(func)


class Gradient:
    _parent = None

    def __init__(self, parent=None):
        self._parent = parent

    def __getattr__(self, item: str) -> "LinearSegmentedColormap":
        if self._parent is None:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute _parent"
            )
        # Handle direct method calls
        if item.startswith("_"):
            return getattr(super(), item)()
        private_name = f"_{item}"
        method = getattr(self, private_name, None)
        if callable(method):
            return method()

        # Parse dynamic color combinations with multiple modifiers
        tokens = item.split("_")
        colors = []
        i = 0
        try:
            # Use the parent class if available, otherwise default to Palette
            parent_cls = self._parent
            while i < len(tokens):
                color_name = tokens[i]
                modifiers = []
                # Collect all subsequent modifier tokens
                j = i + 1
                while j < len(tokens) and tokens[j] in ("main", "dark", "light"):
                    modifiers.append(tokens[j])
                    j += 1
                color_obj = getattr(parent_cls, color_name)
                value = color_obj
                # Apply all modifiers in order, if any
                for mod in modifiers:
                    value = getattr(value, mod, None)
                    if value is None:
                        raise AttributeError(
                            f"Color '{color_name}' has no modifier '{mod}'"
                        )
                if not modifiers:
                    value = getattr(color_obj, "main", color_obj)
                colors.append(value)
                i = j
            return parent_cls.cmap(*colors)
        except AttributeError as e:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{item}'"
            ) from e


class Palette:
    _color_list: list[ColorClass]
    gradient: Gradient

    def __init__(
        self,
        colors: dict[str, _POSSIBLE_COLOR_INIT_TYPES] = None,
        color_list: list[ColorClass] = None,
    ):
        if colors is not None:
            for name, color in colors.items():
                setattr(self, name, ColorClass(color))
        if color_list is not None:
            self._color_list = color_list
        self.gradient = Gradient(self)

    @staticmethod
    def cmap(*colors):
        return cmap.get_cmap(*colors)

    @staticmethod
    def color(color: _POSSIBLE_COLOR_INIT_TYPES) -> ColorClass:
        return ColorClass(color)

    # @classproperty
    # def gradient(cls):
    #     return Gradient(cls)

    @property
    def cycler(self):
        from cycler import cycler

        return cycler(color=self._color_list)

    def make_default_mpl_palette(self):
        import matplotlib.pyplot as plt

        plt.rcParams["axes.prop_cycle"] = self.cycler
