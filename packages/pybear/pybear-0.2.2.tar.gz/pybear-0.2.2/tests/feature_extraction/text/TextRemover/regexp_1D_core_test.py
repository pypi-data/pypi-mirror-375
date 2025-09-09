# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.feature_extraction.text._TextRemover._regexp_1D_core import \
    _regexp_1D_core



class TestRegExp1DCore:

    # no validation

    @pytest.mark.parametrize('_from_2D', (True, False))
    def test_None(self, _from_2D):
        # None skips -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        X = list('abcde')

        out_X, out_mask = \
            _regexp_1D_core(X, None, _from_2D)

        assert isinstance(out_X, list)
        assert np.array_equal(out_X, list('abcde'))

        assert isinstance(out_mask, np.ndarray)
        assert out_mask.dtype == np.bool_
        assert np.array_equal(out_mask, [True, True, True, True, True])
        # END False skips -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('_from_2D', (True, False))
    def test_str_one_match(self, _from_2D):
        # str, one match -- -- -- -- -- -- -- -- -- -- -- -- -- --
        X = list('abCde')
        out_X, out_mask = _regexp_1D_core(X, re.compile('c', re.I), _from_2D)

        assert isinstance(out_X, list)
        assert np.array_equal(out_X, list('abde'))

        assert isinstance(out_mask, np.ndarray)
        assert out_mask.dtype == np.bool_
        assert np.array_equal(out_mask, [True, True, False, True, True])
        # END str, one match -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('_from_2D', (True, False))
    def test_str_two_matches(self, _from_2D):
        # str, two matches -- -- -- -- -- -- -- -- -- -- -- -- -- --
        X = list('cbadC')
        out_X, out_mask = _regexp_1D_core(X, re.compile('c', re.I), _from_2D)

        assert isinstance(out_X, list)
        assert np.array_equal(out_X, list('bad'))

        assert isinstance(out_mask, np.ndarray)
        assert out_mask.dtype == np.bool_
        assert np.array_equal(out_mask, [False, True, True, True, False])
        ########
        X = list('cbadc')
        out_X, out_mask = _regexp_1D_core(X, re.compile('c'), _from_2D)

        assert isinstance(out_X, list)
        assert np.array_equal(out_X, list('bad'))

        assert isinstance(out_mask, np.ndarray)
        assert out_mask.dtype == np.bool_
        assert np.array_equal(out_mask, [False, True, True, True, False])
        # END str, two matches -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('_from_2D', (True, False))
    def test_tuples(self, _from_2D):
        # tuples -- -- -- -- -- -- -- -- -- -- -- -- -- --
        X = list('AbCdE')

        out_X, out_mask = _regexp_1D_core(
            X,
            (re.compile('A', re.I), re.compile('c', re.I), re.compile('E', re.I)),
            _from_2D
        )

        assert isinstance(out_X, list)
        assert np.array_equal(out_X, list('bd'))

        assert isinstance(out_mask, np.ndarray)
        assert out_mask.dtype == np.bool_
        assert np.array_equal(out_mask, [False, True, False, True, False])
        # tuples -- -- -- -- -- -- -- -- -- -- -- -- -- --


    def test_fails_list_rr_if_X_from_2D(self):

        with pytest.raises(TypeError):

            X = list('abcde')
            _regexp_1D_core(
                X,
                [
                    (re.compile('a'), re.compile('b'), re.compile('c')),
                    None,
                    re.compile(r'\w'),
                    re.compile('A|E', re.I),
                    None
                ],
                _from_2D=True
            )


    def test_list_rr_on_X_not_from_2D(self):

        # lists -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        X = list('abcde')
        out_X, out_mask = _regexp_1D_core(
            X,
            [
                (re.compile('a'), re.compile('b'), re.compile('c')),
                None,
                re.compile(r'\w'),
                re.compile('A|E', re.I),
                None
            ],
            _from_2D=False
        )

        assert isinstance(out_X, list)
        assert np.array_equal(out_X, list('bde'))

        assert isinstance(out_mask, np.ndarray)
        assert out_mask.dtype == np.bool_
        assert np.array_equal(out_mask, [False, True, False, True, True])

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # this one should fail for list inside a list
        X = list('abcde')
        with pytest.raises(TypeError):
            _regexp_1D_core(
                X,
                [
                    [re.compile('a|e'), re.compile('q')],
                    None,
                    re.compile(r'\w'),
                    (re.compile('a'), re.compile('b'), re.compile('c')),
                    None
                ],
                _from_2D=False
            )

        assert isinstance(out_X, list)
        assert np.array_equal(out_X, list('bde'))

        assert isinstance(out_mask, np.ndarray)
        assert out_mask.dtype == np.bool_
        assert np.array_equal(out_mask, [False, True, False, True, True])

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        X = list('abcde')
        out_X, out_mask = _regexp_1D_core(
            X,
            [
                re.compile('A|E'),
                None,
                re.compile('C'),
                re.compile('ABC'),
                None
            ],
            _from_2D=False
        )

        assert isinstance(out_X, list)
        assert np.array_equal(out_X, list('abcde'))

        assert isinstance(out_mask, np.ndarray)
        assert out_mask.dtype == np.bool_
        assert np.array_equal(out_mask, [True, True, True, True, True])

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        X = list('zzzzz')
        out_X, out_mask = _regexp_1D_core(
            X,
            [
                re.compile('z'),
                re.compile('z'),
                re.compile('z'),
                re.compile('z'),
                re.compile('z')
            ],
            _from_2D=False
        )

        assert isinstance(out_X, list)
        assert np.array_equal(out_X, [])

        assert isinstance(out_mask, np.ndarray)
        assert out_mask.dtype == np.bool_
        assert np.array_equal(out_mask, [False, False, False, False, False])
        # END lists -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --












