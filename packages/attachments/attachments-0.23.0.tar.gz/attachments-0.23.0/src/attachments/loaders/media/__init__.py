"""Media loaders - images, audio, video, vector graphics, etc."""

from .archives import zip_to_images
from .images import image_to_pil
from .vector_graphics import eps_to_epsdocument, svg_to_svgdocument

__all__ = ["image_to_pil", "zip_to_images", "svg_to_svgdocument", "eps_to_epsdocument"]
