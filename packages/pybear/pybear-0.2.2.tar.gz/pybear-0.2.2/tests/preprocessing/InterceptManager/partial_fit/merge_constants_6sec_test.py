# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from typing import Any

import numpy as np

from pybear.preprocessing._InterceptManager._partial_fit._merge_constants \
    import _merge_constants



class TestMergeConstantsValidation:

    # old_constants ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('_old_constants',
        (-np.e, -1, 0, 1, np.e, True, False, 'trash', [0,1], (0,1), lambda x: x)
    )
    def test_old_constants_rejects_junk(self, _old_constants):
        with pytest.raises(AssertionError):
            _merge_constants(
                _old_constants,
                {0:1, 1:1},
                _rtol=1e-5,
                _atol=1e-8
            )


    def test_old_constants_rejects_bad(self):
        with pytest.raises(AssertionError):
            # keys must be col idxs
            _merge_constants(
                {'a':0, 'b':1, 'c':np.nan},
                {0:1, 1:1},
                _rtol=1e-5,
                _atol=1e-8
            )


    @pytest.mark.parametrize('_old_constants',
        (None, {}, {0: 1, 4: 0, 5: 0}, {0: 1, 2: np.nan})
    )
    def test_old_constants_accepts_good(self, _old_constants):
        _merge_constants(
            _old_constants,
            {0: 1, 1: 1},
            _rtol=1e-5,
            _atol=1e-8
        )
    # END old_constants ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # new_constants ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('_new_constants',
        (-np.e, -1, 0, 1, np.e, True, False, 'trash', [0,1], (0,1), lambda x: x)
    )
    def test_new_constants_rejects_junk(self, _new_constants):
        with pytest.raises(AssertionError):
            _merge_constants(
                {0:0, 1:1, 10:np.e},
                _new_constants,
                _rtol=1e-5,
                _atol=1e-8
            )


    @pytest.mark.parametrize('_new_constants',
        (None, {'a':0, 'b': 1, 'c':np.nan})
    )
    def test_new_constants_rejects_bad(self, _new_constants):
        # keys must be col idxs
        with pytest.raises(AssertionError):
            _merge_constants(
                {0:0, 1:1, 10:np.e},
                _new_constants,
                _rtol=1e-5,
                _atol=1e-8
            )


    @pytest.mark.parametrize('_new_constants',
        ({}, {0: 1, 4: 0, 5: 0}, {0: 1, 2: np.nan})
    )
    def test_new_constants_accepts_good(self, _new_constants):

        _merge_constants(
            {0: 0, 1: 1, 2: np.nan},
            _new_constants,
            _rtol=1e-5,
            _atol=1e-8
        )

    # END new_constants ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # rtol atol ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    @pytest.mark.parametrize('_junk',
        (None, 'trash', [0,1], (0,1), {0,1}, {'a':1}, lambda x: x)
    )
    def test_rtol_atol_rejects_junk(self, _junk):

        with pytest.raises(AssertionError):
            _merge_constants(
                {0:0, 1:1, 10:np.e},
                {},
                _rtol=_junk,
                _atol=1e-8
            )

        with pytest.raises(AssertionError):
            _merge_constants(
                {0: 0, 1: 1, 10: np.e},
                {},
                _rtol=1e-5,
                _atol=_junk
            )


    @pytest.mark.parametrize('_bad', (-np.e, -1, True, False))
    def test_rtol_atol_rejects_bad(self, _bad):

        with pytest.raises(AssertionError):
            _merge_constants(
                {0: 0, 1: 1, 10: np.e},
                {},
                _rtol=_bad,
                _atol=1e-8
            )

        with pytest.raises(AssertionError):
            _merge_constants(
                {0: 0, 1: 1, 10: np.e},
                {},
                _rtol=1e-5,
                _atol=_bad
            )


    @pytest.mark.parametrize('_good', (0, 1e-5, 1, np.e))
    def test_rtol_atol_accepts_good(self, _good):

        _merge_constants(
            {0: 0, 1: 1, 10: np.e},
            {},
            _rtol=_good,
            _atol=1e-8
        )

        _merge_constants(
            {0: 0, 1: 1, 10: np.e},
            {},
            _rtol=1e-5,
            _atol=_good
        )

    # END rtol atol  ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


@pytest.mark.parametrize('_dtype', ('num', 'str'), scope='module')
class TestMergeConstants:


    # def _merge_constants(
    #     _old_constants: ConstantColumnsType | None,
    #     _new_constants: ConstantColumnsType,
    #     _rtol: numbers.Real,
    #     _atol: numbers.Real
    # ) -> ConstantColumnsType:


    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @staticmethod
    @pytest.fixture(scope='module')
    def _init_constants(_dtype):
        if _dtype == 'num':
            return {1:2, 2:2, 4:2, 6:2, 7:1}
        elif _dtype == 'str':
            return {1: 'a', 2: 'b', 4: 'c', 6: 'd', 7: 'e'}


    @staticmethod
    @pytest.fixture(scope='module')
    def _more_constants(_dtype):
        if _dtype == 'num':
            return {1:2, 2:2, 3:0, 4:2, 6:2, 7:1}
        elif _dtype == 'str':
            return {1: 'a', 2: 'b', 3: 'z', 4: 'c', 6: 'd', 7: 'e'}


    @staticmethod
    @pytest.fixture(scope='module')
    def _less_constants(_dtype):
        if _dtype == 'num':
            return {1:2, 2:2, 6:2, 7:1}
        elif _dtype == 'str':
            return {1: 'a', 2: 'b', 6: 'd', 7: 'e'}

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    @pytest.mark.parametrize('_constants_set', ('init', 'no', 'more', 'less'))
    def test_first_pass(
        self, _constants_set, _init_constants, _more_constants, _less_constants,
        _dtype
    ):

        # verifies accuracy of _merge_constants on a single pass

        # using these just to run more tests, the fact that they are
        # 'more' or 'less' compared to each other is not important, theyre
        # the fixtures available
        _constants = {
            'init': _init_constants, 'no': {},
            'more': _more_constants, 'less': _less_constants
        }[_constants_set]


        # get constant idxs and their values
        out: dict[int, Any] = _merge_constants(
            _old_constants=None,   # first pass! occ must be None!
            _new_constants=_constants,
            _rtol=1e-6,
            _atol=1e-6
        )

        # on first pass, the output of _find_constants is returned directly.
        # assert found constants indices and values vs expected are the same
        if _constants_set == 'no':
            # with no constants, or not _equal_nan, there can be no constants
            assert out == {}
        elif _constants_set in ('init', 'more', 'less'):
            # num out constant columns == num given constant columns
            assert len(out) == len(_constants)
            # out constant column idxs == given constant column idxs
            assert np.array_equal(sorted(list(out)), sorted(list(_constants)))
            # out constant column values == given constant column values
            for _idx, _value in out.items():
                if str(_value) == 'nan':
                    assert str(_constants[_idx]) == 'nan'
                elif _dtype == 'num':
                    assert np.isclose(
                        _value, _constants[_idx], rtol=1e-6, atol=1e-6
                    )
                elif _dtype == 'str':
                    assert _value == _constants[_idx]
                else:
                    raise Exception


    def test_less_constants_found(self, _init_constants, _less_constants, _dtype):

        # verifies accuracy of _merge_constants when second partial fit
        # has less constants than the first

        # _columns_getter only allows csc

        # get first partial fit constants
        _first_fit_constants: dict[int, Any] = _merge_constants(
            _old_constants=None,   # first pass! occ must be None!
            _new_constants=_init_constants,
            _rtol=1e-6,
            _atol=1e-6
        )

        # get second partial fit constants
        _scd_fit_constants: dict[int, Any] = _merge_constants(
            _old_constants=_first_fit_constants, # <=========
            _new_constants=_less_constants,
            _rtol=1e-6,
            _atol=1e-6
        )

        # on a partial fit where less duplicates are found, outputted melded
        # duplicates should reflect the lesser columns
        assert np.array_equal(
            sorted(list(_scd_fit_constants)), sorted(list(_less_constants))
        )
        for _col_idx, _value in _scd_fit_constants.items():
            if str(_value) == 'nan':
                assert str(_less_constants[_col_idx]) == 'nan'
            elif _dtype == 'num':
                assert np.isclose(
                    _value, _less_constants[_col_idx], rtol=1e-6, atol=1e-6
                )
            elif _dtype == 'str':
                assert _value == _less_constants[_col_idx]
            else:
                raise Exception


    def test_more_constants_found(self, _init_constants, _more_constants, _dtype):

        # verifies accuracy of _merge_constants when second partial fit
        # has more constants than the first

        # _columns_getter only allows csc

        # get first partial fit constants
        _first_fit_constants: dict[int, Any] = _merge_constants(
            _old_constants=None,   # first pass! occ must be None
            _new_constants=_init_constants,
            _rtol=1e-6,
            _atol=1e-6
        )

        # get second partial fit constants
        _scd_fit_constants: dict[int, Any] = _merge_constants(
            _old_constants=_first_fit_constants, # <=========
            _new_constants=_more_constants,
            _rtol=1e-6,
            _atol=1e-6
        )

        # on a partial fit where more duplicates are found, outputted melded
        # duplicates should not add the newly found columns
        assert np.array_equal(
            sorted(list(_scd_fit_constants)), sorted(list(_init_constants))
        )
        for _col_idx, _value in _scd_fit_constants.items():
            if str(_value) == 'nan':
                assert str(_init_constants[_col_idx]) == 'nan'
            elif _dtype == 'num':
                assert np.isclose(
                    _value, _init_constants[_col_idx], rtol=1e-6, atol=1e-6
                )
            elif _dtype == 'str':
                assert _value == _init_constants[_col_idx]
            else:
                raise Exception


    def test_more_and_less_constants_found(
        self, _init_constants, _less_constants, _more_constants, _dtype
    ):

        # verifies accuracy of _merge_constants when partial fits after the
        # first have both more and less constants

        # _columns_getter only allows csc

        # get first partial fit constants
        _first_fit_constants: dict[int, Any] = _merge_constants(
            _old_constants=None,  # first pass!  occ must be None!
            _new_constants=_init_constants,
            _rtol=1e-6,
            _atol=1e-6
        )

        # get second partial fit constants
        _scd_fit_constants: dict[int, Any] = _merge_constants(
            _old_constants=_first_fit_constants,  # <=========
            _new_constants=_more_constants,
            _rtol=1e-6,
            _atol=1e-6
        )

        # get third partial fit constants
        _third_fit_constants: dict[int, Any] = _merge_constants(
            _old_constants=_scd_fit_constants,  # <=========
            _new_constants=_less_constants,
            _rtol=1e-6,
            _atol=1e-6
        )

        # on a partial fit where more duplicates are found, outputted melded
        # duplicates should not add the newly found columns
        # on a partial fit where less duplicates are found, outputted melded
        # duplicates should reflect the lesser columns
        # the net effect should be that final output is the lesser columns
        assert np.array_equal(
            sorted(list(_third_fit_constants)), sorted(list(_less_constants))
        )
        for _col_idx, _value in _third_fit_constants.items():
            if str(_value) == 'nan':
                assert str(_less_constants[_col_idx]) == 'nan'
            elif _dtype == 'num':
                assert np.isclose(
                    _value, _less_constants[_col_idx], rtol=1e-6, atol=1e-6
                )
            elif _dtype == 'str':
                assert _value == _less_constants[_col_idx]
            else:
                raise Exception




