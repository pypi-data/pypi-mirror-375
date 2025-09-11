import unittest
from unittest.mock import patch, MagicMock
from bycolors.by_palette import BYPalette, BYGradient, by_palette
from bycolors.palette import Palette, Gradient
from bycolors.color_class import ColorClass


class TestBYPalette(unittest.TestCase):
    """Test the BYPalette class functionality."""

    def test_by_palette_inherits_from_palette(self):
        """Test that BYPalette inherits from Palette."""
        self.assertTrue(issubclass(BYPalette, Palette))

    def test_by_palette_has_required_colors(self):
        """Test that BYPalette has all required color attributes."""
        required_colors = [
            "yellow",
            "blue",
            "red",
            "green",
            "purple",
            "orange",
            "grey",
            "brown",
            "pink",
            "violet",
            "cyan",
            "black",
            "white",
            "transparent",
        ]

        for color_name in required_colors:
            with self.subTest(color=color_name):
                self.assertTrue(hasattr(BYPalette, color_name))
                color_obj = getattr(BYPalette, color_name)
                self.assertIsInstance(color_obj, ColorClass)

    def test_by_palette_color_values(self):
        """Test specific color values in BYPalette."""

        # Test a few key colors - ColorClass.main returns RGB tuples, not hex
        # Convert hex to RGB for comparison
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))

        self.assertAlmostEqual(
            BYPalette.yellow.main[0], hex_to_rgb("#E5B700")[0], places=2
        )
        self.assertAlmostEqual(
            BYPalette.yellow.main[1], hex_to_rgb("#E5B700")[1], places=2
        )
        self.assertAlmostEqual(
            BYPalette.yellow.main[2], hex_to_rgb("#E5B700")[2], places=2
        )

        self.assertAlmostEqual(
            BYPalette.blue.main[0], hex_to_rgb("#0050A0")[0], places=2
        )
        self.assertAlmostEqual(
            BYPalette.blue.main[1], hex_to_rgb("#0050A0")[1], places=2
        )
        self.assertAlmostEqual(
            BYPalette.blue.main[2], hex_to_rgb("#0050A0")[2], places=2
        )

    def test_by_palette_color_variants(self):
        """Test that colors have light and dark variants where expected."""
        # Test that main colors have light and dark variants
        main_colors = ["yellow", "blue", "red", "green", "purple", "orange"]

        for color_name in main_colors:
            with self.subTest(color=color_name):
                color_obj = getattr(BYPalette, color_name)
                self.assertTrue(hasattr(color_obj, "light"))
                self.assertTrue(hasattr(color_obj, "dark"))
                self.assertTrue(hasattr(color_obj, "main"))

    def test_by_palette_transparent_color(self):
        """Test transparent color has proper RGBA value."""
        transparent = BYPalette.transparent
        self.assertEqual(transparent.main, (1, 1, 1, 0))


class TestBYGradient(unittest.TestCase):
    """Test the BYGradient class functionality."""

    def test_by_gradient_inherits_from_gradient(self):
        """Test that BYGradient inherits from Gradient."""
        self.assertTrue(issubclass(BYGradient, Gradient))

    def test_by_gradient_init(self):
        """Test BYGradient initialization."""
        gradient = BYGradient(BYPalette)
        self.assertEqual(gradient._parent, BYPalette)

    def test_by_gradient_has_type_annotations(self):
        """Test that BYGradient has proper type annotations."""
        expected_annotations = [
            "blue_yellow",
            "white_blue",
            "white_yellow",
            "transparent_white",
        ]

        for annotation in expected_annotations:
            with self.subTest(annotation=annotation):
                self.assertIn(annotation, BYGradient.__annotations__)

    @patch.object(BYPalette, "cmap")
    def test_by_gradient_blue_yellow_method(self, mock_cmap):
        """Test _blue_yellow method."""
        mock_cmap.return_value = "mock_colormap"
        gradient = BYGradient(BYPalette)

        result = gradient._blue_yellow()

        mock_cmap.assert_called_once_with(
            BYPalette.blue, BYPalette.white, BYPalette.yellow
        )
        self.assertEqual(result, "mock_colormap")

    @patch.object(BYPalette, "cmap")
    def test_by_gradient_white_blue_method(self, mock_cmap):
        """Test _white_blue method."""
        mock_cmap.return_value = "mock_colormap"
        gradient = BYGradient(BYPalette)

        result = gradient._white_blue()

        mock_cmap.assert_called_once_with(BYPalette.white, BYPalette.blue)
        self.assertEqual(result, "mock_colormap")


class TestByPaletteInstance(unittest.TestCase):
    """Test the by_palette instance functionality."""

    def test_by_palette_instance_exists(self):
        """Test that by_palette instance is created."""
        self.assertIsInstance(by_palette, BYPalette)

    def test_by_palette_instance_has_color_list(self):
        """Test that by_palette instance has _color_list attribute."""
        self.assertTrue(hasattr(by_palette, "_color_list"))
        self.assertIsInstance(by_palette._color_list, list)

    def test_by_palette_instance_color_list_length(self):
        """Test the length of color list in by_palette instance."""
        # Should have 8 main colors + 8 light variants = 16 colors
        self.assertEqual(len(by_palette._color_list), 16)

    def test_by_palette_instance_color_list_contents(self):
        """Test that color list contains correct ColorClass instances."""
        expected_main_colors = [
            BYPalette.blue,
            BYPalette.yellow,
            BYPalette.orange,
            BYPalette.purple,
            BYPalette.red,
            BYPalette.cyan,
            BYPalette.pink,
            BYPalette.green,
        ]

        expected_light_colors = [
            BYPalette.blue.light,
            BYPalette.yellow.light,
            BYPalette.orange.light,
            BYPalette.purple.light,
            BYPalette.red.light,
            BYPalette.cyan.light,
            BYPalette.pink.light,
            BYPalette.green.light,
        ]

        # Check first 8 are main colors
        for i, expected_color in enumerate(expected_main_colors):
            with self.subTest(index=i, color_type="main"):
                self.assertEqual(by_palette._color_list[i], expected_color)

        # Check next 8 are light colors
        for i, expected_color in enumerate(expected_light_colors):
            with self.subTest(index=i + 8, color_type="light"):
                self.assertEqual(by_palette._color_list[i + 8], expected_color)

    def test_by_palette_instance_gradient_property(self):
        """Test that by_palette instance has gradient property."""
        self.assertIsInstance(by_palette.gradient, Gradient)
        self.assertEqual(by_palette.gradient._parent, by_palette)

    @patch("cycler.cycler")
    def test_by_palette_instance_cycler(self, mock_cycler):
        """Test by_palette instance cycler property."""
        mock_cycler.return_value = "mock_cycler"

        result = by_palette.cycler

        mock_cycler.assert_called_once_with(color=by_palette._color_list)
        self.assertEqual(result, "mock_cycler")


class TestBYPaletteIntegration(unittest.TestCase):
    """Integration tests for BYPalette functionality."""

    @patch("bycolors.palette.cmap.get_cmap")
    def test_gradient_color_combination_integration(self, mock_get_cmap):
        """Test full gradient color combination workflow."""
        mock_get_cmap.return_value = "integrated_colormap"

        # Test accessing gradient through by_palette instance
        _ = by_palette.gradient.blue_yellow_red  # Access to trigger the method

        # Verify cmap was called with the correct colors
        mock_get_cmap.assert_called_once()
        args = mock_get_cmap.call_args[0]
        self.assertEqual(len(args), 3)  # blue, yellow, red

    def test_palette_class_vs_instance_behavior(self):
        """Test behavior differences between class and instance usage."""
        # Test that both class and instance can create ColorClass objects
        class_color = BYPalette.color("#FF0000")
        instance_color = by_palette.color("#FF0000")

        self.assertIsInstance(class_color, ColorClass)
        self.assertIsInstance(instance_color, ColorClass)
        self.assertEqual(class_color.main_color, instance_color.main_color)


if __name__ == "__main__":
    unittest.main()
