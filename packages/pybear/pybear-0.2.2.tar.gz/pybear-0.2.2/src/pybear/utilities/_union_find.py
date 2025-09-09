# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
    Sequence
)

from collections import defaultdict



def union_find(
    pairs: Sequence[Sequence[Any]]
) -> tuple[tuple[Any, Any], ...]:
    """Use the union-find algorithm to find groups of connected values
    from disjoint pairs of connected values.

    Requires an sequence list-like container holding sequence list-like
    pairs of values. The contents of the pairs are not validated, but
    must be hashable by a Python dictionary and must be compatible with
    Python '==' and '!=' operators. Python lists and tuples are tested
    and recommended, though other list-like containers such as sets and
    numpy arrays are likely to work. The output is not sorted in any way;
    any sorting needs to be done external to `union_find`.

    Parameters
    ----------
    pairs : Sequence[Sequence[Any]]
        Disjoint pairs of connected values.

    Returns
    -------
    _connected : tuple[tuple[Any, ...], ...]
        The unions of the disjoint pairs of connected values into groups
        of mutually connected values.

    Examples
    --------
    >>> from pybear.utilities import union_find
    >>> pairs = [(0, 4), (7, 3), (5, 9), (5, 4), (3, 8)]
    >>> out = union_find(pairs)
    >>> print(out)
    ((0, 4, 5, 9), (7, 3, 8))

    """


    # Find connected components using union-find

    parent = {}


    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])  # Path compression
        return parent[x]


    def union(x, y):
        root_x = find(x)
        root_y = find(y)
        if root_x != root_y:
            parent[root_y] = root_x


    # Initialize Union-Find
    for x, y in pairs:
        if x not in parent:
            parent[x] = x
        if y not in parent:
            parent[y] = y
        union(x, y)

    # Group elements by their root
    components = defaultdict(list)
    for node in parent:
        root = find(node)
        components[root].append(node)

    _connected = tuple(map(tuple, components.values()))


    return _connected




