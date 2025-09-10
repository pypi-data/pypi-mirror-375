"""Abstract class to implement Select Widgets."""

from abc import ABC
from abc import abstractmethod

from engineai.sdk.dashboard.base import AbstractFactory


class AbstractSelectWidget(AbstractFactory, ABC):
    """Abstract class to implement Select Widgets."""

    @property
    @abstractmethod
    def widget_id(self) -> str:
        """Return the widget id."""
        ...
