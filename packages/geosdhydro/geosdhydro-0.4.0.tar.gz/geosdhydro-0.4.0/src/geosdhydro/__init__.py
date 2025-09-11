"""geosdhydro package.

GIS tools for semi-distributed hydrologic modelling
"""

from __future__ import annotations

from geosdhydro._internal.cli import get_parser, main
from geosdhydro._internal.swift import ShapefileToSwiftConverter

__all__: list[str] = ["ShapefileToSwiftConverter", "get_parser", "main"]
