# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Sequence

import pytest
import numbers

import numpy as np
import pandas as pd

from pybear.feature_extraction.text._TextStatistics.TextStatistics import\
    TextStatistics as TS
from pybear.base import is_fitted
from pybear.base.exceptions import NotFittedError
from ._read_green_eggs_and_ham import _read_green_eggs_and_ham



# v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
# FIXTURES

@pytest.fixture(scope='module')
def _X_list():
    return _read_green_eggs_and_ham()


@pytest.fixture(scope='module')
def _X_np(_X_list):
    return np.array(_X_list)


@pytest.fixture(scope='module')
def _X_pd(_X_np):
    return pd.Series(data=_X_np)

# END fixtures
# v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^



# ACCESS ATTR BEFORE AND AFTER FIT
class TestAttrAccessBeforeAndAfterFit:


    @pytest.mark.parametrize('store_uniques', (True, False))
    @pytest.mark.parametrize('x_format', ('list', 'np', 'pd'))
    def test_attr_access(
        self, _X_list, _X_np, _X_pd, store_uniques, x_format
    ):

        _attrs = [
            'size_',
            'overall_statistics_',
            'uniques_',
            'startswith_frequency_',
            'character_frequency_',
            'string_frequency_'
        ]

        if x_format == 'list':
            _X = _X_list.copy()
        elif x_format == 'np':
            _X = _X_np.copy()
        elif x_format == 'pd':
            _X = _X_pd.copy()
        else:
            raise Exception


        TestCls = TS(store_uniques=store_uniques)

        # BEFORE FIT ***************************************************

        for attr in _attrs:
            with pytest.raises(AttributeError):
                getattr(TestCls, attr)

        # parameter is accessible
        assert isinstance(getattr(TestCls, 'store_uniques', None), bool)

        # uniques_ and size_ cannot be set
        with pytest.raises(AttributeError):
            setattr(TestCls, 'uniques_', list('abc'))

        with pytest.raises(AttributeError):
            setattr(TestCls, 'size_', 37)

        # END BEFORE FIT ***********************************************

        # AFTER FIT ****************************************************

        TestCls.fit(_X)

        # all attrs should be accessible after fit
        for attr in _attrs:
            out = getattr(TestCls, attr)

            if attr == 'size_':
                assert isinstance(out, numbers.Integral)
            elif attr == 'overall_statistics_':
                assert isinstance(out, dict)
                assert all(map(isinstance, out, (str for _ in out)))
                for key in ['size', 'uniques_count', 'max_length']:
                    assert key in out
                assert all(map(
                    isinstance, out.values(),
                    (numbers.Real for _ in out)
                ))
            elif attr == 'uniques_':
                assert isinstance(attr, Sequence)
                assert all(map(isinstance, out, (str for _ in out)))
            elif attr == 'startswith_frequency_':
                assert isinstance(out, dict)
                assert all(map(isinstance, out, (str for _ in out)))
                assert all(map(lambda x: len(x) == 1, out))
                assert all(map(
                    isinstance, out.values(), (numbers.Integral for _ in out)
                ))
                assert all(map(lambda x: x >= 1, out.values()))
            elif attr == 'character_frequency_':
                assert isinstance(out, dict)
                assert all(map(isinstance, out, (str for _ in out)))
                assert all(map(lambda x: len(x) == 1, out))
                assert all(map(
                    isinstance, out.values(), (numbers.Integral for _ in out)
                ))
                assert all(map(lambda x: x >= 1, out.values()))
            elif attr == 'string_frequency_':
                assert isinstance(out, dict)
                assert all(map(isinstance, out, (str for _ in out)))
                assert all(map(
                    isinstance, out.values(), (numbers.Integral for _ in out)
                ))
            else:
                raise Exception

        # parameter is accessible
        assert isinstance(getattr(TestCls, 'store_uniques', None), bool)

        # uniques_ and size_ cannot be set
        with pytest.raises(AttributeError):
            setattr(TestCls, 'uniques_', list('abc'))

        with pytest.raises(AttributeError):
            setattr(TestCls, 'size_', 37)


        # END AFTER FIT ************************************************

        del _X, TestCls

# END ACCESS ATTR BEFORE AND AFTER FIT


# ACCESS METHODS BEFORE AND AFTER FIT ***
class TestMethodAccessBeforeAndAfterFit:


    @staticmethod
    @pytest.fixture(scope='function')
    def _methods():
        return [
            '_reset',
            'partial_fit',
            'fit',
            'get_params',
            'transform',
            'score',
            'print_overall_statistics',
            'print_startswith_frequency',
            'print_character_frequency',
            'print_string_frequency',
            'get_longest_strings',
            'print_longest_strings',
            'get_shortest_strings',
            'print_shortest_strings',
            'lookup_substring',
            'lookup_string'
        ]


    @pytest.mark.parametrize('store_uniques', (True, False))
    @pytest.mark.parametrize('x_format', ('list', 'np', 'pd'))
    def test_access_methods_before_fit(
        self, _X_list, _X_np, _X_pd, _methods, store_uniques, x_format
    ):

        if x_format == 'list':
            _X = _X_list.copy()
        elif x_format == 'np':
            _X = _X_np.copy()
        elif x_format == 'pd':
            _X = _X_pd.copy()
        else:
            raise Exception

        TestCls = TS(store_uniques=store_uniques)

        # **************************************************************
        # vvv BEFORE FIT vvv *******************************************

        # fit()
        assert isinstance(TestCls.fit(_X), TS)

        # HERE IS A CONVENIENT PLACE TO TEST _reset() ^v^v^v^v^v^v^v^v^v^v^v
        # Reset Changes is_fitted To False:
        # fit an instance  (done above)
        # assert the instance is fitted
        assert is_fitted(TestCls) is True
        # call :meth: _reset
        TestCls._reset()
        # assert the instance is not fitted
        assert is_fitted(TestCls) is False
        # END HERE IS A CONVENIENT PLACE TO TEST _reset() ^v^v^v^v^v^v^v^v^v

        TestCls._reset()

        assert isinstance(TestCls.partial_fit(_X), TS)

        TestCls._reset()

        for _method in _methods:

            if _method in ['fit', 'partial_fit', '_reset']:
                continue
            elif _method == 'get_params':
                out = getattr(TestCls, _method)()
                assert isinstance(out, dict)
                assert all(map(isinstance, out.keys(), (str for _ in out.keys())))
                assert list(out.keys())[0] == 'store_uniques'
            elif _method == 'transform':
                with pytest.raises(NotFittedError):
                    getattr(TestCls, _method)(_X)
            elif _method == 'score':
                with pytest.raises(NotFittedError):
                    getattr(TestCls, _method)(_X)
            elif _method == 'print_overall_statistics':
                with pytest.raises(NotFittedError):
                    getattr(TestCls, _method)()
            elif _method == 'print_startswith_frequency':
                with pytest.raises(NotFittedError):
                    getattr(TestCls, _method)()
            elif _method == 'print_character_frequency':
                with pytest.raises(NotFittedError):
                    getattr(TestCls, _method)()
            elif _method == 'print_string_frequency':
                with pytest.raises(NotFittedError):
                    getattr(TestCls, _method)(n=10)
            elif _method == 'get_longest_strings':
                with pytest.raises(NotFittedError):
                    getattr(TestCls, _method)(n=10)
            elif _method == 'print_longest_strings':
                with pytest.raises(NotFittedError):
                    getattr(TestCls, _method)(n=10)
            elif _method == 'get_shortest_strings':
                with pytest.raises(NotFittedError):
                    getattr(TestCls, _method)(n=10)
            elif _method == 'print_shortest_strings':
                with pytest.raises(NotFittedError):
                    getattr(TestCls, _method)(n=10)
            elif _method == 'lookup_substring':
                with pytest.raises(NotFittedError):
                    getattr(TestCls, _method)('look me up')
            elif _method == 'lookup_string':
                with pytest.raises(NotFittedError):
                    getattr(TestCls, _method)('look me up')
            else:
                raise Exception

        # END ^^^ BEFORE FIT ^^^ ***************************************
        # **************************************************************


    @pytest.mark.parametrize('store_uniques', (True, False))
    @pytest.mark.parametrize('x_format', ('list', 'np', 'pd'))
    def test_access_methods_after_fit(
        self, _X_list, _X_np, _X_pd, _methods, store_uniques, x_format
    ):

        # **************************************************************
        # vvv AFTER FIT vvv ********************************************

        if x_format == 'list':
            _X = _X_list.copy()
        elif x_format == 'np':
            _X = _X_np.copy()
        elif x_format == 'pd':
            _X = _X_pd.copy()
        else:
            raise Exception

        TestCls = TS(store_uniques=store_uniques)


        for _method in _methods:

            if _method == '_reset':
                continue
            elif _method == 'fit':
                assert isinstance(TestCls.fit(_X), TS)
                assert is_fitted(TestCls) is True
            elif _method == 'partial_fit':
                assert isinstance(TestCls.partial_fit(_X), TS)
            elif _method == 'get_params':
                out = getattr(TestCls, _method)()
                assert isinstance(out, dict)
                assert all(map(isinstance, out.keys(), (str for _ in out.keys())))
                assert list(out.keys())[0] == 'store_uniques'
            elif _method == 'transform':
                out = getattr(TestCls, _method)(_X)
                assert np.array_equal(out, _X)
            elif _method == 'score':
                assert getattr(TestCls, _method)(_X) is None
            elif _method == 'print_overall_statistics':
                assert getattr(TestCls, _method)() is None
            elif _method == 'print_startswith_frequency':
                assert getattr(TestCls, _method)() is None
            elif _method == 'print_character_frequency':
                assert getattr(TestCls, _method)() is None
            elif _method == 'print_string_frequency':
                assert getattr(TestCls, _method)(n=10) is None
            elif _method == 'get_longest_strings':
                out = getattr(TestCls, _method)(n=10)
                assert isinstance(out, dict)
                assert all(map(isinstance, out, (str for _ in out)))
                assert all(map(
                    isinstance, out.values(), (numbers.Integral for _ in out)
                ))
                if not store_uniques:
                    assert len(out) == 0
            elif _method == 'print_longest_strings':
                assert getattr(TestCls, _method)(n=10) is None
            elif _method == 'get_shortest_strings':
                out = getattr(TestCls, _method)(n=10)
                assert isinstance(out, dict)
                assert all(map(isinstance, out, (str for _ in out)))
                assert all(map(
                    isinstance, out.values(), (numbers.Integral for _ in out)
                ))
                if not store_uniques:
                    assert len(out) == 0
            elif _method == 'print_shortest_strings':
                assert getattr(TestCls, _method)(n=10) is None
            elif _method == 'lookup_substring':
                out = getattr(TestCls, _method)(
                    'I do so like',
                    case_sensitive=False
                )
                assert isinstance(out, Sequence)
                assert all(map(isinstance, out, (str for _ in out)))
                if store_uniques:
                    assert np.array_equal(out, ['I do so like'])
                else:
                    assert np.array_equal(out, [])
            elif _method == 'lookup_string':
                out = getattr(TestCls, _method)('I am Sam', case_sensitive=False)
                if store_uniques:
                    assert isinstance(out, Sequence)
                    assert all(map(isinstance, out, (str for _ in out)))
                    assert np.array_equal(out, ['I am Sam'])
                else:
                    assert isinstance(out, list)
                    assert len(out) == 0
            else:
                raise Exception

        # END ^^^ AFTER FIT ^^^ ****************************************
        # **************************************************************

# END ACCESS METHODS BEFORE AND AFTER FIT



