# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Literal



def _val_keep(
    _keep:Literal['first', 'last', 'random']
) -> None:
    """Validate `_keep` - must be 'first', 'last', or 'random'.

    Parameters
    ----------
    _keep : Literal['first', 'last', 'random']
        The strategy for keeping a single representative from a set
        of identical columns in the polynomial expansion. This is
        over-ruled if a polynomial feature is a duplicate of one of
        the original features, and the original feature will always be
        kept and the polynomial duplicates will always be dropped. One
        of SPF's design rules is to never alter the originally passed
        data, so the original feature will always be kept. Under SPF's
        design rule that the original data has no duplicate columns,
        an expansion feature cannot be identical to 2 of the original
        features. In all cases where the duplicates are only within the
        polynomial expansion, 'first' retains the column left-most in
        the expansion (lowest degree); 'last' keeps the column right-most
        in the expansion (highest degree); 'random' keeps a single
        randomly-selected feature of the set of duplicates.

    Returns
    -------
    None

    """


    _err_msg = lambda _required: f"'keep' must be one of {', '.join(_required)}"
    _required = ('first', 'last', 'random')

    if not isinstance(_keep, str):
        raise TypeError(_err_msg(_required))

    if sum([_ == _keep for _ in _required]) != 1:
        raise ValueError(_err_msg(_required))
    del _err_msg, _required




