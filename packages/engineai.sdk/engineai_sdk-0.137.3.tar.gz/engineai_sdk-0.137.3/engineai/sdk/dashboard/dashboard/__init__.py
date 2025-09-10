"""Spec for building a dashboard."""

from .dashboard import Dashboard
from .page.page import Page
from .page.root import RootGrid
from .page.route import Route

__all__ = [
    # .dashboard
    "Dashboard",
    "Page",
    "RootGrid",
    "Route",
]
