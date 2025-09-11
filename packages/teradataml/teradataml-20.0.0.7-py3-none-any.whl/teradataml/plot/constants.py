from enum import Enum

class ImageType(Enum):
    PNG = "PNG"
    JPEG = "JPEG"
    SVG = "SVG"

class MapType(Enum):
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    WIGGLE = "wiggle"
    MESH = "mesh"
    GEOMETRY = "geometry"
    CORR = "corr"
