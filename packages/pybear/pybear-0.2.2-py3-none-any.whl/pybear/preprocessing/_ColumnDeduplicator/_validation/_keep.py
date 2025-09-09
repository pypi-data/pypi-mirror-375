# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import KeepType



def _val_keep(
    _keep: KeepType
) -> None:
    """Validate keep - must be 'first', 'last', or 'random'.

    Parameters
    ----------
    _keep : KeepType
        The strategy for keeping a single representative from a set of
        identical columns. 'first' retains the column left-most in the
        data; 'last' keeps the column right-most in the data; 'random'
        keeps a single randomly-selected column from the set of
        duplicates.

    Returns
    -------
    None

    """


    _err_msg = f"'keep' must be one of {', '.join(['first', 'last', 'random'])}"

    if not isinstance(_keep, str):
        raise TypeError(_err_msg)

    if sum([_ == _keep for _ in ['first', 'last', 'random']]) != 1:
        raise ValueError(_err_msg)
    del _err_msg





