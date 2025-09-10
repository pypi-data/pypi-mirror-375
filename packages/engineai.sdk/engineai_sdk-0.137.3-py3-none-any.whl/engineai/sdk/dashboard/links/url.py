"""Specs for URL link."""

from collections.abc import Iterator


class UrlQueryDependency:
    """Establish a link to the route and the widget or layout item."""

    def __init__(self, field: str) -> None:
        """Construct for URL link."""
        self.__field = field

    def __eq__(self, other: object) -> bool:
        """Return True if other is equal to self."""
        if not isinstance(other, UrlQueryDependency):
            return False
        return self.field == other.field

    def __iter__(self) -> Iterator[tuple[str, str]]:
        yield "field", self.__field

    def __hash__(self) -> int:
        return hash(tuple(self))

    def __repr__(self) -> str:
        return f"U_:{self.__field}"

    def __str__(self) -> str:
        return self._generate_templated_string()

    @property
    def field(self) -> str:
        """Returns id of field to be used from selectable widget.

        Returns:
            str: field id from selectable widget
        """
        return self.__field

    @property
    def item_id(self) -> str:
        """Return Item Id."""
        return f"URL_{self.__field}"

    def _generate_templated_string(self, *, _: int = 0) -> str:
        """Return the template string to be used in dependency."""
        return f"{{{{__ROUTE__{self.field}}}}}"
