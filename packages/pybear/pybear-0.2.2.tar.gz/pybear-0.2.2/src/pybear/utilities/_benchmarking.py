# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



from typing import Callable
import numpy.typing as npt

from functools import wraps
import numbers
import os
import time

import numpy as np
import psutil



def timer(orig_func) -> Callable:
    """Wraps a function with a timer that displays the time in seconds
    it took for the function to run.

    Parameters
    ----------
    orig_func : Callable
        Function to be timed when called.

    Returns
    -------
    wrapper : Callable
        Wrapped original function.

    Examples
    --------
    >>> from pybear.utilities import timer
    >>>
    >>> @timer
    ... def my_function(x):
    ...     time.sleep(x)
    ...     return x
    ...
    >>> my_function(1.28)
    my_function ran in 1.28 sec
    1.28

    """

    @wraps(orig_func)
    def wrapper(*args, **kwargs):
        """Wrap the decorated function with a timer.

        Parameters
        ----------
        *args:
            The positional arguments for the wrapped function.
        **kwargs:
            The keyword arguments for the wrapped function.

        """

        t1 = time.time()
        result = orig_func(*args, **kwargs)
        t2 = time.time() - t1
        print(f'{orig_func.__name__} ran in {t2:,.3g} sec')
        return result

    return wrapper


def time_memory_benchmark(
    *args,
    number_of_trials:int = 7,
    rest_time:numbers.Real = 1,
    verbose:numbers.Real = 1
) -> npt.NDArray:
    """Measure the average time (seconds) and the average change in system
    RAM (MB) when computing functions.

    Displays statistics to the screen and returns an np.ndarray containing
    the raw measurements.

    Parameters
    ----------
    *args
        Tuples of ('function_name', function, ARGS_AS_LIST, KWARGS_AS_DICT).
    number_of_trials : int
        Number of times to run each given function. Given, for example,
        two trials with functions f1, f2, and f3, runs are ordered as f1,
        f2, f3, f1, f2, f3, not f1, f1, f2, f2, f3, f3.
    rest_time : numbers.Real
        Time to rest in seconds before and after running a function to
        allow for RAM equilibration. The rest time is not included in
        the reported computation time.
    verbose : numbers.Real
        Print (verbose > 0) or do not print (verbose=0) information to
        the screen during run time.

    Returns
    -------
    TIME_MEM_HOLDER : ndarray of shape (2, n_functions, n_trials)
        Raw measurements of time (sec) and memory change (MB). Index 0
        of the first axis contains time results, index 1 contains memory
        results.

    Examples
    --------
    >>> from pybear.utilities import time_memory_benchmark
    >>> def function_a(a, b, c=1):
    ...     time.sleep(a + b + c)
    ...     return a + b + c
    ...
    >>> def function_b(d, e, f=2):
    ...     time.sleep(d + e + f)
    ...     return d + e + f
    ...
    >>> results = time_memory_benchmark(
    ...     ('function_a', function_a, [1, 2], {'c': 3}),
    ...     ('function_b', function_b, [0, 3], {'f': 1}),
    ...     number_of_trials=2,
    ...     rest_time=1,
    ...     verbose=1
    ... ) #doctest:+SKIP
    ********************************************************************
    Running trial 1...
         function_a...
         function_b...
    ********************************************************************
    Running trial 2...
         function_a...
         function_b...

    Done.

    function_a     time = 6.005 +/- 0.000 sec; mem = 0.000 +/- 0.000 MB

    function_b     time = 4.004 +/- 0.002 sec; mem = 0.000 +/- 0.000 MB

    >>> print(results) #doctest:+SKIP

    [[[6.0045845 6.005382300000001]
      [4.0055356 4.0022901]]

     [[0.0 0.0]
      [0.0 0.0]]]

    """


    # validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    if len(args)==0:
        raise ValueError(f"must pass at least one tuple of values")


    for arg in args:
        if len(arg) != 4:
            raise ValueError(
                f"Enter args as tuples of ('function_name', function, "
                f"ARGS_AS_LIST, KWARGS_AS_DICT)."
            )

        if not isinstance(arg[0], str):
            raise TypeError(
                f"first position in tuple must be function name as a string"
            )
        if not callable(arg[1]):
            raise TypeError(f"second position in tuple must be a callable")
        if isinstance(arg[2], (str, dict)):
            raise TypeError(
                f"third position in tuple must be a list-type of arguments "
                f"for the function"
            )
        try:
            list(arg[2])
        except:
            raise TypeError(
                f"third position in tuple must be a list-type of arguments "
                f"for the function"
            )
        if not isinstance(arg[3], dict):
            raise TypeError(
                f"fourth position in tuple must be a dictionary of keyword "
                f"arguments for the function"
            )

    try:
        float(number_of_trials)
        if int(number_of_trials) != number_of_trials or number_of_trials < 1:
            raise Exception
    except:
        raise ValueError(f"number_of_trials must be an integer >= 1")

    try:
        float(rest_time)
        if rest_time < 0:
            raise Exception
    except:
        raise ValueError(f"rest_time must be a number >= 0")


    try:
        float(verbose)
        if verbose < 0:
            raise Exception
    except:
        raise ValueError(f"verbose must be a number >= 0")

    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    ###### CORE MEASUREMENT FUNCTIONS ##################################
    def timer(user_fxn) -> Callable:
        """Decorator for the user function."""

        def wrapped1(ARGS, KWARGS):
            time.sleep(rest_time)                       # EQUILIBRATE MEMORY
            t0 = time.perf_counter()                    # GET START TIME
            FUNCTION_OUTPUT = user_fxn(ARGS, KWARGS)    # RUN FUNCTION
            _time = (time.perf_counter() - t0)          # GET DELTA TIME
            del t0
            return FUNCTION_OUTPUT, _time

        return wrapped1


    def mem(timer_fxn) -> Callable:
        """Decorator for the user function."""

        def wrapped2(ARGS, KWARGS):
            # GET START MEM
            mem0 = int(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
            # RUN time() FXN
            FUNCTION_OUTPUT, _time = timer_fxn(ARGS, KWARGS)
            # EQUILIBRATE MEMORY
            time.sleep(rest_time)
            # GET FINAL MEMORY
            _mem = int(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2) - mem0
            # CLEAR MEMORY OF PRODUCED OBJECTS
            del FUNCTION_OUTPUT

            return _time, _mem

        return wrapped2
    ###### END CORE MEASUREMENT FUNCTIONS ##############################


    # TIME_MEM_HOLDER SHAPE:
    # axis_0 = time, mem;
    # axis_1 = number_of_functions;
    # axis_2 = number_of_trials
    TIME_MEM_HOLDER = np.ma.empty((2, len(args), number_of_trials), dtype=np.float64)
    TIME_MEM_HOLDER.mask = True


    for trial in range(number_of_trials):

        if verbose:
            print(f'\n' + f'*'*80)
            print(f'Running trial {trial + 1}...')

        for fxn_num, (fxn_name, user_fxn, ARGS, KWARGS) in enumerate(args):

            @mem
            @timer
            def fxn_obj1(ARGS, KWARGS):
                return user_fxn(*ARGS, **KWARGS)

            if verbose:
                print(5*f' ' + f'{fxn_name}...')

            _time, _mem = fxn_obj1(ARGS, KWARGS)

            TIME_MEM_HOLDER[0, fxn_num, trial] = _time
            TIME_MEM_HOLDER[1, fxn_num, trial] = _mem


    if verbose:
        print(f'\nDone.\n')



    if number_of_trials >= 4:

        TIME_MEM_HOLDER.sort(axis=2)

        TIME_MEM_HOLDER[:, :, :int(np.ceil(0.1 * number_of_trials))] = \
            np.ma.masked
        TIME_MEM_HOLDER[:, :, int(np.floor(0.9 * number_of_trials)):] = np.ma.masked


    if verbose:

        names = list(zip(*args))[0]
        pad = min(max(map(len, names)) + 5, 50)

        for idx, name in enumerate(names):

            print(f'{name[:45]}'.ljust(pad) +
                  f'time = {TIME_MEM_HOLDER[0,idx,:].mean():,.3f} +/- '
                  f'{TIME_MEM_HOLDER[0,idx,:].std():,.3f} sec; '
                  f'mem = {TIME_MEM_HOLDER[1,idx,:].mean():,.3f} +/- '
                  f'{TIME_MEM_HOLDER[1,idx,:].std():,.3f} MB'
            )

        del names, pad


    return TIME_MEM_HOLDER
    # TIME_MEM_HOLDER SHAPE:
    # axis_0 = time, mem
    # axis_1 = number_of_functions
    # axis_2 = number_of_trials



