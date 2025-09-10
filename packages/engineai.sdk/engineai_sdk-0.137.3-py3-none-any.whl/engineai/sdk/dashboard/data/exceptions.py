"""Dashboard Data Error."""

from engineai.sdk.dashboard.exceptions import EngineAIDashboardError


class DataInvalidSlugError(EngineAIDashboardError):
    """Dashboard invalid slug error."""

    def __init__(self, slug: str, *args: object) -> None:
        """Constructor for DashboardInvalidSlugError class.

        Args:
            slug (str): connector type.
            *args (object): Additional arguments passed to the base
                EngineAIDashboardError class.
        """
        super().__init__(slug, *args)
        self.error_strings.append(
            "The Data Connector slug must be between 3 and 36 characters long and"
            "contain only lowercase letters, numbers, and hyphens."
        )
