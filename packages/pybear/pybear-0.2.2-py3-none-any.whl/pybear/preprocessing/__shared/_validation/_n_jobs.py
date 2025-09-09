# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



def _val_n_jobs(
    _n_jobs: int | None
) -> None:
    """Validate `n_jobs` is None, -1, or integer >= 1.

    Parameters
    ----------
    _n_jobs : int | None
        The number of processors/threads to use for CPU bound tasks.

    Return
    ------
    None

    """


    err_msg = f"n_jobs must be None, -1, or an integer greater than 0"

    if _n_jobs is None:
        return

    try:
        float(_n_jobs)
        if isinstance(_n_jobs, bool):
            raise Exception
        if int(_n_jobs) != _n_jobs:
            raise Exception
    except Exception as e:
        raise TypeError(err_msg)

    if _n_jobs == -1 or _n_jobs >= 1:
        pass
    else:
        raise ValueError(err_msg)

    del err_msg




