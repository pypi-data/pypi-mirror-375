from __future__ import annotations
from pyproj import CRS, Transformer
from rasterio.transform import from_bounds, rowcol, xy
from urllib.parse import urlparse, parse_qs


# setup of the pixel canvas
N_TILES_X: int = 2048
N_TILES_Y: int = 2048
N_TILE_PIXELS_X: int = 1000
N_TILE_PIXELS_Y: int = 1000
N_PIXELS_X: int = N_TILES_X * N_TILE_PIXELS_X
N_PIXELS_Y: int = N_TILES_Y * N_TILE_PIXELS_Y
N_REGION_PIXELS_X: int = 4000
N_REGION_PIXELS_Y: int = 4000
N_REGIONS_X: int = N_PIXELS_X // N_REGION_PIXELS_X
N_REGIONS_Y: int = N_PIXELS_Y // N_REGION_PIXELS_Y

# used coordinate reference systems
EPSG_3857 = CRS.from_epsg(3857) # Pseudo-Mercator
EPSG_4326 = CRS.from_epsg(4326) # longitude / latitude (WGS84)

# transformations between Pseudo-Mercator and WGS84
FROM_LONLAT = Transformer.from_crs(EPSG_4326, EPSG_3857, always_xy=True)
TO_LONLAT = Transformer.from_crs(EPSG_3857, EPSG_4326, always_xy=True)

# WGS84 bounds of the canvas from https://maps.wplace.live/planet
LON_WEST: float = -180.
LON_EAST: float =  180.
LAT_NORTH: float =  85.05113
LAT_SOUTH: float = -85.05113

# canvas bounds in EPSG:3857
WEST, NORTH = FROM_LONLAT.transform(xx=LON_WEST, yy=LAT_NORTH)
EAST, SOUTH = FROM_LONLAT.transform(xx=LON_EAST, yy=LAT_SOUTH)

# transformation between pixel coordinated and EPSG:3857
PIXEL_TRAFO = from_bounds(
    west=WEST,
    north=NORTH,
    east=EAST,
    south=SOUTH,
    width=N_PIXELS_X,
    height=N_PIXELS_Y,
)


def _pixel_to_lonlat(col: int, row: int) -> tuple[float, float]:
    """Return the WGS84 longitude and latitude of a pixel on the Wplace
    canvas.
    """
    x, y = xy(PIXEL_TRAFO, row, col)
    return TO_LONLAT.transform(x, y)


def _lonlat_to_pixel(lon: float, lat: float) -> tuple[int, int]:
    """Return the pixel coordinate on the Wplace canvas corresponding to the
    given WGS84 longitude and latitude.
    """
    x, y = FROM_LONLAT.transform(lon, lat)
    row, col = rowcol(PIXEL_TRAFO, x, y)
    return col.item(), row.item()


class _CanvasElement(tuple):
    __slots__ = ()

    # number of elements in x and y direction
    N_X: int = None
    N_Y: int = None

    def __new__(cls, x: int, y: int):
        if not (isinstance(x, int) and isinstance(y, int)):
            raise TypeError("x and y must be integers")
        if cls.N_X is None or cls.N_Y is None:
            raise NotImplementedError(
                f"{cls.__name__} must define class attributes N_X and N_Y")
        if not (0 <= x < cls.N_X and 0 <= y < cls.N_Y):
            raise ValueError(
                f"x must be in [0,{cls.N_X}), y must be in [0,{cls.N_Y})")
        return super().__new__(cls, (x, y))

    @property
    def x(self) -> int:
        return self[0]

    @property
    def y(self) -> int:
        return self[1]

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(x={self.x}, y={self.y})"

    def __add__(self, other: tuple[int, int]) -> _CanvasElement:
        x, y = other
        return type(self)(
            (self.x + x) % self.N_X,
            self.y + y,
        )

    def __sub__(
        self,
        other: tuple[int, int] | _CanvasElement,
    ) -> _CanvasElement | tuple[int, int]:
        if isinstance(other, _CanvasElement):
            dx = self.x - other.x
            if dx < 0:
                dx += self.N_X
            return dx, self.y - other.y
        x, y = other
        return type(self)(
            (self.x - x) % self.N_X,
            self.y - y,
        )



class Region(_CanvasElement):
    """A 4000 x 4000 pixels region on the Wplace canvas."""
    N_X: int = N_REGIONS_X
    N_Y: int = N_REGIONS_Y

    @property
    def origin(self) -> Pixel:
        """Return the most north-west pixel of the region."""
        return Pixel(
            self.x * N_REGION_PIXELS_X,
            self.y * N_REGION_PIXELS_Y,
        )


class Tile(_CanvasElement):
    """A 1000 x 1000 pixels tile on the Wplace canvas."""
    N_X: int = N_TILES_X
    N_Y: int = N_TILES_Y

    @property
    def origin(self) -> Pixel:
        """Return the most north-west pixel of the tile."""
        return Pixel(
            self.x * N_TILE_PIXELS_X,
            self.y * N_TILE_PIXELS_Y,
        )

    @property
    def region(self) -> Region:
        """Return the canvas region that contains the tile."""
        return self.origin.region

class Pixel(_CanvasElement):
    """A pixel on the Wplace canvas."""
    N_X: int = N_PIXELS_X
    N_Y: int = N_PIXELS_Y

    @classmethod
    def from_tile(
        cls,
        tile: Tile,
        px: int = 0,
        py: int = 0,
    ) -> Pixel:
        if not 0 <= px < N_TILE_PIXELS_X:
            raise ValueError(f"px has to be in [{0},{N_TILE_PIXELS_X})")
        if not 0 <= py < N_TILE_PIXELS_Y:
            raise ValueError(f"py has to be in [{0},{N_TILE_PIXELS_Y})")
        return tile.origin + (px, py)

    @classmethod
    def from_region(
        cls,
        region: Region,
        px: int = 0,
        py: int = 0,
    ) -> Pixel:
        if not 0 <= px < N_REGION_PIXELS_X:
            raise ValueError(f"px has to be in [{0},{N_REGION_PIXELS_X})")
        if not 0 <= py < N_REGION_PIXELS_Y:
            raise ValueError(f"py has to be in [{0},{N_REGION_PIXELS_Y})")
        return region.origin + (px, py)

    @classmethod
    def from_lonlat(cls, lon: float, lat: float) -> Pixel:
        x, y = _lonlat_to_pixel(lon=lon, lat=lat)
        return cls(x, y)

    @classmethod
    def from_link(cls, url: str) -> Pixel:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        return cls.from_lonlat(
            lon=float(params["lng"][0]),
            lat=float(params["lat"][0]),
        )

    @property
    def tile(self) -> Tile:
        """Return the canvas tile that contains the pixel."""
        return Tile(
            self.x // N_TILE_PIXELS_X,
            self.y // N_TILE_PIXELS_Y,
        )

    @property
    def coords_in_tile(self) -> tuple[int, int]:
        """Return coordinates of the pixel within its canvas tile."""
        return (
            self.x % N_TILE_PIXELS_X,
            self.y % N_TILE_PIXELS_Y,
        )

    @property
    def region(self) -> Region:
        """Return the canvas region that contains the pixel."""
        return Region(
            self.x // N_REGION_PIXELS_X,
            self.y // N_REGION_PIXELS_Y,
        )

    @property
    def coords_in_region(self) -> tuple[int, int]:
        """Return coordinates of the pixel within its canvas region."""
        return (
            self.x % N_REGION_PIXELS_X,
            self.y % N_REGION_PIXELS_Y,
        )

    @property
    def lonlat(self) -> tuple[float, float]:
        """Return the WGS84 longitude and latitude of the pixel."""
        return _pixel_to_lonlat(col=self.x, row=self.y)
