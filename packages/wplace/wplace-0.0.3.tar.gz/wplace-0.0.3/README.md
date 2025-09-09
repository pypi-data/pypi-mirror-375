# wplace

Utility classes and methods for [Wplace.live](https://wplace.live/)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/wplace?style=flat-square)
![PyPI - Downloads](https://img.shields.io/pypi/dm/wplace?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/wplace?style=flat-square)

## Installation

`wplace` is available on pypi:
```bash
python3 -m pip install --upgrade wplace
```

## Example
Basic usage example (can be found in [examples/tile_image_url.py](examples/tile_image_url.py)):

```python
from wplace import Pixel

wplace_link = "https://wplace.live/?lat=52.53835814390717&lng=13.37545865302734"
pixel = Pixel.from_link(wplace_link)
print(f"Selected pixel: {pixel!r}.")

region = pixel.region
print(f"Lies within {region!r}. Coords within region: {pixel.region_pixel}.")
print(f"Navigate to region origin: {region.origin.link(select=True)}")

tile = pixel.tile
print(f"Lies within {tile!r}. Coords within tile: {pixel.tile_pixel}.")
print(f"Tile image URL: {tile.url}")
```

Output:

```
Selected pixel: Pixel(x=1100091, y=671480).
Lies within Region(x=275, y=167). Coords within region: (91, 3480).
Navigate to region origin: https://wplace.live/?lat=52.90885200790681&lng=13.359462890624988&select=0
Lies within Tile(x=1100, y=671). Coords within tile: (91, 480).
Tile image URL: https://backend.wplace.live/files/s0/tiles/1100/671.png
```
