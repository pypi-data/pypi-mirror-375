"""Typing for entities."""

from engineai.sdk.dashboard.widgets.components.charts.series.entities.country import (
    CountryEntity,
)
from engineai.sdk.dashboard.widgets.components.charts.series.entities.custom import (
    CustomEntity,
)

Entities = CountryEntity | CustomEntity
