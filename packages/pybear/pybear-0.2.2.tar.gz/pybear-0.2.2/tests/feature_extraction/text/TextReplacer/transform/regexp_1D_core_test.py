# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.feature_extraction.text._TextReplacer._transform._regexp_1D_core \
    import _regexp_1D_core



class TestRegExp1DCore:


    # this module can only take re.compile as the search!


    @pytest.mark.parametrize('junk_X',
        (-2.7, -1, 0, 1, 2.7, True, None, 'junk', [0,1], (1,), {1,2}, {'A':1},
         set(list('abcde')), tuple(list('abcde')), lambda x: x)
    )
    def test_blocks_junk_X(self, junk_X):

        with pytest.raises(AssertionError):
            _regexp_1D_core(
                junk_X,
                [((re.compile('a'), ''),), ((re.compile('b'), 'B'),)]
            )


    # there is currently no other validation for this on rr
    # rr is validated on the way out of _special_param_conditioner


    def test_takes_good_X_and_rr(self):
        _regexp_1D_core(
            list('ab'),
            [((re.compile('[a-m]'), ''),), (re.compile('[b-d]'), 'B')]
        )

    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --



    def test_accuracy(self):

        #

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # all empty makes no changes
        X = list('abcde')
        _regexp_replace = [None for _ in range(len(X))]

        out = _regexp_1D_core(X, _regexp_replace)
        assert isinstance(out, list)
        assert np.array_equal(out, X)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # single replace
        X = list('abcde')
        _regexp_replace = [((re.compile('a'), ''),) for _ in range(len(X))]

        out = _regexp_1D_core(X, _regexp_replace)
        assert isinstance(out, list)
        assert np.array_equal(out, [''] + list('bcde'))

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # two replaced
        X = ['a', 'b', 'c', 'D E', 'F G']
        _regexp_replace = [
            None,
            None,
            None,
            (re.compile('[de]', re.I), ''),
            ((re.compile('q', re.I), ''), (re.compile('[fg]', re.I), '', re.I))
        ]

        out = _regexp_1D_core(X, _regexp_replace)
        assert isinstance(out, list)
        assert np.array_equal(out, ['a', 'b', 'c', ' ', ' '])

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # no matches
        X = list('abcde')
        _regexp_replace = [
            (re.compile('q', re.I), ''),
            (re.compile('r', re.X), ''),
            (re.compile('s'), ''),
            (re.compile('t'), ''),
            (re.compile('u'), '')
        ]

        out = _regexp_1D_core(X, _regexp_replace)
        assert isinstance(out, list)
        assert np.array_equal(out, list('abcde'))

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # callable
        X = list('abcde')
        _regexp_replace = [
            (re.compile('a', re.I), lambda x: 2*x),
            (re.compile('b', re.X), lambda x: 3*x),
            (re.compile('c'), lambda x: 4*x),
            (re.compile('d'), lambda x: 5*x),
            (re.compile('e'), lambda x: 6*x)
        ]

        out = _regexp_1D_core(X, _regexp_replace)
        assert isinstance(out, list)
        assert all(map(
            np.array_equal,
            out,
            ['aa', 'bbb', 'cccc', 'ddddd', 'eeeeee']
        ))

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --






