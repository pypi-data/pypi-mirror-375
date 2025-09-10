"""Specs for default color specs."""

from engineai.sdk.dashboard.styling.color.gradient import Gradient
from engineai.sdk.dashboard.styling.color.gradient import GradientItem
from engineai.sdk.dashboard.styling.color.single import Palette


class EngineAIScoreColorGradient(Gradient):
    """Standard Gradient used for EngineAI Score.

    Args:
        n_steps (int): number of intermediate colors between
            gradient items. (Default: ``10``)

    Intervals:
        * ]-10, -0.5[ from Palette.RUBI_RED to Palette.SALMON_RED
        * [-0.5, 0.5[ Palette.COCONUT_GREY
        * [0.5, 10[ from Palette.BABY_BLUE to Palette.SEA_BLUE
    """

    def __init__(self, *, n_steps: int = 10) -> None:
        """EngineAI Score gradient spec."""
        super().__init__(
            GradientItem(color=Palette.RUBI_RED, value=-10),
            GradientItem(color=Palette.SALMON_RED, value=-0.5001),
            GradientItem(color=Palette.COCONUT_GREY, value=-0.5001),
            GradientItem(color=Palette.COCONUT_GREY, value=0.5),
            GradientItem(color=Palette.BABY_BLUE, value=0.5),
            GradientItem(color=Palette.OCEAN_BLUE, value=10),
            steps=n_steps,
        )
