#!/usr/bin/env python3
"""
Created on Wed Dec  1 18:35:00 2021.

@author: pierrot

"""
import sys

# Import version dynamically from Poetry
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version


# Conditional import for stateful_ops to avoid numba issues during documentation builds
if "sphinx" in sys.modules:
    # During documentation builds, skip heavy stateful_ops imports
    AggStream = None
    by_x_rows = None
else:
    from .stateful_ops import AggStream
    from .stateful_ops import by_x_rows

from .stateful_loop import StatefulLoop
from .stateful_ops import AsofMerger
from .store import OrderedParquetDataset
from .store import Store
from .store import check_cmidx
from .store import conform_cmidx
from .store import is_toplevel
from .store import sublevel
from .store import toplevel
from .store import write


try:
    __version__ = version("oups")
except PackageNotFoundError:
    # Package is not installed, likely in development
    __version__ = "development"
