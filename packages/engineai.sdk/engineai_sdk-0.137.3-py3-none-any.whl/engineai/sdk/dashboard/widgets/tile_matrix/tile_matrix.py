"""Spec for TileMatrix Widget."""

from typing import Any

import pandas as pd
from typing_extensions import override

from engineai.sdk.dashboard.data.manager.manager import DataType
from engineai.sdk.dashboard.data.manager.manager import StaticDataType
from engineai.sdk.dashboard.widgets.base import Widget
from engineai.sdk.dashboard.widgets.utils import build_data

from .items.text.item import TextItem
from .typing import TileMatrixItem


class TileMatrix(Widget):
    """Spec for Tile Matrix Widget."""

    _DEPENDENCY_ID = "__TILE_MATRIX_DATA_DEPENDENCY__"
    _WIDGET_API_TYPE = "tileMatrix"
    _DEFAULT_HEIGHT = 0.86
    _FLUID_ROW_COMPATIBLE = True

    def __init__(
        self,
        data: DataType | pd.DataFrame,
        *,
        widget_id: str | None = None,
        max_columns: int | None = None,
        item: TileMatrixItem | str | None = None,
    ) -> None:
        """Construct spec for the Tile Matrix Widget.

        Args:
            data: data to be used by
                widget. Accepts Storages as well as raw data.
            widget_id: unique widget id in a dashboard.
            max_columns: maximum number of columns to be displayed.
            item: Tile Matrix item. If not provided, it will look into
                the first column of the data and decide the item type.

        Examples:
            ??? example "Create a minimal Tile Matrix Widget"
                ```py linenums="1"
                    import pandas as pd
                    from engineai.sdk.dashboard.dashboard import Dashboard
                    from engineai.sdk.dashboard.widgets import tile_matrix

                    data = pd.DataFrame([{"number": i} for i in range(1, 5)])

                    tile_widget = tile_matrix.TileMatrix(data=data)

                    Dashboard(content=tile_widget)
                ```

            ??? example "Create a Tile Matrix Widget with item as string"
                ```py linenums="1"
                    import pandas as pd
                    from engineai.sdk.dashboard.dashboard import Dashboard
                    from engineai.sdk.dashboard.widgets import tile_matrix

                    data = pd.DataFrame([{"number": i} for i in range(1, 5)])

                    tile_widget = tile_matrix.TileMatrix(data=data, item="number")

                    Dashboard(content=tile_widget)
                ```
        """
        super().__init__(widget_id=widget_id, data=data)
        self.__item = self.__set_item(data=data, item=item)
        self.__max_columns = max_columns

    def _prepare(self, **kwargs: object) -> None:
        self.__item.prepare()
        self._json_data = kwargs.get("json_data") or self._json_data

    def __set_item(
        self,
        data: DataType | pd.DataFrame,
        item: TileMatrixItem | str | None,
    ) -> TileMatrixItem:
        """Sets item for Tile Matrix Widget.

        Args:
            data: data to be used by widget.
            item: Tile Matrix item
        """
        if item is not None:
            if isinstance(item, str):
                return TextItem(data_column=item)
            return item

        if isinstance(data, DataType):
            msg = (
                "Item is required for Tile Matrix Widget when 'data' "
                "is a DataSource, Http or HttpConnector."
            )
            raise TypeError(msg)

        return TextItem(data_column=data.columns[0])

    @override
    def validate(self, data: StaticDataType, **_: Any) -> None:
        """Validates widget spec.

        Args:
            data (pd.DataFrame): pandas DataFrame where the data is present.
        """
        if isinstance(data, pd.DataFrame):
            self.__item.validate(data=data)

    @override
    def _build_widget_input(self) -> dict[str, Any]:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API
        """
        return {
            "data": build_data(path=self.dependency_id, json_data=self._json_data),
            "item": {self.__item.input_key: self.__item.build()},
            "maxColumns": self.__max_columns,
        }
