"""Specs for Tile Matrix item typing."""

from .items.chart.base import BaseTileMatrixChartItem
from .items.number.item import NumberItem
from .items.text.item import TextItem

TileMatrixItem = NumberItem | TextItem | BaseTileMatrixChartItem
