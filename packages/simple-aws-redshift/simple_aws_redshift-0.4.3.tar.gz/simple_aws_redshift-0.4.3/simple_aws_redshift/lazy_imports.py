# -*- coding: utf-8 -*-

from soft_deps.api import MissingDependency

try:
    import tabulate
except ImportError:  # pragma: no cover
    tabulate = MissingDependency("pandas", "pip install tabulate")


try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = MissingDependency("pandas", "pip install pandas")

try:
    import polars as pl
except ImportError:  # pragma: no cover
    pl = MissingDependency("polars", "pip install polars")
