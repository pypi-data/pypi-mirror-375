# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
    TypeAlias
)
import numpy.typing as npt

import pandas as pd
import polars as pl



PythonTypes: TypeAlias = Sequence[Sequence[str]]

NumpyTypes: TypeAlias = npt.NDArray[str]

PandasTypes: TypeAlias = pd.DataFrame

PolarsTypes: TypeAlias = pl.DataFrame

XContainer: TypeAlias = PythonTypes | NumpyTypes | PandasTypes | PolarsTypes

XWipContainer: TypeAlias = list[list[str]]







