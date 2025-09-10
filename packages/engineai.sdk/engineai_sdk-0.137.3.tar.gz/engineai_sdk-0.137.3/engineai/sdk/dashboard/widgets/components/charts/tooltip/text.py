"""Specs for text item for a tooltip."""

from engineai.sdk.dashboard.formatting import TextFormatting
from engineai.sdk.dashboard.templated_string import DataField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from .base import BaseTooltipItem


class TextTooltipItem(BaseTooltipItem):
    """Customize tooltips for textual data in Chart.

    Define specifications for a text item within a tooltip
    for a Chart widget to customize the appearance and
    content of tooltips displayed for textual data.
    """

    def __init__(
        self,
        *,
        data_column: TemplatedStringItem,
        formatting: TextFormatting | None = None,
        label: str | DataField | None = None,
    ) -> None:
        """Constructor for TextTooltipItem.

        Args:
            data_column (TemplatedStringItem): name of column in pandas dataframe(s)
                used for the value of the tooltip item.
            formatting (Optional[TextFormatting]): tooltip formatting spec.
                Defaults to TextFormatting(max_characters=30).
            label (Optional[Union[str, DataField]]): label to be used for tooltip item,
                it can be either a string or a DataField object.
        """
        super().__init__(
            data_column=data_column,
            formatting=formatting if formatting is not None else TextFormatting(),
            label=label,
        )
