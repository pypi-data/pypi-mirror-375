# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from typing import Any

import numpy as np

from pybear.preprocessing._InterceptManager._partial_fit._find_constants \
    import _find_constants



class TestScipySparseSpecial:


    @pytest.mark.parametrize('_format',
        (
            'csr_array', 'csr_matrix',
            'coo_array', 'coo_matrix',
            'dia_array', 'dia_matrix',
            'bsr_array', 'bsr_matrix',
            'dok_array', 'dok_matrix',
            'lil_array', 'lil_matrix'
         )
    )
    def test_blocks_not_csc(self, _X_factory, _format, _columns, _shape):

        _X_wip = _X_factory(
            _format=_format, _dtype='flt', _columns=_columns,
            _has_nan=False, _constants=None, _shape=_shape
        )

        # this is raised by scipy let it raise whatever
        with pytest.raises(Exception):
            _find_constants(
                _X_wip,
                _equal_nan=True,
                _rtol=1e-5,
                _atol=1e-8
            )


    @pytest.mark.parametrize('_format', ('csc_array', 'csc_matrix'))
    @pytest.mark.parametrize('_dtype', ('flt', 'int'))
    def test_ss_all_zeros(self, _format, _dtype, _shape):

        # build X
        _X_wip = np.zeros(_shape).astype(np.uint8)

        # get constant idxs and their values
        out: dict[int, Any] = _find_constants(
            _X_wip,
            _equal_nan=True,
            _rtol=1e-5,
            _atol=1e-8
        )

        assert np.array_equal(list(out.keys()), list(range(_shape[1])))
        assert np.array_equal(list(out.values()), [0 for i in range(_shape[1])])



@pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csc_array'), scope='module')
@pytest.mark.parametrize('_dtype', ('flt', 'int', 'str', 'obj', 'hybrid'), scope='module')
@pytest.mark.parametrize('_has_nan', (True, False), scope='module')
@pytest.mark.parametrize('_equal_nan', (True, False), scope='module')
class TestFindConstants:


    # def _find_constants(
    #     _X: InternalXContainer,
    #     _equal_nan: bool,
    #     _rtol: numbers.Real,
    #     _atol: numbers.Real
    # ) -> ConstantColumnsType:


    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @staticmethod
    @pytest.fixture(scope='module')
    def _constants_1(_dtype):
        if _dtype in ('flt', 'int'):
            return {1:2, 2:2, 4:2, 6:2, 7:1}
        elif _dtype in ('str', 'obj', 'hybrid'):
            return {1: 'a', 2: 'b', 4: 'c', 6: 'd', 7: 'e'}
        else:
            raise Exception


    @staticmethod
    @pytest.fixture(scope='module')
    def _constants_2(_dtype):
        if _dtype in ('flt', 'int'):
            return {1:2, 2:2, 3:0, 4:2, 6:2, 7:1}
        elif _dtype in ('str', 'obj', 'hybrid'):
            return {1: 'a', 2: 'b', 3: 'z', 4: 'c', 6: 'd', 7: 'e'}
        else:
            raise Exception


    @staticmethod
    @pytest.fixture(scope='module')
    def _constants_3(_dtype):
        if _dtype in ('flt', 'int'):
            return {1:2, 2:2, 6:2, 7:1}
        elif _dtype in ('str', 'obj', 'hybrid'):
            return {1: 'a', 2: 'b', 6: 'd', 7: 'e'}
        else:
            raise Exception

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # @class level marks!
    @pytest.mark.parametrize('_constants_set', ('init', 'no', 'more', 'less'))
    def test_first_pass(
        self, _X_factory, _columns, _shape, _dtype, _format, _constants_set,
        _has_nan, _equal_nan, _constants_1, _constants_2, _constants_3
    ):

        # verifies accuracy of _find_constants on a single pass

        # skip impossible ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        if _format not in ('np', 'pd', 'pl') and _dtype in ('str', 'obj', 'hybrid'):
            pytest.skip(reason=f'scipy sparse only takes num')
        # END skip impossible ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # using these just to run more tests, the fact that they are
        # 'more' or 'less' compared to each other is not important, theyre
        # the fixtures available
        _constants = {
            'init': _constants_1, 'no': {},
            'more': _constants_2, 'less': _constants_3
        }[_constants_set]


        # build X
        _X_wip = _X_factory(
            _format=_format, _dtype=_dtype, _columns=_columns,
            _has_nan=_has_nan, _constants=_constants, _shape=_shape
        )

        # get constant idxs and their values
        out: dict[int, Any] = _find_constants(
            _X_wip,
            _equal_nan=_equal_nan,
            _rtol=1e-6,
            _atol=1e-6
        )


        # assert found constants indices and values vs expected are the same
        if (not _equal_nan and _has_nan) or _constants_set == 'no':
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
                elif _dtype in ('flt', 'int'):
                    assert np.isclose(_value, _constants[_idx], rtol=1e-6, atol=1e-6)
                elif _dtype in ('str', 'obj', 'hybrid'):
                    assert _value == _constants[_idx]
                else:
                    raise Exception
        else:
            raise Exception








