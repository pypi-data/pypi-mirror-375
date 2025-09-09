# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Sequence,
    TypeAlias,
)
import numpy.typing as npt

import pandas as pd
import polars as pl
import scipy.sparse as ss



PythonTypes: TypeAlias = Sequence | Sequence[Sequence]

NumpyTypes: TypeAlias = npt.NDArray

PandasTypes: TypeAlias = pd.DataFrame | pd.Series

PolarsTypes: TypeAlias = pl.DataFrame | pl.Series

# dok and lil are left out intentionally
SparseTypes: TypeAlias = (
    ss._csr.csr_matrix | ss._csc.csc_matrix | ss._coo.coo_matrix
    | ss._dia.dia_matrix | ss._bsr.bsr_matrix | ss._csr.csr_array
    | ss._csc.csc_array | ss._coo.coo_array | ss._dia.dia_array
    | ss._bsr.bsr_array
)

XContainer: TypeAlias = \
    PythonTypes | NumpyTypes | PandasTypes | PolarsTypes | SparseTypes





