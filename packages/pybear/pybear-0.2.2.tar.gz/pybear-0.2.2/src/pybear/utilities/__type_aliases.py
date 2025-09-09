# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    TypeAlias,
)
import numpy.typing as npt

import pandas as pd
import polars as pl
import scipy.sparse as ss



Python1DTypes: TypeAlias = list | tuple | set
Python2DTypes: TypeAlias = list[list] | tuple[tuple]
PythonTypes: TypeAlias = Python1DTypes | Python2DTypes

Numpy1DTypes: TypeAlias = npt.NDArray
Numpy2DTypes: TypeAlias = npt.NDArray
NumpyTypes: TypeAlias = Numpy1DTypes | Numpy2DTypes

Pandas1DTypes: TypeAlias = pd.Series
Pandas2DTypes: TypeAlias = pd.DataFrame
PandasTypes: TypeAlias = Pandas1DTypes | Pandas2DTypes

Polars1DTypes: TypeAlias = pl.Series
Polars2DTypes: TypeAlias = pl.DataFrame
PolarsTypes: TypeAlias = Polars1DTypes | Polars2DTypes

ScipySparseTypes: TypeAlias = (
    ss.csc_matrix | ss.csc_array | ss.csr_matrix | ss.csr_array
    | ss.coo_matrix | ss.coo_array | ss.dia_matrix | ss.dia_array
    | ss.lil_matrix | ss.lil_array | ss.dok_matrix | ss.dok_array
    | ss.bsr_matrix | ss.bsr_array
)



