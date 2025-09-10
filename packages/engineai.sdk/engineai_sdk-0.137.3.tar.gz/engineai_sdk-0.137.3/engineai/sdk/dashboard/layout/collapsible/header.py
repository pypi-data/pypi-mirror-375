"""Spec for the layout Collapsible Section Header."""

from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import override

from engineai.sdk.dashboard.layout.components.header import BaseHeader

if TYPE_CHECKING:
    from engineai.sdk.dashboard.templated_string import TemplatedStringItem

    from .chip import CollapsibleSectionChip


class CollapsibleSectionHeader(BaseHeader):
    """Provides title and chips for collapsible section headers.

    The CollapsibleSectionHeader class represents the header of a
    collapsible section, providing additional information such as
    title and chips.
    """

    def __init__(
        self,
        *chips: CollapsibleSectionChip,
        title: TemplatedStringItem | None = None,
    ) -> None:
        """Constructor for CollapsibleSectionHeader.

        Args:
            chips: chips to be added to the collapsible section header.
            title: Collapsible Section title.

        Examples:
            ??? example "Create a Collapsible Section layout with a title"
                ```py linenums="1"
                # Add Header to a Collapsible Section
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import pie
                from engineai.sdk.dashboard import layout

                data = pd.DataFrame(
                   {
                       "category": ["A", "B"],
                       "value": [1, 2],
                   },
                )

                Dashboard(
                    content=layout.CollapsibleSection(
                        content=pie.Pie(data=data),
                        header=layout.CollapsibleSectionHeader(title="Header Title")
                    )
                )
                ```
        """
        super().__init__(*chips, title=title)

    @override
    def has_title(self) -> bool:
        """Method to validate if header has title."""
        return self.__title is not None
