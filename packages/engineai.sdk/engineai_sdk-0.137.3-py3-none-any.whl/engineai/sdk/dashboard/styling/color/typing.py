"""Specs for color typing."""

from engineai.sdk.dashboard.styling.color.palette import Palette

from .discrete_map import DiscreteMap
from .gradient import Gradient
from .single import Single

ColorSpec = Palette | Single | Gradient | DiscreteMap | str
"""Union type for color descriptions.

Union type representing various color descriptions including
palettes, single colors, gradients, and discrete maps.
"""
