"""Color spec helpers."""

from typing import Any

from .discrete_map import DiscreteMap
from .gradient import Gradient
from .single import Single
from .typing import ColorSpec


def build_color_spec(spec: ColorSpec) -> dict[str, Any]:
    """Builds spec for dashboard API.

    Returns:
        Input object for Dashboard API
    """
    if isinstance(spec, Gradient):
        input_key = "gradient"
    elif isinstance(spec, DiscreteMap):
        input_key = "discreteMap"
    elif isinstance(spec, Single):
        input_key = "single"
    else:  # isinstance(spec, Palette | str):
        spec = Single(color=spec)
        input_key = "single"

    return {input_key: spec.build()}
