# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
    Literal,
    Sequence,
    TypeAlias
)
import numpy.typing as npt

import numbers

import joblib
import numpy as np

from pybear.utilities._serial_index_mapper import serial_index_mapper as sim
from pybear.utilities._array_sparsity import array_sparsity as arsp



def choice(
    a: Sequence[Any],
    shape: int | Sequence[int],
    replace: bool=True,
    n_jobs: int | None = None
) -> npt.NDArray[Any]:
    """Randomly select elements from the given pool `a`, with or without
    replacement, to fill a numpy array of size `shape`.

    This module improves on the impossible slowness of numpy.random.choice
    on large `a` when `replace=False`. Enter `a` as a 1-dimensional
    vector. A 'p' argument is not available as this algorithm  relies on
    the assumption of equal likelihood for all values in `a`.

    Parameters
    ----------
    a : Sequence[Any]
        1-dimensional list-like of elements to randomly choose from.
    shape : int | Sequence[int]
        Shape of returned numpy array containing the randomly selected
        values.
    replace : bool
        Select values from `a` with (True) or without (False) replacement
        of previous pick.
    n_jobs : int | None, default=None
        Number of CPU cores used when parallelizing over subpartitions
        of `a` during selection. -1 means using all processors.

    Returns
    -------
    picked : numpy.ndarray[Any] of shape 'shape'
        Elements randomly selected from `a`.

    See Also
    --------
    numpy.random.choice

    Examples
    --------
    >>> from pybear.new_numpy.random import choice as pb_choice
    >>> result = pb_choice(list(range(20)), (3,2), n_jobs=1)
    >>> print(result) #doctest:+SKIP
    [[ 9  6]
     [ 2  0]
     [11  8]]

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # a ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    err_msg = (f"'a' must be a non-empty 1-dimensional array-like that "
               f"can be converted to a numpy array")

    try:
        list(a[:10])
        if isinstance(a, (str, dict)):
            raise Exception
        a = np.array(a)
        if len(a.shape) != 1:
            raise UnicodeError
        if len(a) == 0:
            raise UnicodeError
    except UnicodeError:
        raise ValueError(err_msg)
    except Exception as e:
        raise TypeError(err_msg)

    del err_msg
    # END a ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # shape ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    err_msg = f"'shape' must be an integer or a tuple of integers"
    # shape can be > 2 dimensional

    try:
        list(shape)
        shape = tuple(shape)
    except Exception as e:
        try:
            float(shape)
            if not int(shape) == shape:
                raise Exception
            shape = (int(shape),)
        except Exception as f:
            raise TypeError(err_msg)

    del err_msg
    # END shape ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # replace ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    if not isinstance(replace, bool):
        raise TypeError(f"'replace' kwarg must be boolean")

    if replace is False and np.prod(shape) > a.size:
        raise ValueError(
            f'quantity of selected cannot be greater than pool size when '
            f'`replace=False`'
        )
    # END replace ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # n_jobs ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    err_msg = f"n_jobs must be a positive integer, -1, or None, got '{n_jobs}'"
    try:
        if n_jobs is None:
            raise MemoryError
        float(n_jobs)
        if int(n_jobs) != n_jobs:
            raise UnicodeError
        n_jobs = int(n_jobs)
        if n_jobs < -1 or n_jobs == 0:
            raise UnicodeError
    except MemoryError:
        pass
    except UnicodeError:
        raise ValueError(err_msg)
    except Exception as e:
        raise TypeError(err_msg)

    del err_msg
    # END n_jobs ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    partition_size = min(a.size, int(2**16))

    psis = range(0, a.size, partition_size)  # partition_start_indices

    # parallelized function -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @joblib.wrap_non_picklable_objects
    def _puller(
        subpartition_of_a: npt.NDArray,
        _size: int,
        pick_qty: int,
        replace: bool
    ):
        """Parallelized random selector from subpartitions of `a`."""

        PULL: npt.NDArray = np.random.choice(
            subpartition_of_a,
            int(np.ceil(len(subpartition_of_a) / _size * pick_qty)),
            replace=replace
        )

        return PULL
    # END parallelized function -- -- -- -- -- -- -- -- -- -- -- -- --

    pick_qty = np.prod(shape)

    ARGS = [a.size, pick_qty, replace]

    # 'a' MUST BE 1-D
    with joblib.parallel_config(prefer='processes', n_jobs=n_jobs):
        PULLED = joblib.Parallel(return_as='list')(
            joblib.delayed(_puller)(a[psi:psi+partition_size], *ARGS) for psi in psis
        )

    picked = np.hstack((PULLED))

    del partition_size, psis, _puller, ARGS, PULLED


    if picked.size > pick_qty:
        picked = np.random.choice(picked, pick_qty, replace=False)
    elif picked.size < pick_qty:
        raise AssertionError(
            f"'picked' is smaller than pick_qty, algorithm failure"
        )

    return picked.reshape(shape)



EngineType: TypeAlias = \
    Literal["choice", "filter", "serialized", "iterative", "default"]


class Sparse:
    """Return random values from a “discrete uniform” (integer) or
    "uniform" (float) distribution of the specified dtype in the
    “half-open” interval [`minimum`, `maximum`) (includes low, but
    excludes the maximum), with desired sparsity.

    Samples are uniformly distributed over the interval. In other words,
    any value within the given interval is equally likely to be drawn.

    The sparse array is constructed at instantiation of the `Sparse`
    class, and is accessible via the `sparse_array_` attribute of the
    instance. This means that `Sparse` cannot generate arrays dynamically;
    one instance, one array. If you want to change any of the parameters
    of the instance to create a new array, you need to create a new
    instance.

    **Engine**

    `Sparse` has different engines for populating the output array with
    zeros to the desired sparsity. Some engines offer higher speed with
    lower accuracy, while others have higher accuracy at the expense of
    speed. "default" behavior is a hybrid of "filter" and "iterative".

    "choice"
        Build a full-size mask with sparse locations determined by
        numpy.random.choice on [0,1], with 'p' achieving amount of
        sparsity. Build a full-sized 100% dense numpy.ndarray filled as
        dictated by parameters then apply the mask to populate it with
        zeros.

    "filter"
        Generate an array filled randomly from [1,100000] and convert
        the array to a mask that fixes the sparse locations by applying
        a number filter derived from the target sparsity. Generate a
        100% dense array of integers or floats then apply the mask to
        it to achieve sparsity.

    "serialized"
        Generate a serialized list of unique indices and random values
        (or zeros) then map the values (or zeros) into a fully sparse
        (or dense) array.

        1. Determine the number of dense (or sparse) positions in
            the target array.

        2. Generate that number of random dense (or sparse) indices
            serially using pybear.new_numpy.random.choice *without
            replacement*. This guarantees no duplicate indices.

        3. Generate an equally-sized vector of dense values (or zeros).

        4. Map the vector of values (or zeros) to the index positions
            in a 100% sparse (or dense) full-sized array.

    "iterative"
        Generate a serialized list of not-necessarily-unique indices and
        random values (or zeros), then map the values (or zeros) into a
        fully sparse (or dense) array. Repeat iteratively until the
        desired sparsity is achieved. Same as 'serialized' except these
        indices are not necessarily unique and the process is iterative.

        1. Determine the number of dense (or sparse) positions in the
        target array.

        2. Generate that number of random dense (or sparse) indices
        serially *with replacement*; this does not guarantee
        non-duplicate indices.

        3. Generate an equally-sized vector of values (or zeros).

        4. Map the vector of values (or zeros) to the index positions
        in a 100% sparse (or dense) full-sized array.

        5. Because there may have been duplicate indices, repeat steps
        2-4 until desired sparsity is achieved.

    "default"
        A hybrid method of "filter" and "iterative" that maximizes speed
        and accuracy. When the size of the target object is less than
        1,000,000, the fastest methods "filter" and "choice" have
        difficulty achieving the target sparsity. In this case, the more
        accurate, but slower, "iterative" method is used. For target
        sizes over 1,000,000, the law of averages prevails and the
        "filter" method is able to achieve sufficiently close sparsities
        at speeds much faster than "iterative".

    Parameters
    ----------
    minimum : numbers.Real
        Lowest (signed) value to be drawn from the distribution.
    maximum : numbers.Real
        Upper boundary of the output interval. All values generated will
        be less than this number.
    shape : int | Sequence[int]
        Dimensions of the returned array.
    sparsity : numbers.Real, default = 0
        Desired percentage of zeros in the returned array.
    engine : EngineType, default = "default"
        Selects the desired engine for generating the returned array.
        See the 'Engine' section of the docs for a detailed explanation.
    dtype : object, default = float
        Desired dtype of the result.

    Attributes
    ----------
    sparse_array_ : numpy.ndarray[numbers.Real]
        ndarray of shape 'shape' with desired dtype and sparsity.

    See Also
    --------
    numpy.random.randint
    numpy.random.uniform

    Notes
    -----

    **Type Aliases**

    EngineType:
        Literal["choice", "filter", "serialized", "iterative", "default"]

    Examples
    --------
    >>> from pybear.new_numpy import random as pb_random
    >>> instance = pb_random.Sparse(0, 10, (3,3), 50, dtype=np.int8)
    >>> sparse_array = instance.sparse_array_
    >>> print(sparse_array) #doctest:+SKIP
    [[0 6 0]
     [8 8 0]
     [0 0 1]]

    """


    def __init__(
        self,
        minimum: numbers.Real,
        maximum: numbers.Real,
        shape: int | Sequence[int],
        sparsity: numbers.Real = 0,
        engine: EngineType = 'default',
        dtype: object = float,
    ):
        """Initialize the `Sparse` instance."""

        self._min = minimum
        self._max = maximum
        self._shape = shape
        self._sparsity = sparsity
        self._engine = engine
        self._dtype = dtype

        # VALIDATION ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # dtype ** * ** * ** * ** * ** * ** * ** *
        # THIS MUST BE BEFORE _min & _max
        if not isinstance(self._dtype, type(int)):
            raise TypeError(f'dtype must be a valid py or numpy dtype')
        # dtype ** * ** * ** * ** * ** * ** * ** *


        # _min ** * ** * ** * ** * ** * ** *
        try:
            float(self._min)
        except Exception as e:
            raise TypeError(f"'minimum' must be numeric")

        if 'INT' in str(self._dtype).upper():
            if int(self._min) != self._min:
                raise ValueError(
                    f"'minimum' must be an integer when dtype is integer"
                )
        elif 'FLOAT' in str(self._dtype).upper():
            if self._min == float('inf') or self._min == float('-inf'):
                raise ValueError(f"'minimum' cannot be infinity")
        # END _min ** * ** * ** * ** * ** * ** *

        # _max ** * ** * ** * ** * ** * ** *
        try:
            float(self._max)
        except:
            raise TypeError(f"'maximum' must be numeric")

        if 'INT' in str(self._dtype).upper():
            if int(self._max) != self._max:
                raise ValueError(
                    f"'maximum' must be an integer when dtype is integer"
                )
        elif 'FLOAT' in str(self._dtype).upper():
            if self._max == float('inf') or self._max == float('-inf'):
                raise ValueError(f"'maximum' cannot be infinity")
        # END _max ** * ** * ** * ** * ** * ** *

        # _min v _max ** * ** * ** * ** * ** * ** *
        if 'INT' in str(self._dtype).upper():
            if self._min >= self._max:
                raise ValueError(f"when dtype is integer, 'minimum' must be "
                    f"<= ('maximum' - 1)")
        elif 'FLOAT' in str(self._dtype).upper():
            if self._min > self._max:
                self._min, self._max = self._max, self._min
        # END _min v _max ** * ** * ** * ** * ** * ** *


        # shape ** * ** * ** * ** * ** * ** * ** *

        err_msg = f"'shape' expected a sequence of integers or a single integer"

        try:
            if isinstance(self._shape, type(None)):
                raise MemoryError
            float(self._shape)
            self._shape = (self._shape, )
        except MemoryError:
            self._shape = ()
        except Exception as e:
            try:
                list(self._shape)
                if isinstance(self._shape, (str, dict)):
                    raise Exception
            except Exception as f:
                raise TypeError(f"{err_msg}, got type '{type(self._shape)}'")

        # self._shape must be an iterable

        if len(np.array(list(self._shape)).shape) > 1:
            raise TypeError(err_msg)

        self._shape = tuple(self._shape)

        if any(map(lambda x: x < 0, self._shape)):
            raise ValueError(f"negative dimensions are not allowed")

        if not all(map(
            isinstance, self._shape, (numbers.Integral for i in self._shape)
        )):
            raise TypeError(err_msg)

        # END shape ** * ** * ** * ** * ** * ** * ** *


        # sparsity ** * ** * ** * ** * ** * ** * ** *
        err_msg = f"sparsity must be a number between 0 and 100, inclusive"
        try:
            float(self._sparsity)
        except:
            raise TypeError(err_msg)

        if self._sparsity < 0 or self._sparsity > 100:
            raise ValueError(err_msg)

        if 'INT' in str(self._dtype).upper():
            if self._min==0 and self._max==1 and self._sparsity != 100:
                raise ValueError(f"cannot satisfy the impossible condition of "
                    f"'minimum' = 0 'maximum' = 1 and 'sparsity' != 100 for "
                    f"integer dtype")
        elif 'FLOAT' in str(self._dtype).upper():
            if self._min==0 and self._max==0 and self._sparsity != 100:
                raise ValueError(f"cannot satisfy the impossible condition of "
                    f"'minimum' = 0 'maximum' = 0 and 'sparsity' != 100 for "
                    f"float dtype")

        del err_msg
        # END sparsity ** * ** * ** * ** * ** * ** * **


        # engine ** * ** * ** * ** * ** * ** * ** * ** * **

        allowed = ['choice', 'filter', 'serialized', 'iterative', 'default']
        err_msg = (f"'engine' must be {', '.join(allowed)}")

        if not isinstance(self._engine, str):
            raise TypeError(err_msg)

        self._engine = self._engine.lower()

        if self._engine not in allowed:
            raise ValueError(
                f"'{self._engine}' is not in allowed, must be "
                f"{', '.join(map(str, allowed))}"
            )
        del allowed

        # END engine ** * ** * ** * ** * ** * ** * ** * ** *

        # END VALIDATION ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        if 0 in self._shape:
            self.sparse_array_ = \
                np.array([], dtype=self._dtype).reshape(self._shape)

        if self._sparsity == 0:
            self.sparse_array_ = self._make_base_array_with_no_zeros(
                self._min,
                self._max,
                self._shape,
                self._dtype
            ).astype(self._dtype)

        if self._sparsity == 100:
            self.sparse_array_ = np.zeros(self._shape, dtype=self._dtype)

        if self._engine == "choice":
            self.sparse_array_ = self._choice()

        elif self._engine == "filter":
            self.sparse_array_ = self._filter()

        elif self._engine == "serialized":
            self.sparse_array_ = self._serialized()

        elif self._engine == "iterative":
            self.sparse_array_ = self._iterative()

        elif self._engine == "default":

            # IF total_size IS ABOVE 1e6, MAKE BY FILTER METHOD, IS MUCH FASTER
            # THAN SERIALIZED OR ITERATIVE AND LAW OF AVERAGES SHOULD GET
            # SPARSITY CLOSE ENOUGH. BUT WHEN SIZE IS SMALL, "FILTER" AND
            # "CHOICE" HAVE A HARD TIME GETTING SPARSITY CLOSE ENOUGH, SO USE
            # ITERATIVE.
            if np.prod(self._shape) >= 1e6:
                self.sparse_array_ = self._filter()
            else:
                self.sparse_array_ = self._iterative()
        else:
            raise AssertionError(f"logic managing engine selection failed")


    def _make_base_array_with_no_zeros(
        self, _min, _max, _shape, _dtype
    ) -> npt.NDArray[numbers.Real]:
        """Generate an array based on the given minimum, maximum, shape,
        and dtype rules, and iteratively replace any zeros with non-zero
        values generated by the same rules.

        Parameters
        ----------
        _min : int
            The low end of the range of random numbers in the fully-dense
            base array.
        _max : int
            The high end of the range of random numbers in the fully-dense
            base array.
        _shape : tuple[int]
            The shape of the final sparse array.
        _dtype : object
            The dtype of the final sparse array.

        Returns
        -------
        BASE_ARRAY: npt.NDArray[numbers.Real]
            Fully dense numpy ndarray with minimum, maximum, shape, and
            dtype as specified.

        """

        # Set the numpy array generators to be used based on dtype. *********
        if 'INT' in str(self._dtype).upper():
            array_generator = np.random.randint
        elif 'FLOAT' in str(self._dtype).upper():
            # CREATE A WRAPPER FOR np.random.uniform SO THAT IT'S SIGNATURE IS
            # THE SAME AS np.random.randint. dtype WILL JUST PASS THROUGH.
            def new_rand_uniform(_min, _max, _shape, _dtype):
                return np.random.uniform(_min, _max, _shape)

            array_generator = new_rand_uniform
        else:
            raise Exception
        # END Set the numpy array generators to be used based on dtype. ******

        BASE_ARRAY = array_generator(_min, _max, _shape, _dtype)
        # DONT LOOP THE ZEROES OUT OF BASE_ARRAY "NON_ZERO_VALUES"!
        # LOOP THEM OUT OF THE PATCH!
        if 0 in BASE_ARRAY:
            MASK = (BASE_ARRAY == 0)
            PATCH = array_generator(_min, _max, np.sum(MASK), _dtype)

            while 0 in PATCH:
                PATCH_MASK = (PATCH == 0)
                PATCH[PATCH_MASK] = \
                    array_generator(_min, _max, np.sum(PATCH_MASK), _dtype)
                del PATCH_MASK

            BASE_ARRAY[MASK] = PATCH

            del MASK, PATCH

        return BASE_ARRAY


    def _calc_support_info(self):
        """Calculate supporting info for performing operations."""

        if len(self._shape)==0:
            self._total_size = 0
        else:
            self._total_size = np.prod(self._shape).astype(np.int32)

        self._dense_size = self._total_size / 100 * (100 - self._sparsity)

        # IF SPARSITY DOESNT GO EVENLY INTO NUM ELEMENTS (I.E. _dense_size
        # IS NOT AN INTEGER), ROUND OFF _dense_size
        if self._dense_size % 1 > 0:
            self._dense_size = int(round(self._dense_size, 0))
        else:
            self._dense_size = int(self._dense_size)

        self._sparse_size = int(self._total_size - self._dense_size)

        try:
            self._target_sparsity = \
                round(100 * self._sparse_size / self._total_size, 12)
        except:
            self._target_sparsity = self._sparsity


    def _choice(self):
        """Apply a mask of bools generated by random.choice to a 100%
        dense array to achieve sparsity.

        Returns
        -------
        SPARSE_ARRAY : npt.NDArray[numbers.Real]
            Sparse array of specified minimum & maximum (excluding zeros),
            shape and dtype, made by applying a random.choice binary mask
            to a fully dense array.

        """

        ################################################################
        # "choice" - BUILD A FULL-SIZED MASK WITH SPARSE LOCATIONS
        # DETERMINED BY random.choice ON [0,1], WITH p ACHIEVING AMOUNT
        # OF SPARSITY. APPLY MASK TO A FULL SIZED 100% DENSE NP ARRAY
        # FILLED AS DICTATED BY PARAMETERS.
        ################################################################

        # REMEMBER! THE MASK IS GOING TO BE A BOOL TO REPRESENT PLACES
        # IN THE BASE ARRAY THAT WILL GO TO ZERO!  THAT MEANS THAT THE
        # PLACES THAT WILL BE ZERO MUST BE A ONE IN THE MASK, AND ZERO
        # IF NOT GOING TO BE ZERO! MAKE SENSE?
        MASK = np.random.choice(
            [1, 0], self._shape, replace=True,
            p=(self._sparsity / 100, (100 - self._sparsity) / 100)
        ).astype(bool)

        SPARSE_ARRAY = self._make_base_array_with_no_zeros(
            self._min, self._max, self._shape, self._dtype
        )

        SPARSE_ARRAY[MASK] = 0
        del MASK

        return SPARSE_ARRAY.astype(self._dtype)


    def _filter(self):
        """Generate an array filled randomly from [1,100000] and turn it
        into a mask by applying a number filter; generate a 100% dense
        array of ints or floats then apply the mask to it to achieve
        sparsity.

        Returns
        -------
        SPARSE_ARRAY : npt.NDArray[numbers.Real]
            Sparse array of specified minimum & maximum (excluding zeros),
            shape and dtype, made by applying a number filter mask to a
            fully dense array.

        """

        ################################################################
        # "filter" - BUILD A FULL-SIZED ARRAY FILLED RANDOMLY ON RANGE
        # [0-100000]. CONVERT THE ARRAY TO A MASK THAT FIXES THE SPARSE
        # LOCATIONS BY APPLYING A NUMBER FILTER DERIVED FROM THE TARGET
        # SPARSITY. APPLY THE MASK OVER A FULL SIZED 100% DENSE NP ARRAY.
        ################################################################

        # USE THIS TO DETERMINE WHAT WILL BECOME ZEROS
        MASK = np.random.randint(0, 100000, self._shape, dtype=np.int32)
        MASK = (MASK >= (1 - self._sparsity / 100) * 100000).astype(bool)

        SPARSE_ARRAY = self._make_base_array_with_no_zeros(
            self._min, self._max, self._shape, self._dtype
        )
        SPARSE_ARRAY[MASK] = 0

        del MASK

        return SPARSE_ARRAY.astype(self._dtype)


    def _serialized(self):
        """Generate a serialized list of unique indices and random values
        (or zeros) then map the values (or zeros) into a fully sparse
        (or dense) array.

        Returns
        -------
        SPARSE_ARRAY : npt.NDArray[numbers.Real]
            Sparse array of specified minimum & maximum (excluding zeros),
            shape and dtype, made by building a vector of positions that
            identify dense or sparse locations in the final array.

        """

        ################################################################
        # "serialized"
        # i) DETERMINE THE NUMBER OF DENSE (OR SPARSE) POSITIONS IN THE ARRAY.
        # ii) GENERATE THAT NUMBER OF RANDOM DENSE (OR SPARSE) INDICES
        # SERIALLY USING random.choice *WITHOUT REPLACEMENT*. THIS GUARANTEES
        # NO DUPLICATE INDICES.
        # iii) GENERATE AN EQUALLY-SIZED VECTOR OF DENSE VALUES (OR ZEROS).
        # iv) MAP THE VECTOR OF VALUES (OR ZEROS) TO THE INDEX POSITIONS IN A
        # 100% SPARSE (OR DENSE) FULL SIZED ARRAY
        ################################################################

        self._calc_support_info()

        # ALLOW pybear.new_numpy.random.choice TO SELECT FROM THE SMALLER OF
        # dense_size OR sparse_size, SAVES MEMORY & TIME

        # WHEN DENSE IS SMALLER OR _sparse_size == 0
        if self._dense_size == 0 and self._sparse_size == 0:
            return self._filter()

        elif (self._sparse_size >= self._dense_size > 0) \
            or self._sparse_size == 0:

            SERIAL_DENSE_POSNS = choice(
                range(self._total_size),
                self._dense_size,
                replace=False,
                n_jobs=-1
            ).astype(np.int32)

            SERIAL_DENSE_POSNS.sort()

            # CREATE RANDOM VALUES MATCHING THE DENSE SIZE
            SERIAL_VALUES = self._make_base_array_with_no_zeros(
                self._min, self._max, self._dense_size, self._dtype
            )

            SPARSE_ARRAY = np.zeros(self._shape, dtype=self._dtype)

            MAPPED_INDICES = sim(self._shape, SERIAL_DENSE_POSNS)

            SPARSE_ARRAY[tuple(zip(*MAPPED_INDICES))] = SERIAL_VALUES

            del SERIAL_DENSE_POSNS, SERIAL_VALUES, MAPPED_INDICES

            return SPARSE_ARRAY.astype(self._dtype)


        # WHEN SPARSE IS SMALLER OR _dense_size == 0
        elif (0 < self._sparse_size < self._dense_size) or self._dense_size == 0:

            if self._sparse_size:
                SERIAL_SPARSE_POSNS = choice(
                    range(self._total_size),
                    self._sparse_size,
                    replace=False,
                    n_jobs=-1
                ).astype(np.int32)

            SERIAL_SPARSE_POSNS.sort()

            SPARSE_ARRAY = self._make_base_array_with_no_zeros(
                self._min,
                self._max,
                self._shape,
                self._dtype
            )

            MAPPED_INDICES = sim(self._shape, SERIAL_SPARSE_POSNS)

            SPARSE_ARRAY[tuple(zip(*MAPPED_INDICES))] = 0

            del SERIAL_SPARSE_POSNS, MAPPED_INDICES

            return SPARSE_ARRAY.astype(self._dtype)


    def _iterative(self):
        """Generate a serialized list of not-necessarily-unique indices
        and random values (or zeros) then map the values (or zeros) into
        a fully sparse (or dense) array, and repeat iteratively until the
        desired sparsity is achieved.

        Same as _serialized except these indices are not necessarily
        unique and the process is iterative.

        Returns
        -------
        SPARSE_ARRAY : npt.NDArray[numbers.Real]
            Sparse array of specified minimum & maximum (excluding zeros),
            shape and dtype, made by building a vector of positions that
            identify dense or sparse locations in the final array.

        """

        ###############################################################
        # "iterative"
        # i) DETERMINE THE NUMBER OF DENSE (OR SPARSE) POSITIONS IN THE ARRAY.
        # ii) GENERATE THAT NUMBER OF RANDOM DENSE (OR SPARSE) INDICES SERIALLY
        # *WITH REPLACEMENT*. THIS DOES NOT GUARANTEE NON-DUPLICATE INDICES.
        # iii) GENERATE AN EQUALLY-SIZED VECTOR OF VALUES (OR ZEROS).
        # iv) MAP THE VECTOR OF VALUES (OR ZEROS) TO THE INDEX POSITIONS IN A
        # 100% SPARSE (OR DENSE) FULL SIZED ARRAY
        # v) BECAUSE THERE MAY HAVE BEEN DUPLICATE INDICES, REPEAT STEPS
        # ii - iv UNTIL DESIRED SPARSITY IS ACHIEVED
        ################################################################

        self._calc_support_info()

        # ALLOW pybear.new_numpy.random.choice TO SELECT FROM THE SMALLER
        # OF dense_size OR sparse_size, SAVES MEMORY & TIME

        if self._dense_size == 0 and self._sparse_size == 0:

            return self._filter()

        elif self._sparse_size >= self._dense_size:  # WHEN DENSE IS SMALLER

            SPARSE_ARRAY = np.zeros(self._shape, dtype=self._dtype)

            _last_sparsity = 100

            # MAKE A RANDOM GRID OF COORDINATES
            while _last_sparsity != self._target_sparsity:
                need_dense_size = np.sum(SPARSE_ARRAY == 0) - self._sparse_size
                SERIAL_DENSE_POSNS = np.empty(
                    (need_dense_size, len(self._shape)),
                    dtype=np.int32
                )
                for _dim in range(len(self._shape)):
                    SERIAL_DENSE_POSNS[:, _dim] = \
                         np.random.randint(
                            0,
                            self._shape[_dim],
                            need_dense_size,
                            dtype=np.int32
                    )

                # CREATE RANDOM VALUES MATCHING THE DENSE SIZE
                SERIAL_VALUES = self._make_base_array_with_no_zeros(
                    self._min,
                    self._max,
                    need_dense_size,
                    self._dtype
                )

                SPARSE_ARRAY[tuple(zip(*SERIAL_DENSE_POSNS))] = SERIAL_VALUES

                _new_sparsity = round(arsp(SPARSE_ARRAY), 12)
                if _new_sparsity == self._target_sparsity:
                    break
                else:
                    _last_sparsity = _new_sparsity

            return SPARSE_ARRAY.astype(self._dtype)

        elif self._sparse_size < self._dense_size:  # WHEN SPARSE IS SMALLER

            SPARSE_ARRAY = self._make_base_array_with_no_zeros(
                self._min, self._max, self._shape, self._dtype
            )

            _last_sparsity = 0

            # MAKE A RANDOM GRID OF COORDINATES
            while _last_sparsity != self._target_sparsity:
                need_sparse_size = self._sparse_size - np.sum(SPARSE_ARRAY == 0)
                SERIAL_SPARSE_POSNS = np.empty(
                    (need_sparse_size, len(self._shape)),
                    dtype=np.int32
                )
                for _dim in range(len(self._shape)):
                    SERIAL_SPARSE_POSNS[:, _dim] = \
                        np.random.randint(0,
                            self._shape[_dim],
                            need_sparse_size,
                            dtype=np.int32
                    )

                SPARSE_ARRAY[tuple(zip(*SERIAL_SPARSE_POSNS))] = 0

                _new_sparsity = round(arsp(SPARSE_ARRAY), 12)
                if _new_sparsity == self._target_sparsity:
                    break
                else:
                    _last_sparsity = _new_sparsity

            return SPARSE_ARRAY.astype(self._dtype)


def sparse(
    minimum: numbers.Real,
    maximum: numbers.Real,
    shape: int | Sequence[int],
    sparsity: numbers.Real,
    dtype: object = np.float64
):
    """Return random values from a “discrete uniform” (integer) or
    "uniform" (float) distribution of the specified dtype in the
    “half-open” interval [`minimum`, `maximum`) (includes low, but
    excludes the maximum), with desired sparsity.

    Samples are uniformly distributed over the interval. In other words,
    any value within the given interval is equally likely to be drawn.

    This function is a simplified :class:`Sparse` implementation.

    Parameters
    ----------
    minimum : numbers.Real
        Lowest (signed) value to be drawn from the distribution.
    maximum : numbers.Real
        Upper boundary of the output interval. All values generated will
        be less than this number.
    shape : int | Sequence[int]
        Dimensions of the returned array.
    sparsity : numbers.Real, default = 0
        Desired percentage of zeros in the returned array.
    dtype : object, default = float
        Desired dtype of the result.

    Returns
    -------
    sparse_array : numpy.ndarray[numbers.Real]
        Array of dimension `shape` with random values from the
        appropriate distribution and with the specified sparsity.

    See Also
    --------
    numpy.random.randint
    numpy.random.uniform
    pybear.random.Sparse

    Examples
    --------
    >>> from pybear.new_numpy.random import sparse as pb_sparse
    >>> sparse_array = pb_sparse(11, 20, (4,4), 70, dtype=np.int8)
    >>> print(sparse_array)   #doctest:+SKIP
    [12  0  0 13]
    [0 16  0  0]
    [0  0  0 17]
    [0  0  0 16]]

    """

    return Sparse(
        minimum, maximum, shape, sparsity, "default", dtype
    ).sparse_array_






