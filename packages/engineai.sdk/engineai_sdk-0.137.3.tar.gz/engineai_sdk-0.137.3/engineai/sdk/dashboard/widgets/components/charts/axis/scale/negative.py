"""Spec for scale for y axis with only negative values."""

from typing import Any

from engineai.sdk.dashboard.base import AbstractFactory


class AxisScaleNegative(AbstractFactory):
    """Y-axis scale for charts with negative values.

    Construct specifications for a scale for the y-axis with only
    negative values. It assumes the maximum value of the chart to
    be fixed at 0. Specify a fixed minimum value for the axis with
    the min_value parameter, which defaults to None, allowing
    for dynamic calculation of the minimum value.
    """

    def __init__(
        self, *, min_value: int | None = None, intermediate_tick_amount: int = 3
    ) -> None:
        """Constructor for AxisScaleNegative.

        Args:
            min_value: fixed minimum value for axis.
                Defaults to None (min value calculated dynamically)
            intermediate_tick_amount: number of extra ticks between extremes.
        """
        super().__init__()
        self.__min_value = min_value
        self.__intermediate_tick_amount = intermediate_tick_amount

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "min": self.__build_min_value(),
            "tickAmount": self.__intermediate_tick_amount,
        }

    def __build_min_value(
        self,
    ) -> dict[str, Any]:
        return {
            "min": self.__min_value,
        }
