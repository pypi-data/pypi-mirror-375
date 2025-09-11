from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.colors import LinearSegmentedColormap


def get_cmap(*colors) -> "LinearSegmentedColormap":
    import matplotlib as mpl

    name = str(hash(colors))
    return mpl.colors.LinearSegmentedColormap.from_list(name, [*colors])
