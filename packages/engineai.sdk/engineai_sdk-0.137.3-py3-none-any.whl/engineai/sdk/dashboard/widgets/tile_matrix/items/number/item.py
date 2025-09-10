"""Spec for Tile Matrix Number Item."""

from typing import Any

import pandas as pd

from engineai.sdk.dashboard.formatting.number import NumberFormatting
from engineai.sdk.dashboard.templated_string import DataField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from ..base import BaseTileMatrixItem
from ..typing import Actions
from .typing import TileMatrixNumberItemStyling


class NumberItem(BaseTileMatrixItem[TileMatrixNumberItemStyling]):
    """Spec for Tile Matrix Number Item."""

    _INPUT_KEY = "number"

    def __init__(
        self,
        *,
        data_column: TemplatedStringItem,
        label: TemplatedStringItem | DataField | None = None,
        icon: TemplatedStringItem | DataField | None = None,
        link: Actions | None = None,
        formatting: NumberFormatting | None = None,
        styling: TileMatrixNumberItemStyling | None = None,
        required: bool = True,
    ) -> None:
        """Construct spec for the TileMatrixNumberItem class.

        Args:
            data_column: column that has the value to be represented.
            label: Label text to be displayed.
            icon: icon to be displayed.
            link: link or action to be executed in the URL Icon.
            formatting: formatting spec.
            styling: styling spec.
            required: Flag to make Number item mandatory.

        Examples:
            ??? example "Create a Tile Matrix Widget with a Number Item."
                ```py linenums="1"
                    import pandas as pd
                    from engineai.sdk.dashboard.dashboard import Dashboard
                    from engineai.sdk.dashboard.widgets import tile_matrix

                    data = pd.DataFrame([{"number": i} for i in range(1, 5)])

                    tile_widget = tile_matrix.TileMatrix(
                        data=data, item=tile_matrix.NumberItem(data_column="number")
                    )

                    Dashboard(content=tile_widget)
                ```
        """
        super().__init__(
            data_column=data_column,
            label=label,
            icon=icon,
            link=link,
            formatting=formatting or NumberFormatting(),
            styling=styling,
            required=required,
        )

    def _build_extra_inputs(self) -> dict[str, Any]:
        if self._styling is not None:
            return {"styling": self._styling.build_styling()}
        return {}

    def validate(
        self,
        *,
        data: pd.DataFrame,
    ) -> None:
        """Validates Tile Matrix Number Item.

        Args:
            data (pd.DataFrame): data inside `path`.
        """
        if self._required:
            super().validate(
                data=data,
            )
            if self._styling is not None:
                self._styling.validate(
                    data=data,
                    column_name="value_column",
                )
