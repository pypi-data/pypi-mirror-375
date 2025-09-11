# /usr/bin/env python3

"""
Plotext Utilities - Clean Public API
===================================

This module provides utility functions for terminal operations, file handling,
and other helper functionality that users might need.
"""

# Import global utilities - check what's actually available
# Import utility functions from internal modules
from ._global import test_bar_data_url
from ._global import test_data_url
from ._global import test_gif_url
from ._global import test_image_url
from ._global import test_video_url

# Import output utilities
from ._output import error as log_error
from ._output import info as log_info
from ._output import success as log_success
from ._output import warning as log_warning
from ._utility import colorize
from ._utility import delete_file
from ._utility import download
from ._utility import matrix_size
from ._utility import no_color
from ._utility import terminal_width

__all__ = [
    # Terminal utilities
    "terminal_width",
    "colorize",
    "no_color",
    # Matrix utilities
    "matrix_size",
    # File utilities
    "delete_file",
    "download",
    # Test data URLs
    "test_data_url",
    "test_bar_data_url",
    "test_image_url",
    "test_gif_url",
    "test_video_url",
    # Logging utilities
    "log_info",
    "log_success",
    "log_warning",
    "log_error",
]
