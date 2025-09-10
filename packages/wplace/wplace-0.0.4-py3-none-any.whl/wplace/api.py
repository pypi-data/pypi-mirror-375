import cloudscraper
from io import BytesIO
import logging
from PIL import Image
import requests

from .canvas import Pixel, Region, Tile
from .dto import PixelInfo, RegionInfo


class WplaceAPI:
    def __init__(
        self,
        frontend_url: str = "https://wplace.live",
        backend_url: str = "https://backend.wplace.live",
    ) -> None:
        self.frontend_url = frontend_url.rstrip("/")
        self.backend_url = backend_url.rstrip("/")

    def get_pixel_link(
        self,
        pixel: Pixel,
        select: bool = False,
        zoom: float | None = None,
    ) -> str:
        """Return link that navigates to the `pixel` on the Wplace canvas."""
        lon, lat = pixel.lonlat
        url = f"{self.frontend_url}/?lat={lat}&lng={lon}"
        if zoom is not None:
            url += f"&zoom={zoom}"
        if select:
            url += "&select=0"
        return url

    def get_pixel_url(self, pixel: Pixel) -> str:
        """Return the backend URL used to get information about the `pixel`."""
        tx, ty = pixel.tile
        px, py = pixel.coords_in_tile
        return f"{self.backend_url}/s0/pixel/{tx}/{ty}?x={px}&y={py}"

    def get_tile_url(self, tile: Tile) -> str:
        """Return the backend URL of the `tile` image."""
        return f"{self.backend_url}/files/s0/tiles/{tile.x}/{tile.y}.png"

    def fetch_pixel_info(self, pixel: Pixel) -> PixelInfo:
        """Get information about the `pixel` from the backend."""
        # TODO: Handle exceptions / add retries + timeout
        url = self.get_pixel_url(pixel=pixel)
        logging.debug(f"Downloading pixel information from {url}")
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        info = response.json()
        del scraper

        return PixelInfo.from_dict(info=info)

    def fetch_region_info(self, region: Region) -> RegionInfo:
        """Get information about the `region` from the backend."""
        return self.fetch_pixel_info(region.origin).region

    def fetch_tile_image(self, tile: Tile) -> Image.Image | None:
        """Download the `tile` image from the backend.

        Args:
            tile: The tile to download the image for.

        Returns:
            Image.Image: The tile image. Will be an indexed image with an RGB
                color palette with one palette index assigned to full
                transparency. NOTE: Palette length, order, and transparency
                index are NOT consistent across different tile images!
            None: If errors occurred or no image exists for the tile, yet.
        """
        url = self.get_tile_url(tile=tile)
        # TODO: Handle exceptions / add retries + timeout
        logging.debug(f"Downloading tile image from {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            return image
        except requests.HTTPError as exc:
            logging.error(f"Failed to load tile image: {exc}")
            return None
