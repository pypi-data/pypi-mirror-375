"""Specs for selectable layouts in a dashboard vertical grid."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any

from typing_extensions import Unpack

from engineai.sdk.dashboard.abstract.layout import AbstractLayoutItem
from engineai.sdk.dashboard.interface import SelectableInterface
from engineai.sdk.dashboard.interface import WidgetInterface as Widget
from engineai.sdk.dashboard.layout.exceptions import ElementHeightNotDefinedError
from engineai.sdk.dashboard.layout.typings import LayoutItem
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from .exceptions import SelectableDuplicatedLabelError
from .exceptions import SelectableHasNoItemsError
from .exceptions import SelectableWithDefaultSelectionError

if TYPE_CHECKING:
    from engineai.sdk.dashboard.abstract.typing import PrepareParams
    from engineai.sdk.dashboard.layout.typings import LayoutItem
    from engineai.sdk.dashboard.templated_string import TemplatedStringItem


class SelectableItem(AbstractLayoutItem, ABC):
    """Spec for item for a selectable section in a dashboard vertical grid layout."""

    def __init__(
        self,
        *,
        label: TemplatedStringItem,
        content: LayoutItem,
        default_selected: bool = False,
    ) -> None:
        """Construct tab for tab section dashboard vertical grid layout.

        Args:
            label: label to be displayed in dashboard
            content: item to be added in selectable
                layout.
            default_selected: set item as default selected.
        """
        super().__init__()
        self.__label = label
        self.__content = content
        self.__height: int | float | None = None
        self.__default_selected = default_selected

    @property
    def default_selected(self) -> bool:
        """Returns whether tab is default selected.

        Returns:
            bool: whether tab is default selected
        """
        return self.__default_selected

    @default_selected.setter
    def default_selected(self, value: bool) -> None:
        """Set tab as default selected.

        Args:
            value (bool): set tab as default selected
        """
        self.__default_selected = value

    def prepare(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepare tab.

        Args:
            **kwargs (Unpack[PrepareParams]): keyword arguments
        """
        self.__content.prepare(**kwargs)

    def prepare_heights(self, row_height: int | float | None = None) -> None:
        """Prepare Selectable Layout heights."""
        if not isinstance(self.__content, Widget):
            self.__content.prepare_heights(row_height=row_height)
        self.__height = row_height or self.__content.height

    @property
    def height(self) -> float:
        """Returns height."""
        if self.__height is None:
            raise ElementHeightNotDefinedError
        return self.__height

    @property
    def has_custom_heights(self) -> bool:
        """Returns if the Selectable Item has custom heights in its inner components."""
        return (
            False
            if isinstance(self.__content, Widget)
            else self.__content.has_custom_heights
        )

    @property
    def item(self) -> LayoutItem:
        """Returns the underlying item."""
        return self.__content

    @property
    def label(self) -> TemplatedStringItem:
        """Returns label.

        Returns:
            str: label
        """
        return self.__label

    def items(self) -> list[AbstractLayoutItem]:
        """Returns list of grid items that need to be inserted individually."""
        return self.__content.items()

    @abstractmethod
    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """


class SelectableSection(SelectableInterface, ABC):
    """Spec for section in a dashboard vertical grid layout."""

    _HEIGHT_TITLE = 0.48

    def __init__(
        self,
    ) -> None:
        """Construct Selectable Section for dashboard vertical grid layout."""
        super().__init__()
        self._items: list[SelectableItem] = []
        self.__item_labels: set[TemplatedStringItem] = set()
        self.__has_default_selection: bool = False
        self.__height: int | float | None = None

    def prepare(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepare Select Section.

        Args:
            **kwargs (Unpack[PrepareParams]): keyword arguments
        """
        # At this level the user already added the items to the SelectableSection
        # so we can assume that there's no other element that will be added.
        # If there's a default selection,
        # we will set the first item as default selected.
        if self.__has_default_selection is False:
            self._items[0].default_selected = True
            self.__has_default_selection = True

        for item in self._items:
            item.prepare(**kwargs)

    def prepare_heights(self, row_height: int | float | None = None) -> None:
        """Prepare Selectable Layout heights."""
        for item in self._items:
            item.prepare_heights(row_height=row_height)
        self.__set_height(row_height)

    def __set_height(self, row_height: int | float | None = None) -> None:
        self.__height = (
            row_height or max(item.height for item in self._items)
        ) + self._HEIGHT_TITLE

    @property
    def height(self) -> int | float:
        """Returns height."""
        if self.__height is None:
            raise ElementHeightNotDefinedError
        return self.__height

    @property
    def has_custom_heights(self) -> bool:
        """Returns whether grid has custom heights."""
        return any(item.has_custom_heights for item in self._items)

    def items(self) -> list[AbstractLayoutItem]:
        """Returns list of grid items that need to be inserted individually."""
        items: list[AbstractLayoutItem] = [self]
        for selectable in self._items:
            items += selectable.items()
        return items

    def _add_items(self, *items: SelectableItem) -> None:
        if len(items) == 0:
            raise SelectableHasNoItemsError(selectable_class=self.__class__.__name__)

        for item in items:
            self.__add_item(item=item)

    def __add_item(
        self,
        *,
        item: SelectableItem,
    ) -> SelectableSection:
        """Add select to select section.

        Args:
            item (SelectableItem): select to be added

        Raises:
            - if select section already has a default selection select
            - if select section already has a select with the same id or label
        """
        if item.default_selected is True and self.__has_default_selection is True:
            raise SelectableWithDefaultSelectionError(
                selectable_class=self.__class__.__name__
            )
        if item.default_selected:
            self.__has_default_selection = item.default_selected

        if item.label in self.__item_labels:
            raise SelectableDuplicatedLabelError(
                selectable_class=self.__class__.__name__,
                selectable_item_label=str(item.label),
            )

        self.__item_labels.add(item.label)
        self._items.append(item)
        return self
