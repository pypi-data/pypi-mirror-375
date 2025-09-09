# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers



def _val_string_frequency(
    _string_frequency: dict[str, int]
) -> None:
    """Validate `string_frequency`.

    Validate the string_frequency dictionary
    - is a dictionary
    - has strings for keys
    - has non-bool integers for values, and all values are >= 1

    Parameters
    ----------
    _string_frequency : dict[str, int]
        A dictionary of unique character strings and counts.

    Returns
    -------
    None


    """


    assert isinstance(_string_frequency, dict)
    for k, v in _string_frequency.items():
        assert isinstance(k, str)
        assert isinstance(v, int)
        assert not isinstance(v, bool)
        assert v >= 1








