import unittest
from bycolors.color_class import ColorClass

darker_coeff = (0.5 - 0.35) * 2
lighter_coeff = (0.65 - 0.5) * 2


class TestColorClass(unittest.TestCase):
    def test_hex_initialization(self):
        color = ColorClass("#FF0000")
        self.assertTupleEqual(color.main_color, (1.0, 0.0, 0.0))

    def test_rgb_initialization(self):
        color = ColorClass((1.0, 0.0, 0.0))
        self.assertTupleEqual(color.main_color, (1.0, 0.0, 0.0))

    def test_rgba_initialization(self):
        color = ColorClass((1.0, 0.0, 0.0, 0.5))
        self.assertTupleEqual(color.main_color, (1.0, 0.0, 0.0, 0.5))

    def test_palette_initialization(self):
        palette = {"main": "#FF0000", "dark": "#800000", "light": "#FF8080"}
        color = ColorClass(palette)
        self.assertTupleEqual(color.palette["main"], (1.0, 0.0, 0.0))
        self.assertTupleEqual(color.palette["dark"], (int("80", 16) / 255, 0.0, 0.0))
        self.assertTupleEqual(
            color.palette["light"], (1.0, int("80", 16) / 255, int("80", 16) / 255)
        )

    def test_none_initialization(self):
        color = ColorClass(None)
        self.assertTupleEqual(color.main_color, (1.0, 1.0, 1.0))

    def test_main_property(self):
        color = ColorClass("#FF0000")
        self.assertEqual(color.main, color)

    def test_hex_property(self):
        color = ColorClass("#FF0000")
        self.assertEqual(color.hex, "#FF0000")

    def test_rgba_property(self):
        color = ColorClass("#FF0000")
        self.assertTupleEqual(color.rgba, (1.0, 0.0, 0.0, 1.0))

    def test_rgb_property(self):
        color = ColorClass("#FF0000")
        self.assertTupleEqual(color.rgb, (1.0, 0.0, 0.0))

    def test_rgb_property_with_alpha(self):
        color = ColorClass((1.0, 0.0, 0.0, 0.5))
        self.assertTupleEqual(color.rgb, (1.0, 0.5, 0.5))

    def test_dark_property_default(self):
        color = ColorClass("#FF0000")
        self.assertTupleEqual(color.dark.main_color, (1 - darker_coeff, 0.0, 0.0))

    def test_light_property_default(self):
        color = ColorClass("#FF0000")
        self.assertTupleEqual(
            color.light.main_color, (1.0, lighter_coeff, lighter_coeff)
        )

    def test_dark_property_custom(self):
        palette = {"main": "#FF0000", "dark": "#800000"}
        color = ColorClass(palette)
        self.assertEqual(color.dark.hex, "#800000")

    def test_light_property_custom(self):
        palette = {"main": "#FF0000", "light": "#FF8080"}
        color = ColorClass(palette)
        self.assertEqual(color.light.hex, "#FF8080")

    def test_alpha_manipulation(self):
        color = ColorClass("#FF0000")
        color_with_alpha = color.alpha(0.5)
        self.assertTupleEqual(color_with_alpha.main_color, (1.0, 0.0, 0.0, 0.5))

    # def test_brightness_manipulation_dark(self):
    #     color = ColorClass("#FF0000")
    #     darker = color.brightness(0.25)
    #     self.assertTupleEqual(darker.main_color, (0.25, 0.0, 0.0))

    # def test_brightness_manipulation_light(self):
    #     color = ColorClass("#FF0000")
    #     lighter = color.brightness(0.75)
    #     self.assertTupleEqual(lighter.main_color, (1.0, 0.75, 0.75))

    # def test_absolute_brightness_manipulation_dark(self):
    #     color = ColorClass("#FF0000")
    #     abs_dark = color.absolute_brightness(0.25)
    #     self.assertTupleEqual(abs_dark.main_color, (0.25, 0.0, 0.0))

    # def test_absolute_brightness_manipulation_light(self):
    #     color = ColorClass("#FF0000")
    #     abs_light = color.absolute_brightness(0.75)
    #     self.assertTupleEqual(abs_light.main_color, (0.75, 0.0, 0.0))

    def test_brightness_clamping_negative(self):
        color = ColorClass("#FF0000")
        self.assertTupleEqual(color.brightness(-1).main_color, (0.0, 0.0, 0.0))

    def test_brightness_clamping_positive(self):
        color = ColorClass("#FF0000")
        self.assertTupleEqual(color.brightness(2).main_color, (1.0, 1.0, 1.0))

    def test_black_color_brightness(self):
        black = ColorClass("#000000")
        self.assertTupleEqual(
            black.absolute_brightness(0.5).main_color, (0.5, 0.5, 0.5)
        )

    def test_white_color_brightness(self):
        white = ColorClass("#FFFFFF")
        self.assertTupleEqual(
            white.absolute_brightness(0.5).main_color, (0.5, 0.5, 0.5)
        )

    def test_invalid_hex_color(self):
        with self.assertRaises(ValueError):
            ColorClass("#FF")

    def test_invalid_color_type(self):
        with self.assertRaises(ValueError):
            ColorClass(123)

    def test_invalid_tuple_length(self):
        with self.assertRaises(ValueError):
            ColorClass((1.0, 0.0))

    def test_invalid_alpha_value(self):
        with self.assertRaises(ValueError):
            ColorClass((1.0, 0.0, 0.0, 2.0))

    def test_invalid_rgb_above_one(self):
        with self.assertRaises(ValueError):
            ColorClass((1.5, 0.0, 0.0))

    def test_invalid_rgb_below_zero(self):
        with self.assertRaises(ValueError):
            ColorClass((-0.5, 0.0, 0.0))

    def test_background_color_black(self):
        color = ColorClass((1.0, 0.0, 0.0, 0.5), background_color=(0.0, 0.0, 0.0))
        self.assertTupleEqual(color.rgb, (0.5, 0.0, 0.0))

    def test_background_color_white(self):
        color = ColorClass((1.0, 0.0, 0.0, 0.5), background_color=(1.0, 1.0, 1.0))
        self.assertTupleEqual(color.rgb, (1.0, 0.5, 0.5))

    def test_tuple_length(self):
        color = ColorClass("#FF0000")
        self.assertEqual(len(color), 3)

    def test_tuple_indexing(self):
        color = ColorClass("#FF0000")
        self.assertEqual(color[0], 1.0)
        self.assertEqual(color[1], 0.0)
        self.assertEqual(color[2], 0.0)

    def test_tuple_unpacking(self):
        color = ColorClass("#FF0000")
        r, g, b = color
        self.assertEqual(r, 1.0)
        self.assertEqual(g, 0.0)
        self.assertEqual(b, 0.0)

    def test_tuple_slicing(self):
        color = ColorClass("#FF0000")
        self.assertTupleEqual(color[:2], (1.0, 0.0))
        self.assertTupleEqual(color[1:], (0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
