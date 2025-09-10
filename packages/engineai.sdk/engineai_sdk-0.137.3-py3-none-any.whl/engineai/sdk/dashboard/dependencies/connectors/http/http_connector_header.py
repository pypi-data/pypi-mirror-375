"""Specs for defining an Http Header."""

from typing import Any

from engineai.sdk.dashboard.base import AbstractFactory


class HttpConnectorHeader(AbstractFactory):
    """Specs for defining an Http Connector Header."""

    def __init__(self, key: str, value: str) -> None:
        """Constructor for HttpConnectorHeader class.

        Args:
            key: key of the header.
            value: value of the header.

        Note: Only `application/json` is supported for `Content-Type` header.
        """
        self.__key = key
        self.__value = value

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {"key": self.__key, "value": self.__value}
