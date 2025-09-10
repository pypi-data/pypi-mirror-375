"""Specs for dependencies."""

from .connectors import DuckDBConnectorDependency
from .connectors import HttpConnectorDependency
from .connectors import SnowflakeConnectorDependency
from .route import RouteDependency
from .widget import WidgetSelectDependency

__all__ = [
    "DuckDBConnectorDependency",
    # .connectors
    "HttpConnectorDependency",
    # .route
    "RouteDependency",
    "SnowflakeConnectorDependency",
    # .widget
    "WidgetSelectDependency",
]
