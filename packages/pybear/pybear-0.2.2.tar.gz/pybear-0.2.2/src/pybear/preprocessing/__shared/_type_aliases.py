# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy.typing as npt
from typing import (
    TypeAlias,
)

import pandas as pd
import polars as pl
import scipy.sparse as ss



XContainer: TypeAlias = (
    npt.NDArray | pd.DataFrame | pl.DataFrame
    | ss._csr.csr_matrix | ss._csc.csc_matrix | ss._coo.coo_matrix
    | ss._dia.dia_matrix | ss._lil.lil_matrix | ss._dok.dok_matrix
    | ss._bsr.bsr_matrix | ss._csr.csr_array | ss._csc.csc_array
    | ss._coo.coo_array | ss._dia.dia_array | ss._lil.lil_array
    | ss._dok.dok_array | ss._bsr.bsr_array
)




