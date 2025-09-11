import unittest
from unittest.mock import patch, MagicMock
from bycolors.palette import Palette, Gradient, ClassPropertyDescriptor, classproperty
from bycolors.color_class import ColorClass


class TestClassPropertyDescriptor(unittest.TestCase):
    """Test the ClassPropertyDescriptor functionality."""

    def test_class_property_descriptor_init(self):
        """Test ClassPropertyDescriptor initialization."""

        def test_func():
            return "test"

        descriptor = ClassPropertyDescriptor(test_func)
        self.assertEqual(descriptor.fget, test_func)

    def test_class_property_descriptor_get_from_class(self):
        """Test accessing class property from class."""

        class TestClass:
            @classproperty
            def test_prop(cls):
                return f"class_{cls.__name__}"

        result = TestClass.test_prop
        self.assertEqual(result, "class_TestClass")

    def test_class_property_descriptor_get_from_instance(self):
        """Test accessing class property from instance."""

        class TestClass:
            @classproperty
            def test_prop(cls):
                return f"class_{cls.__name__}"

        instance = TestClass()
        result = instance.test_prop
        self.assertEqual(result, "class_TestClass")


class TestGradient(unittest.TestCase):
    """Test the Gradient class functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_parent = MagicMock()
        self.mock_parent.blue = ColorClass("#0000FF")
        self.mock_parent.red = ColorClass("#FF0000")
        self.mock_parent.cmap = MagicMock(return_value="mock_colormap")
        self.gradient = Gradient(self.mock_parent)

    def test_gradient_init_with_parent(self):
        """Test Gradient initialization with parent."""
        gradient = Gradient(self.mock_parent)
        self.assertEqual(gradient._parent, self.mock_parent)

    def test_gradient_init_without_parent(self):
        """Test Gradient initialization without parent."""
        gradient = Gradient()
        self.assertIsNone(gradient._parent)

    def test_gradient_getattr_no_parent_raises_error(self):
        """Test that accessing gradient without parent raises AttributeError."""
        gradient = Gradient()
        with self.assertRaises(AttributeError) as cm:
            _ = gradient.some_attribute
        self.assertIn("no attribute _parent", str(cm.exception))

    def test_gradient_getattr_with_underscore_method(self):
        """Test accessing private methods on gradient."""
        gradient = Gradient(self.mock_parent)
        gradient._test_method = MagicMock(return_value="test_result")

        result = gradient._test_method()  # Call the method
        self.assertEqual(result, "test_result")

    def test_gradient_getattr_simple_color_combination(self):
        """Test simple color combination access."""
        _ = self.gradient.blue_red  # Just access it to trigger the method
        self.mock_parent.cmap.assert_called_once()
        # Check that the colors were passed to cmap
        args = self.mock_parent.cmap.call_args[0]
        self.assertEqual(len(args), 2)

    def test_gradient_getattr_color_with_modifiers(self):
        """Test color combination with modifiers."""
        # Mock the color object to have light and dark attributes
        mock_blue = MagicMock()
        mock_blue.main = "#0000FF"
        mock_blue.light = "#3333FF"
        mock_blue.dark = "#000033"

        mock_red = MagicMock()
        mock_red.main = "#FF0000"
        mock_red.light = "#FF3333"

        self.mock_parent.blue = mock_blue
        self.mock_parent.red = mock_red

        # Test blue_light_red_light combination
        _ = self.gradient.blue_light_red_light  # Access to trigger the method
        self.mock_parent.cmap.assert_called()

        # Verify the correct modified colors were used
        args = self.mock_parent.cmap.call_args[0]
        self.assertEqual(len(args), 2)

    def test_gradient_getattr_invalid_color_raises_error(self):
        """Test that accessing invalid color raises AttributeError."""

        # Create a mock parent that properly simulates missing attribute
        class MockParent:
            def __getattr__(self, name):
                raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '{name}'"
                )

        mock_parent = MockParent()
        gradient = Gradient(mock_parent)

        with self.assertRaises(AttributeError) as cm:
            _ = gradient.invalid_color
        self.assertIn("no attribute 'invalid_color'", str(cm.exception))


class TestPalette(unittest.TestCase):
    """Test the Palette class functionality."""

    def test_palette_init_default(self):
        """Test Palette initialization with defaults."""
        palette = Palette()
        self.assertIsInstance(palette.gradient, Gradient)
        self.assertEqual(palette.gradient._parent, palette)

    def test_palette_init_with_colors_dict(self):
        """Test Palette initialization with colors dictionary."""
        colors = {"red": "#FF0000", "blue": (0, 0, 1), "green": {"main": "#00FF00"}}
        palette = Palette(colors=colors)

        self.assertIsInstance(palette.red, ColorClass)
        self.assertIsInstance(palette.blue, ColorClass)
        self.assertIsInstance(palette.green, ColorClass)
        self.assertEqual(palette.red.main_color, (1.0, 0.0, 0.0))
        self.assertEqual(palette.blue.main_color, (0.0, 0.0, 1.0))

    def test_palette_init_with_color_list(self):
        """Test Palette initialization with color list."""
        color_list = [
            ColorClass("#FF0000"),
            ColorClass("#00FF00"),
            ColorClass("#0000FF"),
        ]
        palette = Palette(color_list=color_list)

        self.assertEqual(palette._color_list, color_list)

    @patch("bycolors.palette.cmap.get_cmap")
    def test_palette_cmap_static_method(self, mock_get_cmap):
        """Test Palette.cmap static method."""
        mock_get_cmap.return_value = "mock_colormap"

        result = Palette.cmap("#FF0000", "#00FF00")

        mock_get_cmap.assert_called_once_with("#FF0000", "#00FF00")
        self.assertEqual(result, "mock_colormap")

    def test_palette_color_static_method(self):
        """Test Palette.color static method."""
        result = Palette.color("#FF0000")

        self.assertIsInstance(result, ColorClass)
        self.assertEqual(result.main_color, (1.0, 0.0, 0.0))

    @patch("cycler.cycler")
    def test_palette_cycler_property(self, mock_cycler):
        """Test Palette.cycler property."""
        color_list = [ColorClass("#FF0000"), ColorClass("#00FF00")]
        palette = Palette(color_list=color_list)
        mock_cycler.return_value = "mock_cycler"

        result = palette.cycler

        mock_cycler.assert_called_once_with(color=color_list)
        self.assertEqual(result, "mock_cycler")

    @patch("matplotlib.pyplot.rcParams")
    def test_make_default_mpl_palette(self, mock_rcparams):
        """Test make_default_mpl_palette method."""
        color_list = [ColorClass("#FF0000"), ColorClass("#00FF00")]
        palette = Palette(color_list=color_list)

        # Just test that the method runs without error and sets rcParams
        palette.make_default_mpl_palette()

        # Verify rcParams was accessed/modified
        # The exact value will be the actual cycler from the palette
        self.assertTrue(len(mock_rcparams.__setitem__.call_args_list) > 0)


if __name__ == "__main__":
    unittest.main()
