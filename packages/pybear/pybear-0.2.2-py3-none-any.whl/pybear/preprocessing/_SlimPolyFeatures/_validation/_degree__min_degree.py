# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers



def _val_degree__min_degree(
    _degree: int,
    _min_degree: int
) -> None:
    """Validate `_degree` and `_min_degree`.

    `_min_degree` must be integer >= 1, `degree` must be integer >= 2,
    and both must fulfill `_min_degree` <= `_max_degree`.

    Parameters
    ----------
    _degree : int
        The maximum polynomial degree of the generated features. The
        minimum value accepted by SPF is 2; the no-op case of simply
        returning the original degree-one data is not allowed.
    _min_degree : int
        The minimum polynomial degree of the generated features.
        Polynomial terms with degree below `_min_degree` are not
        included in the final output array. The minimum value accepted
        by SPF is 1; SPF cannot be used to generate a zero-degree column
        (a column of all ones).

    Returns
    -------
    None

    """


    err_msg = \
        (f"\n'min_degree' must be an integer >= 1.\n'degree' must "
        f"be an integer >= 2.\n'degree' must be greater than or equal "
        f"to 'min_degree'. \ngot {_min_degree=}, {_degree=}.")

    _value_error = 0
    _value_error += isinstance(_degree, bool)
    _value_error += isinstance(_min_degree, bool)
    _value_error += not isinstance(_min_degree, numbers.Integral)
    _value_error += not isinstance(_degree, numbers.Integral)

    if _value_error:
        raise ValueError(err_msg)

    _value_error += _min_degree < 1
    _value_error += _degree < 2
    _value_error += _min_degree > _degree

    if _value_error:
        raise ValueError(err_msg)





