# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._MinCountTransformer._partial_fit. \
    _get_dtypes_unqs_cts import _get_dtypes_unqs_cts



class TestGetDtypesUnqsCts:


    @pytest.mark.parametrize('_format',
        (
            'coo_matrix', 'coo_array', 'dia_matrix', 'dia_array',
            'bsr_matrix', 'bsr_array', 'csr_matrix', 'csr_array',
            'lil_matrix', 'lil_array', 'dok_matrix', 'dok_array'
        )
    )
    def test_blocks_ss_not_csc(self, _X_factory, _format, _shape):

        _X_wip = _X_factory(
            _dupl=None,
            _format=_format,
            _dtype='flt',
            _has_nan=False,
            _columns=None,
            _zeros=0.75,
            _shape=_shape
        )

        with pytest.raises(AssertionError):
            _get_dtypes_unqs_cts(_X_wip)


    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'str', 'obj'))
    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csc_matrix', 'csc_array'))
    @pytest.mark.parametrize('_has_nan', (True, False))
    def test_accuracy(
        self, _X_factory, _columns, _shape, _dtype, _has_nan, _format
    ):

        # skip impossible conditions -- -- -- -- -- -- -- -- -- -- -- --
        if _format not in ('np', 'pd', 'pl') and _dtype not in ('int', 'flt'):
            pytest.skip(reason=f'scipy sparse cannot take str')
        # END skip impossible conditions -- -- -- -- -- -- -- -- -- --

        # we know from other tests that _pduc is accurate. _gduc just
        # makes repeated calls to that. just make sure it returns the
        # correct number of columns with the correct dtypes

        _X_wip = _X_factory(
            _dupl=None,
            _format=_format,
            _dtype=_dtype,
            _has_nan=_has_nan,
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _zeros=None,
            _shape=_shape
        )

        out = _get_dtypes_unqs_cts(_X_wip)

        assert len(out) == _shape[1]

        _exp_dtype= {
            'flt': 'float', 'int': 'int', 'str': 'obj', 'obj': 'obj'
        }[_dtype]

        for _tuple in out:
            assert _tuple[0] == _exp_dtype
            assert isinstance(_tuple[1], dict)


    @pytest.mark.parametrize('_format', ('csc_matrix', 'csc_array'))
    def test_accuracy_ss_all_zeros(self, _X_factory, _format, _shape):

        _X_wip = _X_factory(
            _dupl=[list(range(_shape[1]))],
            _format=_format,
            _dtype='flt',
            _has_nan=False,
            _constants={0: 0},
            _columns=None,
            _zeros=None,
            _shape=_shape
        )

        assert np.sum(_X_wip.toarray()) == 0

        out = _get_dtypes_unqs_cts(_X_wip)

        # all dtype/unq/ct tupls should be the same
        for _c_idx in range(_shape[1]):
            assert out[_c_idx][0] == 'int'  # because it is all zeros
            assert out[_c_idx][1][0] == _shape[0]





