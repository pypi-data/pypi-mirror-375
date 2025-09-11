from .palette import Palette


def make_default_mpl_palette(palette: Palette = None):
    import matplotlib.pyplot as plt

    if palette is None:
        from .by_palette import by_palette

        palette = by_palette

    plt.rcParams["axes.prop_cycle"] = palette.cycler
