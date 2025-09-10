"""Class to manage component's data and dependencies."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from copy import copy
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeAlias
from typing import cast

import pandas as pd
from typing_extensions import Unpack

from engineai.sdk.dashboard.links import RouteLink
from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.links.template_string_link import TemplateStringLink
from engineai.sdk.dashboard.links.web_component import WebComponentLink
from engineai.sdk.dashboard.templated_string import InternalDataField
from engineai.sdk.dashboard.widgets.exceptions import (
    WidgetTemplateStringWidgetNotFoundError,
)

from ..connectors import DuckDB
from ..connectors import HttpGet
from ..connectors import Snowflake

if TYPE_CHECKING:
    from engineai.sdk.dashboard.abstract.selectable_widgets import AbstractSelectWidget
    from engineai.sdk.dashboard.abstract.typing import PrepareParams
    from engineai.sdk.dashboard.dependencies import WidgetSelectDependency
    from engineai.sdk.dashboard.interface import OperationInterface as OperationItem

    from ...base import DependencyInterface

DataType = HttpGet | DuckDB | Snowflake | WidgetField
StaticDataType: TypeAlias = pd.DataFrame | dict[str, Any]


class DependencyManager(AbstractFactoryLinkItemsHandler, ABC):
    """Class to manage component's data and dependencies."""

    _DEPENDENCY_ID: str = ""

    def __init__(
        self,
        data: DataType | StaticDataType | None = None,
    ) -> None:
        """Constructor to manage components data.

        Args:
            data: data for the widget.
                Can be a pandas dataframe or a dictionary depending on the widget type,
                or Storage object if the data is to be retrieved from a storage.
        """
        super().__init__()

        if self._DEPENDENCY_ID == "":
            msg = f"Class {self.__class__.__name__}.DEPENDENCY_ID not defined."
            raise NotImplementedError(msg)

        self.dependency_id = self._DEPENDENCY_ID
        self.__dependencies: set[DependencyInterface] = set()
        self._data = self.__set_data(data=data)
        self._json_data = (
            data
            if isinstance(data, pd.DataFrame)
            else pd.DataFrame([data])
            if isinstance(data, dict)
            else None
        )
        self.validation_data = data if isinstance(data, pd.DataFrame | dict) else None

    @property
    def query_parameter(self) -> str:
        """Query parameter."""
        return ""

    @property
    @abstractmethod
    def data_id(self) -> str:
        """Returns data id.

        Returns:
            str: data id
        """

    @abstractmethod
    def validate(self, data: StaticDataType, **kwargs: object) -> None:
        """Page routing has no validations to do."""

    @property
    def dependencies(self) -> set[DependencyInterface]:
        """Returns dependencies of widget.

        Returns:
            set[DependencyInterface]: dependencies of widget
        """
        return self.__dependencies

    def __set_data(
        self,
        data: DataType | StaticDataType | None,
    ) -> DataType | None:
        if data is None or isinstance(data, pd.DataFrame | dict):
            return None

        if isinstance(data, WidgetField):
            return data
        elif isinstance(data, HttpGet):
            copy_data = copy(data)
            copy_data.dependency.dependency_id = self._DEPENDENCY_ID
            if copy_data.additional_paths:
                self.dependency_id += "." + ".".join(copy_data.additional_paths)
            return copy_data
        else:
            data.dependency.dependency_id = self._DEPENDENCY_ID
            return data

    def _prepare_dependencies(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepares dependencies for widget."""
        self.__set_internal_data_field()
        self.__set_template_links_widgets(**kwargs)
        self.__prepare_template_dependencies()
        self.__prepare_widget_fields()
        self.__prepare_dependencies()

    def build_datastore_dependencies(self) -> list[Any]:
        """Build datastore dependencies."""
        return [
            self.__build_dependency(dependency) for dependency in self.__dependencies
        ]

    @staticmethod
    def __build_dependency(dependency: DependencyInterface) -> dict[str, Any]:
        return {
            dependency.input_key: dependency.build(),
        }

    def __prepare_dependencies(self) -> None:
        for item in self.get_all_items(
            HttpGet, DuckDB, Snowflake, WebComponentLink, RouteLink
        ):
            dependency = item.dependency  # type: ignore[union-attr]
            self.__dependencies.add(dependency)

    def __prepare_widget_fields(self) -> None:
        for widget_field in self.get_all_items(WidgetField):
            if isinstance(self._data, WidgetField) and self._data == widget_field:
                dependency = self._data.link_component.select_dependency(
                    dependency_id=self._DEPENDENCY_ID,
                    path=f"selected.0.{self._data.field}",
                )
            else:
                dependency = widget_field.link_component.select_dependency()
            self.__dependencies.add(cast("WidgetSelectDependency", dependency))

    def __prepare_template_dependencies(self) -> None:
        for template_link in self.get_all_items(TemplateStringLink):
            if template_link.is_widget_field():
                dependency = template_link.component.select_dependency(
                    dependency_id=template_link.widget_id
                )

                self.__dependencies.add(
                    cast(
                        "WidgetSelectDependency",
                        dependency,
                    )
                )
            elif template_link.is_route_link():
                route_link = template_link.route_link
                self.__dependencies.add(route_link.dependency)
            elif template_link.is_web_component_link():
                self.__dependencies.add(template_link.web_component_link.dependency)

    def __set_internal_data_field(self) -> None:
        for internal_data_field in self.get_all_items(InternalDataField):
            if internal_data_field.dependency_id == "":
                internal_data_field.set_dependency_id(dependency_id=self._DEPENDENCY_ID)

    def __set_template_links_widgets(
        self,
        **kwargs: Unpack[PrepareParams],
    ) -> None:
        dashboard_slug = kwargs["dashboard_slug"]
        selectable_widgets: dict[str, AbstractSelectWidget] = kwargs[
            "selectable_widgets"
        ]
        for template_link in self.get_all_items(TemplateStringLink):
            if template_link.is_web_component_link():
                continue
            if template_link.is_widget_field():
                if template_link.widget_id not in selectable_widgets:
                    raise WidgetTemplateStringWidgetNotFoundError(
                        slug=dashboard_slug,
                        widget_id=self.data_id,
                        template_widget_id=template_link.widget_id,
                    )
                template_link.component = cast(
                    "AbstractSelectWidget",
                    selectable_widgets.get(template_link.widget_id),
                )
            elif template_link.is_route_link():
                template_link.component = kwargs["page"].route

    def __add_operations_dependencies(
        self,
        operations: list[OperationItem],
    ) -> None:
        for operation in operations:
            for dependency in operation.dependencies:
                self.__dependencies.add(dependency)
