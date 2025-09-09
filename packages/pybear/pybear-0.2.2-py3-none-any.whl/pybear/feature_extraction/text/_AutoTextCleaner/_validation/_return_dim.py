# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import ReturnDimType



def _val_return_dim(
    _return_dim: ReturnDimType
) -> None:
    """Validate 'return_dim', must be None, 1, or 2.

    Parameters
    ----------
    _return_dim : ReturnDimType
        The dimensionality of the container to return the cleaned data
        in, regardless of the input dimension. If None, return the output
        with the same dimensionality as given.

    Returns
    -------
    None

    Notes
    -----

    **Type Aliases**

    ReturnDimType:
        Literal[1, 2] | None

    """

    # return_dim:Literal[1, 2] | None = None,


    if _return_dim is None:
        return


    err_msg = "'return_dim' must be None, 1, or 2."


    if _return_dim not in [1, 2]:
        raise ValueError(err_msg)





