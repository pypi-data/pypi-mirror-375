"""Typing for the tile matrix items."""

from engineai.sdk.dashboard.widgets.components.actions.links import UrlLink
from engineai.sdk.dashboard.widgets.components.actions.links.external import (
    ExternalEvent,
)

Actions = UrlLink | ExternalEvent
