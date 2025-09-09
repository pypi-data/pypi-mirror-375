# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import XContainer



def _val_X(
    _X: XContainer
) -> None:
    """Validate the data.

    Parameters
    ----------
    _X : XContainer
        The data to have nan-like values replaced.

    Returns
    -------
    None

    """


    _err_msg = (
        f"'X' must be an array-like with a copy() or clone() method, "
        f"such as python built-ins, numpy arrays, scipy sparse matrices "
        f"or arrays, pandas dataframes/series, polars dataframes/series. "
        f"\nif passing a scipy sparse object, it cannot be dok or lil. "
        f"\ntuples are allowed, sets are disallowed."
    )

    try:
        iter(_X)
        if isinstance(_X, tuple):
            # tuple does not have copy() method, gets a free pass
            raise UnicodeError
        if isinstance(_X, (str, dict, set)):
            raise Exception
        if not hasattr(_X, 'copy') and not hasattr(_X, 'clone'):
            # copy for py, numpy, pandas, and scipy; clone for polars
            raise Exception
        if hasattr(_X, 'toarray'):
            if not hasattr(_X, 'data'): # ss dok
                raise Exception
            elif all(map(isinstance, _X.data, (list for _ in _X.data))):
                # ss lil
                raise Exception
            else:
                _X = _X.data
    except UnicodeError:
        pass
    except:
        raise TypeError(_err_msg)







