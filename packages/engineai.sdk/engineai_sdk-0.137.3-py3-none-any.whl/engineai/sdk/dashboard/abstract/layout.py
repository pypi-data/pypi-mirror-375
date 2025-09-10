"""Abstract Class implemented by main Dashboard Items."""

from __future__ import annotations

import inspect
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from typing_extensions import Unpack

from engineai.sdk.dashboard.base import AbstractFactory

if TYPE_CHECKING:
    from engineai.sdk.dashboard.abstract.typing import PrepareParams


class AbstractLayoutItem(AbstractFactory, ABC):
    """Abstract Class implemented by main Dashboard Items."""

    INPUT_KEY: ClassVar[str]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "INPUT_KEY") and not inspect.isabstract(cls):
            msg = f"Class {cls.__name__} lacks required class variable INPUT_KEY"
            raise NotImplementedError(msg)

    @abstractmethod
    def items(self) -> list[AbstractLayoutItem]:
        """Returns a list of items contained by the current item.

        Returns:
            List["AbstractLayoutItem"]: List of items contained by the current item.
        """

    @property
    @abstractmethod
    def height(self) -> float:
        """Returns height."""

    @property
    @abstractmethod
    def has_custom_heights(self) -> bool:
        """Returns if has custom heights."""

    @abstractmethod
    def prepare_heights(self, row_height: int | float | None = None) -> None:
        """Prepare heights."""

    @abstractmethod
    def prepare(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepare tab.

        Args:
            **kwargs (Unpack[PrepareParams]): keyword arguments
        """
