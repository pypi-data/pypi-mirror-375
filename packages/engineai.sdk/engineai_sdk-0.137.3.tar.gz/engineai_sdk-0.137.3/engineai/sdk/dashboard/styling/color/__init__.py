"""Spec for Color resources."""

from .default_specs import PositiveNegativeDiscreteMap
from .discrete_map import DiscreteMap
from .discrete_map import DiscreteMapIntervalItem
from .discrete_map import DiscreteMapValueItem
from .divergent import Divergent
from .gradient import Gradient
from .gradient import GradientItem
from .palette import Palette
from .palette import PaletteTypes
from .single import Single

__all__ = [
    # .discrete_map
    "DiscreteMap",
    "DiscreteMapIntervalItem",
    "DiscreteMapValueItem",
    # .divergent
    "Divergent",
    # .gradient
    "Gradient",
    "GradientItem",
    "Palette",
    # .palette
    "PaletteTypes",
    # .default_specs
    "PositiveNegativeDiscreteMap",
    # .single
    "Single",
]
