"""Spec for a Collapsible Section in a dashboard grid layout."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from typing_extensions import Unpack
from typing_extensions import override

from engineai.sdk.dashboard.abstract.layout import AbstractLayoutItem
from engineai.sdk.dashboard.abstract.typing import PrepareParams
from engineai.sdk.dashboard.interface import CollapsibleInterface
from engineai.sdk.dashboard.interface import WidgetInterface as Widget
from engineai.sdk.dashboard.layout.exceptions import ElementHeightNotDefinedError
from engineai.sdk.dashboard.layout.typings import LayoutItem
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from .header import CollapsibleSectionHeader

if TYPE_CHECKING:
    from engineai.sdk.dashboard.abstract.layout import AbstractLayoutItem
    from engineai.sdk.dashboard.abstract.typing import PrepareParams
    from engineai.sdk.dashboard.layout.typings import LayoutItem
    from engineai.sdk.dashboard.templated_string import TemplatedStringItem


class CollapsibleSection(CollapsibleInterface):
    """Organize and group content with expandable/collapsible sections.

    The CollapsibleSection class is used to create collapsible sections
    within a dashboard layout, providing a way to organize and group
    content that can be expanded or collapsed.
    """

    INPUT_KEY = "collapsible"

    def __init__(
        self,
        *,
        content: LayoutItem,
        header: TemplatedStringItem | CollapsibleSectionHeader | None = None,
        expanded: bool = True,
    ) -> None:
        """Constructor for CollapsibleSection.

        Args:
            content: content within the Section. One of Widget, Card, Grid,
                SelectableSection.
            header: Header specifications. By default the CollapsibleSection does
                not have title
            expanded: Whether the section is expanded or not.

        Examples:
            ??? example "Create a Collapsible Section layout and add a widget"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import maps
                from engineai.sdk.dashboard import layout

                data = pd.DataFrame(
                   data=[{"region": "PT", "value": 10}, {"region": "GB", "value": 100}]
                )

                Dashboard(content=layout.CollapsibleSection(
                    content=maps.Geo(data=data))
                )
                ```

            ??? example "Create a Collapsible Section layout with multiple Widgets"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import maps
                from engineai.sdk.dashboard import layout

                data = pd.DataFrame(
                   data=[{"region": "PT", "value": 10}, {"region": "GB", "value": 100}]
                )

                Dashboard(
                    content=layout.CollapsibleSection(content=[
                        maps.Geo(data=data),
                        maps.Geo(data=data)
                    ])
                )
                ```

        """
        super().__init__()
        self.__header = self._set_header(header)
        self.__content = content
        self.__height: int | float | None = None
        self.__expanded = expanded

    @property
    def force_height(self) -> bool:
        """Get if the Section has a forced height."""
        return False

    @property
    def height(self) -> float:
        """Returns height required by Section based on underlying item height.

        Returns:
            float: height required by Section
        """
        if self.__height is None:
            raise ElementHeightNotDefinedError
        return self.__height

    @property
    def has_custom_heights(self) -> bool:
        """Returns if the Item has custom heights in its inner components."""
        return (
            False
            if isinstance(self.__content, Widget)
            else self.__content.has_custom_heights
        )

    def _set_header(
        self, header: TemplatedStringItem | CollapsibleSectionHeader | None
    ) -> CollapsibleSectionHeader:
        if header is None:
            return CollapsibleSectionHeader()
        if isinstance(header, CollapsibleSectionHeader):
            return header
        return CollapsibleSectionHeader(title=header)

    def items(self) -> list[AbstractLayoutItem]:
        """Returns list of grid items that need to be inserted individually."""
        return self.__content.items()

    @override
    def prepare(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepare Section.

        Args:
            **kwargs (Unpack[PrepareParams]): keyword arguments
        """
        self.__content.prepare(**kwargs)

    def prepare_heights(self, row_height: int | float | None = None) -> None:
        """Prepare Selectable Layout heights."""
        if not isinstance(self.__content, Widget):
            self.__content.prepare_heights(row_height=row_height)

        self.__height = row_height or self.__content.height

    @override
    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "item": {self.__content.INPUT_KEY: self.__content.build()},
            "height": self.height,
            "header": self.__header.build(),
            "expanded": self.__expanded,
            "dependencies": [
                {dependency.input_key: dependency.build()}
                for dependency in self.__header.dependencies
            ],
        }
