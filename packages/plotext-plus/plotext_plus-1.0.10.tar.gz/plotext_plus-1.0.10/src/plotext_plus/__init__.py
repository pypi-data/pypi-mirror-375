"""\nplotext plots directly on terminal"""

__name__ = "plotext"
__version__ = "5.3.2"

# Clean Public API - Organized by functionality
# ===========================================

# Legacy imports for backward compatibility
# Main plotting functions (most commonly used)
from ._api import BarChart as BarChart
from ._api import CandlestickChart as CandlestickChart
from ._api import Chart as Chart
from ._api import HeatmapChart as HeatmapChart
from ._api import HistogramChart as HistogramChart
from ._api import Legend as Legend
from ._api import LineChart as LineChart
from ._api import MatrixChart as MatrixChart
from ._api import PlotextAPI as PlotextAPI
from ._api import ScatterChart as ScatterChart
from ._api import StemChart as StemChart
from ._api import api as api
from ._api import create_chart as create_chart

# Backward compatibility - Import original API
from ._core import *

# Modern chart classes (object-oriented interface)
from .charts import *
from .plotting import *

# Theme system
from .themes import *

# Utilities and helpers
from .utilities import *
