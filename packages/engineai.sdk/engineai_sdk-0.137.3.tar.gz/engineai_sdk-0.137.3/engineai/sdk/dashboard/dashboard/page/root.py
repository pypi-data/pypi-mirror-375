"""Spec for a root grid in a dashboard."""

from __future__ import annotations

from typing import Any
from typing import TypeAlias

from typing_extensions import override

from engineai.sdk.dashboard.layout import CollapsibleSection
from engineai.sdk.dashboard.layout import CollapsibleTabSection
from engineai.sdk.dashboard.layout import FluidRow
from engineai.sdk.dashboard.layout import Grid
from engineai.sdk.dashboard.layout import Row
from engineai.sdk.dashboard.layout.row import RowItem

RootGridItemStrict: TypeAlias = (
    Row | FluidRow | CollapsibleSection | CollapsibleTabSection
)
RootGridItem: TypeAlias = RootGridItemStrict | RowItem


class RootGrid(Grid):
    """Spec for a root grid in a dashboard."""

    def __init__(
        self,
        *items: RootGridItem,
    ) -> None:
        """Construct dashboard grid.

        Args:
            items: items to add to grid. Can be widgets, rows or
                selectable sections (e.g tabs).
        """
        super().__init__()
        self._rows: list[RootGridItem] = [  # type: ignore[assignment]
            item if isinstance(item, RootGridItemStrict) else Row(item)
            for item in items
        ]

    @override
    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "items": [
                {
                    "fluid": row.build() if isinstance(row, FluidRow) else None,
                    "responsive": row.build() if isinstance(row, Row) else None,
                    "card": row.build()
                    if isinstance(row, CollapsibleSection)
                    else None,
                    "tabs": row.build()
                    if isinstance(row, CollapsibleTabSection)
                    else None,
                }
                for row in self._rows
            ],
        }
