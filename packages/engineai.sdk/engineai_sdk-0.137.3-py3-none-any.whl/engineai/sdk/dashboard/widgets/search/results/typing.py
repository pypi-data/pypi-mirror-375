"""Search Widget Custom typing."""

from engineai.sdk.dashboard.widgets.search.results.number import ResultNumberItem
from engineai.sdk.dashboard.widgets.search.results.text import ResultTextItem

ResultItemType = ResultTextItem | ResultNumberItem
