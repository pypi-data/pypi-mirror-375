"""Specs for Layout Package Interfaces."""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from engineai.sdk.dashboard.abstract.layout import AbstractLayoutItem

if TYPE_CHECKING:
    from engineai.sdk.dashboard.base import DependencyInterface


class CardInterface(AbstractLayoutItem, ABC):
    """Specs for Card Interface."""


class CollapsibleInterface(AbstractLayoutItem, ABC):
    """Specs for Card Interface."""


class GridInterface(AbstractLayoutItem, ABC):
    """Specs for Grid  Interface."""


class SelectableInterface(AbstractLayoutItem, ABC):
    """Specs for Selectable Interface."""


class WidgetInterface(AbstractLayoutItem, ABC):
    """Interface for Widget instance."""


class RouteInterface:
    """Specs for Route Interface."""


class OperationInterface:
    """Specs for Operation Interface."""

    _FORCE_SKIP_VALIDATION: bool = False

    @property
    def force_skip_validation(self) -> bool:
        """Returns True if widget height is forced."""
        return self._FORCE_SKIP_VALIDATION

    @property
    def dependencies(self) -> list[DependencyInterface]:
        """Returns operation id."""
        return []


class HttpConnectorInterface:
    """Specs for Http Connector Interface."""


class DuckDBConnectorInterface:
    """Specs for DuckDB Connector Interface."""


class SnowflakeConnectorInterface:
    """Specs for Snowflake Connector Interface."""
