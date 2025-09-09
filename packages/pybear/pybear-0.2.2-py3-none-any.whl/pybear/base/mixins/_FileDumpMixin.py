# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Callable,
    Sequence,
    TypeAlias
)

from ..__type_aliases import (
    NumpyTypes,
    PandasTypes,
    PolarsTypes
)

import functools

import numpy as np
import pandas as pd
import polars as pl

from .._validate_user_input import validate_user_str

from .._check_1D_str_sequence import check_1D_str_sequence
from .._check_2D_str_array import check_2D_str_array



PythonTypes: TypeAlias = Sequence[str] | Sequence[Sequence[str]] | set[str]

XContainer: TypeAlias = PythonTypes | NumpyTypes | PandasTypes | PolarsTypes



class FileDumpMixin:
    """A mixin for pybear text transformers that allows the user to save
    data in-situ.

    Notes
    -----

    **Type Aliases**

    PythonTypes:
        Sequence[str] | Sequence[Sequence[str]] | set[str]

    NumpyTypes:
        numpy.ndarray[str]

    PandasTypes:
        pandas.Series | pandas.DataFrame

    PolarsTypes:
        polars.Series | polars.DataFrame

    XContainer:
        PythonTypes | NumpyTypes | PandasTypes | PolarsTypes

    """


    def _dump_to_file_wrapper(foo) -> Callable[[XContainer], None]:
        """Wrapper function for dumping `X` to csv or txt."""

        @functools.wraps(foo)
        def _writer_function(self, _X: XContainer) -> None:

            is_1D = self._validate_X_container(_X)
            is_2D = bool(1 - is_1D)

            if is_2D:
                if isinstance(_X, pd.DataFrame):
                    __X = list(map(" ".join, map(lambda x: map(str, x), _X.values)))
                elif isinstance(_X, pl.DataFrame):
                    __X = list(map(" ".join, map(lambda x: map(str, x), _X.rows())))
                else:
                    __X = list(map(" ".join, map(lambda x: map(str, x), _X)))
            else:
                __X = list(map(str, _X))


            for _ in range(10):
                filename = input(f'Enter filename without extension > ')
                _opt = validate_user_str(
                    f'User entered *{filename}*  ---  Accept? (y/n) > ',
                    'YN'
                )
                if _opt == 'Y':
                    foo(self, __X, filename)
                    break
                elif _opt == 'N':
                    continue
                else:
                    raise Exception
            else:
                raise ValueError(f"too many tries.")

            del __X

            print(f'\n*** Dump to file successful. ***\n')


        return _writer_function


    @_dump_to_file_wrapper
    def dump_to_csv(self, X: list[str], filename: str) -> None:
        """Dump `X` to csv.

        Parameters
        ----------
        X : list[str]
            The data.
        filename : str
            The name for the saved csv file.

        Returns
        -------
        None

        """

        print(f'\nSaving data to csv...')

        pd.Series(
            data=list(map(str, X))
        ).to_csv(f"{filename}.csv", header=True, index=False)

        return


    @_dump_to_file_wrapper
    def dump_to_txt(self, X: list[str], filename: str) -> None:
        """Dump `X` to txt.

        Parameters
        ----------
        X : list[str]
            The data.
        filename : str
            The name for the saved txt file.

        Returns
        -------
        None

        """


        print(f'\nSaving data to txt file...')

        with open(f"{filename}.txt", 'w') as f:
            for line in X:
                f.write(line + '\n')
            f.close()

        return


    def _validate_X_container(self, X: XContainer) -> bool:
        """Validate that `X` is an allowed container and is 1D or 2D.

        This checks the dimensionality of `X`. Must be 1D or 2D. Returns
        True if the data is 1D, False if the data is 2D.

        Parameters
        ----------
        X : XContainer
            The data.

        Returns
        -------
        is_1D : bool
            True if 1D, False if 2D.

        """


        if not isinstance(
            X,
            (list, tuple, set, np.ndarray, pd.Series, pd.DataFrame,
             pl.Series, pl.DataFrame)
        ):
            raise TypeError(f"invalid container for X, got {type(X)}")


        err_msg = f"FileDumpMixin - disallowed dimension of X, must be 1D or 2D."

        if hasattr(X, 'shape'):
            _dim = len(X.shape)
            if _dim not in [1,2]:
                raise ValueError(err_msg)


        try:
            check_1D_str_sequence(X, require_all_finite=False)
            return True
        except:
            pass

        try:
            check_2D_str_array(X, require_all_finite=False)
            return False
        except:
            pass


        # if we get to here both check_XD_str_X failed
        raise ValueError(err_msg)


        return (_dim == 1)






