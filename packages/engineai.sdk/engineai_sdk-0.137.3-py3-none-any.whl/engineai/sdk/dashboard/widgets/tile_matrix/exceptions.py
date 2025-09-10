"""Tile Matrix widget Exceptions."""

from engineai.sdk.dashboard.widgets.exceptions import DashboardWidgetError


class TileMatrixError(DashboardWidgetError):
    """Tile Matrix Widget Base Exception."""

    CLASS_NAME = "TileMatrix"


class TileMatrixValidateValueError(TileMatrixError):
    """Tile Matrix Widget Validate Value Error."""

    def __init__(
        self,
        subclass: str,
        argument: str,
        value: str,
        widget_id: str | None = None,
    ) -> None:
        """Constructor for TileMatrixValidateValueError class.

        Args:
            widget_id (Optional[str]): Tile Matrix widget id.
            subclass (str): Tile Matrix widget secondary class.
            argument (str): Tile Matrix widget argument.
            value (str): Tile Matrix widget value.
        """
        super().__init__(widget_id=widget_id)
        self.error_strings.append(
            f"Missing {argument}='{value}' in Data for the {subclass}."
        )
