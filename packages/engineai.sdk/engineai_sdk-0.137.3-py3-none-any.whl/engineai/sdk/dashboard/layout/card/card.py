"""Spec for a Card in a dashboard  grid layout."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from typing_extensions import Unpack
from typing_extensions import override

from engineai.sdk.dashboard.abstract.layout import AbstractLayoutItem
from engineai.sdk.dashboard.abstract.typing import PrepareParams
from engineai.sdk.dashboard.interface import CardInterface
from engineai.sdk.dashboard.interface import WidgetInterface as Widget
from engineai.sdk.dashboard.layout.exceptions import ElementHeightNotDefinedError
from engineai.sdk.dashboard.layout.grid import Grid
from engineai.sdk.dashboard.layout.typings import LayoutItem
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from .header import CardHeader

if TYPE_CHECKING:
    from engineai.sdk.dashboard.abstract.layout import AbstractLayoutItem
    from engineai.sdk.dashboard.abstract.typing import PrepareParams
    from engineai.sdk.dashboard.layout.typings import LayoutItem
    from engineai.sdk.dashboard.templated_string import TemplatedStringItem


class Card(CardInterface):
    """Groups content with widgets, grids, and selectable sections.

    The Card class is a fundamental component in a dashboard layout,
    allowing users to group and organize content. It provides a container
    for various layout items such as widgets, cards, grids, and selectable sections.
    """

    INPUT_KEY = "card"
    _EXTRA_PADDING = 0.45

    def __init__(
        self,
        *,
        content: LayoutItem,
        header: TemplatedStringItem | CardHeader | None = None,
    ) -> None:
        """Constructor for Card.

        Args:
            content: content within the Card. One of Widget, Card, Grid,
                SelectableSection.
            header: Header card spec. Defaults to None, i.e. a card without title.

        Examples:
            ??? example "Create a Card layout and add a widget"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import maps
                from engineai.sdk.dashboard.layout import Card

                data = pd.DataFrame(
                   data=[{"region": "PT", "value": 10}, {"region": "GB", "value": 100}]
                )

                Dashboard(content=Card(content=maps.Geo(data=data)))
                ```

            ??? example "Create a Card layout with multiple Widgets"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import maps
                from engineai.sdk.dashboard.layout import Card

                data = pd.DataFrame(
                   data=[{"region": "PT", "value": 10}, {"region": "GB", "value": 100}]
                )

                Dashboard(
                    content=Card(content=[maps.Geo(data=data), maps.Geo(data=data)])
                )
                ```
        """
        super().__init__()
        self.__header = self._set_header(header)
        self.__content = content
        self.__height: int | float | None = None

    @property
    def height(self) -> float:
        """Returns height required by Card based on height required by underlying item.

        Returns:
            float: height required by Card
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
        self, header: TemplatedStringItem | CardHeader | None
    ) -> CardHeader:
        if header is None:
            return CardHeader()
        if isinstance(header, CardHeader):
            return header
        return CardHeader(title=header)

    def items(self) -> list[AbstractLayoutItem]:
        """Returns list of grid items that need to be inserted individually."""
        return self.__content.items()

    @override
    def prepare(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepare card.

        Args:
            **kwargs (Unpack[PrepareParams]): keyword arguments
        """
        self.__content.prepare(**kwargs)

    def prepare_heights(self, row_height: int | float | None = None) -> None:
        """Prepare Selectable Layout heights."""
        if not isinstance(self.__content, Widget):
            self.__content.prepare_heights(row_height=row_height)

        self.__height = row_height or (
            (self.__content.height + self._EXTRA_PADDING)
            if isinstance(self.__content, Grid)
            else self.__content.height
        )

    @override
    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "item": {self.__content.INPUT_KEY: self.__content.build()},
            "header": self.__header.build(),
            "dependencies": [
                {dependency.input_key: dependency.build()}
                for dependency in self.__header.dependencies
            ],
        }
