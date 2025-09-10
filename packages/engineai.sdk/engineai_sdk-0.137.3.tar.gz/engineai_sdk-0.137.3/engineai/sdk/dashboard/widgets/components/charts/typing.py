"""Specs for extra elements for tooltip of timeseries chart and series."""

from engineai.sdk.dashboard.widgets.components.charts.tooltip import CategoryTooltipItem
from engineai.sdk.dashboard.widgets.components.charts.tooltip import CountryTooltipItem
from engineai.sdk.dashboard.widgets.components.charts.tooltip import DatetimeTooltipItem
from engineai.sdk.dashboard.widgets.components.charts.tooltip import NumberTooltipItem
from engineai.sdk.dashboard.widgets.components.charts.tooltip import TextTooltipItem

TooltipItem = (
    CategoryTooltipItem
    | DatetimeTooltipItem
    | NumberTooltipItem
    | TextTooltipItem
    | CountryTooltipItem
)

TooltipItems = TooltipItem | list[TooltipItem]
