# /usr/bin/env python3

"""
Plotext Modern Chart Classes - Clean Public API
==============================================

This module provides the modern, object-oriented chart classes for more
structured plotting workflows. These classes offer a cleaner, more intuitive
interface compared to the traditional function-based API.
"""

# Import all chart classes from the internal API module
from ._api import BarChart
from ._api import CandlestickChart
from ._api import Chart  # Base classes
from ._api import HeatmapChart
from ._api import HistogramChart
from ._api import Legend
from ._api import LineChart
from ._api import MatrixChart
from ._api import PlotextAPI
from ._api import ScatterChart  # Specific chart types
from ._api import StemChart
from ._api import api
from ._api import create_chart  # Convenience functions
from ._api import enable_banners  # Banner and logging utilities
from ._api import log_error
from ._api import log_info
from ._api import log_success
from ._api import log_warning
from ._api import quick_bar
from ._api import quick_donut
from ._api import quick_line
from ._api import quick_pie
from ._api import quick_scatter

__all__ = [
    # Base classes
    "Chart",
    "Legend",
    "PlotextAPI",
    "api",
    # Chart types
    "ScatterChart",
    "LineChart",
    "BarChart",
    "HistogramChart",
    "CandlestickChart",
    "HeatmapChart",
    "MatrixChart",
    "StemChart",
    # Convenience functions
    "create_chart",
    "quick_scatter",
    "quick_line",
    "quick_bar",
    "quick_pie",
    "quick_donut",
    # Utilities
    "enable_banners",
    "log_info",
    "log_success",
    "log_warning",
    "log_error",
]
