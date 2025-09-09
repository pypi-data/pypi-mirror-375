# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



def _val_equal_nan(
    _equal_nan: bool
) -> None:
    """Validate `equal_nan`; must be bool.

    Parameters
    ----------
    _equal_nan : bool
        Sets the strategy for determining the equality of nan-like values
        against themselves or against non-nan-like values. This has
        subtly different implications in the modules that use this. See
        the documentation for the individual modules.

    Return
    ------
    None

    """


    if not isinstance(_equal_nan, bool):
        raise TypeError(f"'equal_nan' must be bool")





