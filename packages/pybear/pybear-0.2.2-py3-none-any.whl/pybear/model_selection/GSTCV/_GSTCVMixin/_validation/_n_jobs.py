# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



def _val_n_jobs(
    _n_jobs: int | None
) -> None:
    """Validate that `n_jobs` is None or an integer >= -1 and not 0.

    Parameters
    ----------
    _n_jobs : int | None
        The number of joblib Parallel jobs to use. The default is to use
        processes, but can be overridden externally using a joblib
        parallel_config context manager. The default setting is None,
        which uses the joblib default.

    Returns
    -------
    None

    """


    if _n_jobs is None:
        return


    _err_msg = f"'n_jobs' must be None, -1, or an integer greater than 0"

    try:
        float(_n_jobs)
        if isinstance(_n_jobs, bool):
            raise Exception
        if int(_n_jobs) != _n_jobs:
            raise UnicodeError
        if _n_jobs < -1 or _n_jobs == 0:
            raise UnicodeError
    except UnicodeError:
        raise ValueError(_err_msg)
    except Exception as e:
        raise TypeError(_err_msg)


    del _err_msg

    return






