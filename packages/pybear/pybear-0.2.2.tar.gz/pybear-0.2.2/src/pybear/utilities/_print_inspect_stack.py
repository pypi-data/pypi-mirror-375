# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



from typing import Callable



def print_inspect_stack(inspect_stack: Callable):
    """Print a module's stack hierarchy to screen.

    Pass inspect.stack (not inspect.stack()) to this in body of a
    function or module to print its stack hierarchy to screen.

    Parameters
    ----------
    inspect_stack:
        inspect.stack from the calling function / module.

    Returns
    -------
    None

    See Also
    --------
    inspect.stack

    """

    err_msg = f'can only pass inspect.stack ; do not pass inspect.stack()'
    if not callable(inspect_stack):
        raise TypeError(err_msg)

    if not 'function stack' in str(inspect_stack):
        raise TypeError(err_msg)

    del err_msg

    inspect_stack = inspect_stack()

    print(f'\ninspect.stack():')
    for _ in range(len(inspect_stack)):
        print(f'[{_}]')
        for __ in range(len(inspect_stack[_])):
            print(f' ' * 4 + f'[{__}] {str(inspect_stack[_][__])}')

    print()





