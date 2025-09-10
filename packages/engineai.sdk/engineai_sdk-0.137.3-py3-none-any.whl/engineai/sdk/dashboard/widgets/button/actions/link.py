"""Spec for Button Action."""

from typing import Any

import pandas as pd
from typing_extensions import override

from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.links.route_link import RouteLink
from engineai.sdk.dashboard.links.widget_field import WidgetField
from engineai.sdk.dashboard.widgets.components.actions.links import DashboardLink
from engineai.sdk.dashboard.widgets.components.actions.links import UrlLink
from engineai.sdk.dashboard.widgets.utils import build_data


class ButtonWidgetActionLink(AbstractFactoryLinkItemsHandler):
    """Spec for Button Link Action."""

    def __init__(
        self,
        *,
        data: WidgetField | RouteLink | pd.DataFrame,
        link: UrlLink | DashboardLink,
    ) -> None:
        """Construct spec for Button Link Action.

        Args:
            data: data containing the actual url for the link
            link: link configuration. Either a UrlLink for redirections outside
            of the dashboard or a DashboardLink for redirections to dashboards
            inside of the app.
        """
        super().__init__()
        self.__data = data
        self.__link = link

    def validate(self) -> None:
        """Link validations for the data passed."""
        if isinstance(self.__data, pd.DataFrame):
            self.__link.validate(data=self.__data, widget_class="Button Widget")

    def build_link(self) -> dict[str, Any]:
        """Build the link property based on it's type."""
        if isinstance(self.__link, UrlLink):
            return {"hyperLink": self.__link.build()}
        else:
            return {"dashboardHyperLink": self.__link.build()}

    def build_data(self) -> dict[str, Any]:
        """Build the data property based on it's type."""
        if isinstance(self.__data, pd.DataFrame):
            return build_data(path="", json_data=self.__data)
        else:
            return build_data(
                path=f"{self.__data.dependency.dependency_id}.0.{self.__data.field}"
            )

    @override
    def build(self) -> dict[str, Any]:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API
        """
        return {"data": self.build_data(), "link": self.build_link()}
