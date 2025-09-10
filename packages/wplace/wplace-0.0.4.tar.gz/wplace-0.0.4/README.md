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
Basic usage example (can be found in [examples/tile_image.py](examples/tile_image.py)):

```python
from wplace import Pixel, WplaceAPI

api = WplaceAPI()

wplace_link = "https://wplace.live/?lat=52.53835814390717&lng=13.37545865302734"
pixel = Pixel.from_link(wplace_link)
print(f"Selected pixel: {pixel!r}.")
pixel_info = api.fetch_pixel_info(pixel=pixel)
print(f"Pixel info: {pixel_info}")

region = pixel.region
print(f"Lies within {region!r}. Coords within region: {pixel.coords_in_region}.")
link = api.get_pixel_link(region.origin, select=True)
print(f"Navigate to region origin: {link}")

tile = pixel.tile
print(f"Lies within {tile!r}. Coords within tile: {pixel.coords_in_tile}.")
img_url = api.get_tile_url(tile)
print(f"Tile image URL: {img_url}")
chunk = api.fetch_tile_image(tile=tile)
chunk.show()
```

Output:

```
Selected pixel: Pixel(x=1100091, y=671480).
Pixel info: PixelInfo(painted_by=UserInfo(id=1, name='JohnDoe', alliance_id=None, alliance_name=None, country=None, discord_name=None), region=RegionInfo(id=85779, city_id=699, name='Berlin', number=7, country=Country(id=82, iso='DE', label='Germany')))
Lies within Region(x=275, y=167). Coords within region: (91, 3480).
Navigate to region origin: https://wplace.live/?lat=52.90885200790681&lng=13.359462890624988&select=0
Lies within Tile(x=1100, y=671). Coords within tile: (91, 480).
Tile image URL: https://backend.wplace.live/files/s0/tiles/1100/671.png
```
