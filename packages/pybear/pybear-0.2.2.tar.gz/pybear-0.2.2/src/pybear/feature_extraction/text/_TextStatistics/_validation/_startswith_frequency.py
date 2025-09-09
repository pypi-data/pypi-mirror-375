# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers



def _val_startswith_frequency(
    _startswith_frequency: dict[str, int]
) -> None:
    """Validate `startswith_frequency`.

    Validate the startswith_frequency dictionary
    - is a dictionary
    - has strings for keys, len of string must be 1
    - has non-bool integers for values, and all values are >= 1

    Parameters
    ----------
    _startswith_frequency :dict[str, int]
        A dictionary of unique first characters and counts.

    Returns
    -------
    None

    """


    assert isinstance(_startswith_frequency, dict)
    for k, v in _startswith_frequency.items():
        assert isinstance(k, str)
        assert len(k) == 1
        assert isinstance(v, int)
        assert not isinstance(v, bool)
        assert v >= 1








