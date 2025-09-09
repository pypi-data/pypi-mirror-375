# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import GetStatisticsType



def _val_get_statistics(
    _get_statistics: GetStatisticsType | None
) -> None:
    """Validate 'get_statistics'.

    Must be None or a dictionary with 'before' and 'after' keys. The
    values for the keys must be None or bool.

    Parameters
    ----------
    _get_statistics : GetStatisticsType | None
        A dictionary indicating if TextStatistics is to accumulate
        statistics on the incoming and/or outgoing data, and if so,
        whether to store uniques. When 'store_uniques' is True there
        is risk of memory explosion, especially for the incoming
        TextStatistics.

    Returns
    -------
    None

    Notes
    -----

    **Type Aliases**

    class GetStatisticsType(TypedDict):
        before: Required[bool | None]

        after: Required[bool | None]

    """


    if _get_statistics is None:
        return


    err_msg = (f"'get_statistics' must be None or a dictionary with "
               f"'before' and 'after' keys whose values must be None or "
               f"bool.")


    if not isinstance(_get_statistics, dict):
        raise TypeError(err_msg)


    if 'before' not in _get_statistics:
        raise ValueError(err_msg)

    if 'after' not in _get_statistics:
        raise ValueError(err_msg)


    for _key in ['before', 'after']:
        if not isinstance(_get_statistics[_key], (type(None), bool)):
            raise TypeError(err_msg)




