"""Typing for the dashboard SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .selectable_widgets import AbstractSelectWidget


class PrepareParams(TypedDict):
    """Parameters for kwargs in prepare method."""

    # General
    dashboard_slug: str
    page: NotRequired[Any]
    selectable_widgets: NotRequired[dict[str, AbstractSelectWidget]]
