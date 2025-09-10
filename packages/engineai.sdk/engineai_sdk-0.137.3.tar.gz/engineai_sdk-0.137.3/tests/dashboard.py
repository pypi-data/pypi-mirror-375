import pandas as pd

from engineai.sdk.dashboard.dashboard import Dashboard
from engineai.sdk.dashboard.dashboard.page.page import Page
from engineai.sdk.dashboard.dashboard.page.route import Route
from engineai.sdk.dashboard.data.connectors import Snowflake
from engineai.sdk.dashboard.widgets.content import Content
from engineai.sdk.dashboard.widgets.content.markdown import MarkdownItem
from engineai.sdk.dashboard.widgets.table import Table
from engineai.sdk.dashboard.widgets.table.columns.items.number import NumberColumn
from engineai.sdk.dashboard.widgets.toggle import Toggle

route = Route(
    data=Snowflake(
        query="""
            SELECT 'Route-Test' AS name
            """,
        slug="test",
    ),
    query_parameter="reference",
)

toggle = Toggle(
    id_column="id",
    label_column="label",
    data=pd.DataFrame(
        {"id": ["1", "2", "3"], "label": ["Label 1", "Label 2", "Label 3"]}
    ),
    label=f"Toggle {route.selected.NAME}",
)

content = Content(
    title=f"Title {route.selected.NAME}",
    data={"markdown": "Hello World!"},
).add_items(MarkdownItem("markdown"))

table = Table(
    title=f"Sample Table {route.selected.NAME} linked to Toggle",
    data=Snowflake(
        slug="test",
        query=f"select {toggle.selected.id} as id",
    ),
    columns=[NumberColumn(data_column="ID", label="Value")],
)

table1 = Table(
    title=f"Sample Table {route.selected.NAME}",
    data=pd.DataFrame({"value": [1, 2, 3]}),
    columns=[NumberColumn(data_column="value", label="Value")],
)

page = Page(
    content=[toggle, content, table, table1],
    title=f"Page Title {route.selected.NAME}",
    route=route,
)

dashboard = Dashboard(
    workspace_slug="test",
    app_slug="test",
    slug="test",
    content=page,
)
