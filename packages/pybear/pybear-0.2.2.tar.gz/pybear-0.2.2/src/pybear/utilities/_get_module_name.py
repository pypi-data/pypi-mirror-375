# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



import os
import sys


def get_module_name(sys_modules_string:str) -> str:
    """Retrieve the name of the calling module.

    Parameters
    ----------
    sys_modules_string : str
        Must be passed as 'str(sys.modules[__name__])' in the calling
        module.

    Returns
    -------
    module_name : str
        Name of the calling module.

    Examples
    --------
    >>> from pybear.utilities import get_module_name
    >>> import sys
    >>> print(sys.modules[__name__]) #doctest:+SKIP
    <module '__main__' from '...\\pybear\\utilities\\scratch.py'>

    >>> out = get_module_name(str(sys.modules[__name__]))
    >>> print(out) #doctest:+SKIP
    scratch

    """

    err_msg = (f"'sys_modules_string' must be a valid representation of "
               f"sys.modules[__name__]")

    if not isinstance(sys_modules_string, str):
        raise ValueError(err_msg)

    if str(os.sep) not in sys_modules_string or \
            '.py' not in sys_modules_string or \
            'module' not in sys_modules_string:
        raise ValueError(err_msg)

    del err_msg


    for n in range(len(sys_modules_string) - 1, -1, -1):
        if sys_modules_string[n - 1:n] == str(os.sep):
            return sys_modules_string[n:-5]






