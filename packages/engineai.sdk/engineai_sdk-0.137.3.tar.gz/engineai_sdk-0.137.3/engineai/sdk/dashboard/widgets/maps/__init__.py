"""Map resources."""

from engineai.sdk.dashboard.widgets.components.playback.playback import Playback

from .color_axis import ColorAxis
from .enums import LegendPosition
from .enums import Region
from .geo.geo import Geo
from .geo.playback import GeoPlayback
from .geo.styling.label import MapStylingLabel
from .geo.styling.styling import MapStyling
from .series.numeric import NumericSeries
from .series.styling import SeriesStyling

__all__ = [
    # .color_axis"
    "ColorAxis",
    # .geo
    "Geo",
    "GeoPlayback",
    # .position
    "LegendPosition",
    # .styling
    "MapStyling",
    "MapStylingLabel",
    # .series
    "NumericSeries",
    # .playback
    "Playback",
    "Region",
    # .seriesStyling
    "SeriesStyling",
]
