# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



from typing import (
    Any,
    Sequence
)

import numpy as np



def permuter(vector_of_vectors: Sequence[Sequence[Any]]) -> list[list[int]]:
    """Find all possible unique combinations in drawing a single value
    from each group in a collection of groups of unique values.

    Given a vector of length n that contains n vectors of unique
    values with lengths (l1, l2,...ln), and whose total possible number
    of unique combinations is pn, generate an array of shape (pn, n)
    that contains in its rows the index positions given by permuting
    through all possible unique combinations of values when drawing a
    single value from each of those vectors.

    Parameters
    ----------
    vector_of_vectors : Sequence[Sequence[Any]]
        Vector of vectors of non-zero length

    Returns
    -------
    permutations : list of shape (n_combinations, n_vectors)
        An array that contains in its rows the index positions of all
        possible unique combinations of values in drawing a single value
        from each group in a collection of groups of unique values.

    See Also
    --------
    itertools.product
        for another implementation that returns values instead of indices.

    Examples
    --------
    >>> from pybear.utilities import permuter
    >>> vector1 = ['a', 'b', 'c']
    >>> vector2 = ['w', 'x']
    >>> vector3 = ['y', 'z']
    >>> vector_of_vectors = [vector1, vector2, vector3]
    >>> for _tuple in permuter(vector_of_vectors):
    ...     print(_tuple)
    (0, 0, 0)
    (0, 0, 1)
    (0, 1, 0)
    (0, 1, 1)
    (1, 0, 0)
    (1, 0, 1)
    (1, 1, 0)
    (1, 1, 1)
    (2, 0, 0)
    (2, 0, 1)
    (2, 1, 0)
    (2, 1, 1)

    """


    cp_vector_of_lens = np.array(list(map(len, vector_of_vectors)))

    if (cp_vector_of_lens <= 0).any():
        raise ValueError(f"vector_of_vectors cannot contain any empty vectors")
        
    
    def recursive_fxn(cp_vector_of_lens):
        if len(cp_vector_of_lens)==1:
            seed_array = np.zeros(
                (cp_vector_of_lens[0], len(vector_of_vectors)),
                dtype=int
            )
            seed_array[:, -1] = range(cp_vector_of_lens[0])
            return seed_array
        else:
            seed_array = recursive_fxn(cp_vector_of_lens[1:])
            stack = np.empty((0, len(vector_of_vectors)), dtype=np.uint32)
            for param_idx in range(cp_vector_of_lens[0]):
                filled_array = seed_array.copy()
                col_idx = len(vector_of_vectors) - len(cp_vector_of_lens)
                filled_array[:, col_idx] = param_idx
                del col_idx
                stack = np.vstack((stack, filled_array))
    
            del filled_array
            return stack

    permutations = list(map(tuple, recursive_fxn(cp_vector_of_lens).tolist()))

    del cp_vector_of_lens, recursive_fxn
        
    return permutations






