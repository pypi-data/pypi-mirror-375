"""Spec for ContentItem class."""

from __future__ import annotations

from typing import Any

from .markdown import MarkdownItem

ContentItem = MarkdownItem


def build_content_item(item: ContentItem) -> dict[str, Any]:
    """Builds item for Content Widget.

    Args:
        item (ContentItem): Item to build.

    Returns:
        Input object for Dashboard API
    """
    return {"markdown": item.build()}
