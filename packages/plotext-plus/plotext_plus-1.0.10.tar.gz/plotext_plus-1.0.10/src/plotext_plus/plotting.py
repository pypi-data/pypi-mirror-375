# /usr/bin/env python3

"""
Plotext Core Plotting Functions - Clean Public API
=================================================

This module provides the main plotting functions that users interact with.
All the core plotting capabilities are exposed through clean, public interfaces.
"""

# Import core functions for media handling
# Import all main plotting functions from the internal core module
from ._core import banner_mode  # Interactive features
from ._core import bar
from ._core import build
from ._core import candlestick
from ._core import clc
from ._core import cld
from ._core import clear_color
from ._core import clear_data
from ._core import clear_figure
from ._core import clear_terminal
from ._core import clf
from ._core import clt
from ._core import colorize
from ._core import frame
from ._core import grid
from ._core import image_plot
from ._core import limitsize
from ._core import matrix_plot
from ._core import plot
from ._core import plotsize  # Figure management
from ._core import save_fig  # Data utilities
from ._core import scatter  # Basic plotting functions
from ._core import show  # Layout and display
from ._core import sleep
from ._core import subplot
from ._core import subplots
from ._core import theme  # Colors and themes
from ._core import title  # Plot customization
from ._core import xlabel
from ._core import xlim
from ._core import xscale
from ._core import ylabel
from ._core import ylim
from ._core import yscale

# Import global functions for media handling
from ._global import play_gif
from ._global import play_video

# Import utilities that users might need
from ._utility import colorize as color_text
from ._utility import delete_file
from ._utility import download as download_file
from ._utility import terminal_height
from ._utility import terminal_width

__all__ = [
    # Basic plotting
    "scatter",
    "plot",
    "bar",
    "matrix_plot",
    "candlestick",
    # Plot customization
    "title",
    "xlabel",
    "ylabel",
    "xlim",
    "ylim",
    "xscale",
    "yscale",
    "grid",
    "frame",
    # Colors and themes
    "theme",
    "colorize",
    "color_text",
    # Layout and display
    "show",
    "build",
    "sleep",
    "clear_figure",
    "clear_data",
    "clear_terminal",
    "clear_color",
    "clf",
    "cld",
    "clt",
    "clc",
    # Figure management
    "plotsize",
    "limitsize",
    "subplots",
    "subplot",
    # Utilities
    "save_fig",
    "terminal_width",
    "terminal_height",
    "banner_mode",
    # Media handling
    "download_file",
    "delete_file",
    "image_plot",
    "play_gif",
    "play_video",
]
