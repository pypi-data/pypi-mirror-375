"""Specs for category item for a tooltip."""

from engineai.sdk.dashboard.formatting import MapperFormatting
from engineai.sdk.dashboard.templated_string import DataField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from .base import BaseTooltipItem


class CategoryTooltipItem(BaseTooltipItem):
    """Customize tooltips for categorical data in Chart widget.

    Define specifications for a category tooltip item within a Chart widget to
    customize the appearance and content of tooltips displayed for categorical data.
    """

    def __init__(
        self,
        *,
        data_column: TemplatedStringItem,
        formatting: MapperFormatting,
        label: str | DataField | None = None,
    ) -> None:
        """Constructor for CategoryTooltipItem.

        Args:
            data_column (TemplatedStringItem): name of column in pandas dataframe(s)
                used for the value of the tooltip item.
            formatting (MapperFormatting): tooltip formatting spec.
            label (Optional[Union[str, DataField]]): label to be used for tooltip item,
                it can be either a string or a DataField object.
        """
        super().__init__(
            data_column=data_column,
            formatting=formatting,
            label=label,
        )
