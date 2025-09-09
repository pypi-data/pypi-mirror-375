# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numbers

import numpy as np

from pybear.utilities._union_find import union_find



class TestUnionFind:

    # must be an iterable of iterables. each inner iterable must be a pair.
    # "for x, y in pairs" will catch:
    # 'pairs' must be iterable
    # unpack must be 2 items at a time
    # the values that are unpacked must be:
    # hashable by a python dictionary -- would be caught by "parent[x] = x"
    # compatible with python "==" and "=!" operators, but this isnt validated


    @pytest.mark.parametrize('junk_uf',
        (-2.7, 1, 2.7, True, False, 'junk', [(0,)], [(1,2,3)], (3,), {6,7,8},
         {'a': 1}, lambda x: x)
    )
    def test_rejects_junk(self, junk_uf):

        # this is raised by python, let it raise whatever
        with pytest.raises(Exception):
            union_find(junk_uf)


    @pytest.mark.parametrize('container1', (list, tuple))
    @pytest.mark.parametrize('container2', (list, tuple))
    def test_accepts_good_and_accuracy(self, container1, container2):

        _base = ((0,1), (2,1), (3,4), (5,4))

        if container1 is np.ndarray:
            if container2 is np.ndarray:
                _wip = np.empty((len(_base),), dtype=object)
                for idx, thing in enumerate(_base):
                    _wip[idx] = np.array(list(thing))
            else:
                _wip = np.empty((len(_base),), dtype=object)
                for idx, thing in enumerate(_base):
                    _wip[idx] = container2(thing)
        else:
            _wip = container1(map(container2, _base))

        # v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v
        out = union_find(_wip)
        # ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^

        assert isinstance(out, tuple)
        for thing in out:
            assert isinstance(thing, tuple)
            assert all(map(isinstance, thing, (numbers.Integral for i in thing)))

        # the order of outputs is not controlled. need to look for where
        # things are, then make sure the right things are with each other.
        if 0 in out[0]:
            assert 1 in out[0]
            assert 2 in out[0]
        elif 0 in out[1]:
            assert 1 in out[1]
            assert 2 in out[1]

        if 3 in out[0]:
            assert 4 in out[0]
            assert 5 in out[0]
        if 3 in out[1]:
            assert 4 in out[1]
            assert 5 in out[1]





