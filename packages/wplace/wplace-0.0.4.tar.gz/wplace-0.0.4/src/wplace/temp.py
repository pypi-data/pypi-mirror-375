import itertools
import numpy as np
from PIL import Image
import time

from .canvas import (
    N_TILE_PIXELS_X,
    N_TILE_PIXELS_X,
    N_TILE_PIXELS_Y,
    N_TILE_PIXELS_Y,
    Pixel,
)
from .country import Country
from .color import Color
# from .image_processing import standardize_color_palette


COLOR_ICON_BITS: dict[Color, int] = {
    Color.BLACK:             4897444,
    Color.DARK_GRAY:         4756004,
    Color.GRAY:             15241774,
    Color.MEDIUM_GRAY:      31850982,
    Color.LIGHT_GRAY:       11065002,
    Color.WHITE:            15269550,
    Color.DEEP_RED:         33209205,
    Color.DARK_RED:         19267878,
    Color.RED:              15728622,
    Color.LIGHT_RED:        16236308,
    Color.DARK_ORANGE:      33481548,
    Color.ORANGE:           15658734,
    Color.GOLD:             33226431,
    Color.YELLOW:           33391295,
    Color.LIGHT_YELLOW:     32641727,
    Color.DARK_GOLDENROD:   22708917,
    Color.GOLDENROD:        14352822,
    Color.LIGHT_GOLDENROD:   7847326,
    Color.DARK_OLIVE:        7652956,
    Color.OLIVE:            22501038,
    Color.LIGHT_OLIVE:      28457653,
    Color.DARK_GREEN:       15589098,
    Color.GREEN:            11516906,
    Color.LIGHT_GREEN:       9760338,
    Color.DARK_TEAL:        15399560,
    Color.TEAL:              4685802,
    Color.LIGHT_TEAL:       15587182,
    Color.DARK_CYAN:         9179234,
    Color.CYAN:             29206876,
    Color.LIGHT_CYAN:       30349539,
    Color.DARK_BLUE:         3570904,
    Color.BLUE:             15259182,
    Color.LIGHT_BLUE:        4685269,
    Color.DARK_INDIGO:      18295249,
    Color.INDIGO:           29224831,
    Color.LIGHT_INDIGO:     21427311,
    Color.DARK_SLATE_BLUE:  26843769,
    Color.SLATE_BLUE:       24483191,
    Color.LIGHT_SLATE_BLUE:  5211003,
    Color.DARK_PURPLE:      22511061,
    Color.PURPLE:           15161013,
    Color.LIGHT_PURPLE:      4667844,
    Color.DARK_PINK:        11392452,
    Color.PINK:             11375466,
    Color.LIGHT_PINK:        6812424,
    Color.DARK_PEACH:       14829567,
    Color.PEACH:            17971345,
    Color.LIGHT_PEACH:      28873275,
    Color.DARK_BROWN:        5225454,
    Color.BROWN:            29197179,
    Color.LIGHT_BROWN:       4681156,
    Color.DARK_TAN:         21392581,
    Color.TAN:               7460636,
    Color.LIGHT_TAN:        23013877,
    Color.DARK_BEIGE:       29010254,
    Color.BEIGE:            18285009,
    Color.LIGHT_BEIGE:      18846257,
    Color.DARK_STONE:       21825364,
    Color.STONE:            29017787,
    Color.LIGHT_STONE:       4357252,
    Color.DARK_SLATE:       23057550,
    Color.SLATE:            26880179,
    Color.LIGHT_SLATE:       5242308,
    Color.TRANSPARENT:      15237450,
}


def get_rgb_color_map() -> dict[tuple[int, int, int], Color]:
    return {color.rgb: color for color in Color}


def get_rgb_palette(
    sort_by: str = "id",
    incl_trans: bool = False,
    incl_alpha: bool = False,
    flatten: bool = False,
) -> list[tuple[int, ...]] | list[int]:
    palette = []

    if sort_by == "palette":
        sorter = lambda color: tuple(Color).index(color)
    else:
        sorter = lambda color: getattr(color, sort_by)

    for color in sorted(Color, key=sorter):
        if color == Color.TRANSPARENT:
            alpha = 0
            if not incl_trans:
                continue
        else:
            alpha = 255

        color_tuple = color.rgb
        if incl_alpha:
            color_tuple = tuple(list(color_tuple) + [alpha])

        if flatten:
            palette.extend(color_tuple)
        else:
            palette.append(color_tuple)

    return palette


def get_color_icon(color: Color) -> Image.Image:
    n_pixels: int = 5
    bitmap = COLOR_ICON_BITS[color]
    bits = [bitmap >> i & 0b1 for i in range(n_pixels * n_pixels)]
    array = np.array(bits, dtype=np.uint8).reshape((n_pixels, n_pixels))
    image = Image.fromarray(array)
    image.putpalette([0, 0, 0] + list(color.rgb))
    image.info["transparency"] = 0
    return image


def download_area_image(
    origin: Pixel,
    width: int,
    height: int,
    sleep_time: float = 1.,
) -> Image.Image:
    """Load all needed tile images from the backend and create an image of the
    specified area.

    Returns:
        Image.Image: Indexed image with the Wplace color palette (63 solid
            colors + full transparency).
    """
    # TODO: Implement incremental download / save to handle large areas
    # TODO: Implement option to use already downloaded tile images
    start_tile = origin.tile
    x_start, y_start = origin.tile_pixel

    n_cols = 1 + (x_start + width - 1) // canvas.N_TILE_PIXELS_X
    n_rows = 1 + (y_start + height - 1) // canvas.N_TILE_PIXELS_Y
    n_tiles = n_cols * n_rows

    # init empty array to stitch tiles
    trans_index = Color.TRANSPARENT.id
    array_width = n_cols * canvas.N_TILE_PIXELS_X
    array_height = n_rows * canvas.N_TILE_PIXELS_Y
    array = np.ones((array_height, array_width), dtype=np.uint8) * trans_index

    for i, (col, row) in enumerate(itertools.product(range(n_cols), range(n_rows))):
        try:
            tile = start_tile + (col, row)
        except ValueError:
            # TODO: Handle out-of-bounds better
            continue
        tile_image = tile.download_image(save=False)
        if tile_image is None:
            continue
        tile_image = standardize_color_palette(tile_image)
        x0 = col * canvas.N_TILE_PIXELS_X
        x1 = x0 + canvas.N_TILE_PIXELS_X
        y0 = row * canvas.N_TILE_PIXELS_Y
        y1 = y0 + canvas.N_TILE_PIXELS_Y
        array[y0:y1, x0:x1] = np.array(tile_image, dtype=np.uint8)
        del tile_image
        if i < n_tiles - 1:
            time.sleep(sleep_time)

    cutout = array[y_start:y_start + height, x_start:x_start + width]
    image = Image.fromarray(cutout)
    image.putpalette(Color.rgb_palette(incl_trans=True, flatten=True))
    image.info["transparency"] = trans_index
    return image
