# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._MinCountTransformer._partial_fit._columns_getter \
    import _columns_getter



class TestColumnsGetter:


    @pytest.mark.parametrize('_format',
        ('csr_array', 'csr_matrix', 'coo_array', 'coo_matrix', 'dia_array',
         'dia_matrix', 'lil_array', 'lil_matrix', 'dok_array', 'dok_matrix',
         'bsr_array', 'bsr_matrix')
    )
    def test_block_non_csc(self, _X_factory, _format, _columns, _shape):

        # _columns_getter could only use ss that are indexable
        # coo, dia, & bsr matrix/array must be blocked
        # the others are blocked because internally only csc is used

        _X_wip = _X_factory(
            _format=_format,
            _dupl=None, _has_nan=False, _dtype='flt', _columns=None,
            _constants=None, _noise=0, _zeros=None, _shape=_shape
        )

        with pytest.raises(AssertionError):
            _columns_getter(_X_wip, tuple((0, 1, 2)))


    @pytest.mark.parametrize('_col_idxs',
        (0, 20, (0,), (20,), (0,1), (0,20), (100,200))
    )
    def test_rejects_idx_out_of_col_range(self, _X_factory, _col_idxs, _shape):

        _out_of_range = False
        try:
            tuple(_col_idxs)
            # is a tuple
            for _idx in _col_idxs:
                if _idx not in range(_shape[1]):
                    _out_of_range = True
        except:
            # is int
            if _col_idxs not in range(_shape[1]):
                _out_of_range = True

        _X = _X_factory(
            _format='np',
            _dtype='flt',
            _has_nan=False,
            _shape=_shape
        )

        if _out_of_range:
            with pytest.raises(AssertionError):
                _columns_getter(_X, _col_idxs)
        else:
            assert isinstance(_columns_getter(_X, _col_idxs), np.ndarray)


    @pytest.mark.parametrize('_format',
        ('np', 'pd', 'pl', 'csc_array', 'csc_matrix')
    )
    @pytest.mark.parametrize('_col_idxs', (0, 2, (0,), (1,), (0,2), (0,1,2)))
    def test_accuracy(self, _X_factory, _shape, _columns, _col_idxs, _format):

        # _columns_getter only allows ss csc.

        _X_wip = _X_factory(
            _format=_format,
            _dtype='flt',
            _has_nan=False,
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _shape=_shape
        )

        # pass _col_idxs as given (int or tuple) to _columns getter
        _extracted = _columns_getter(_X_wip, _col_idxs)


        # assertions v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        assert isinstance(_extracted, np.ndarray)
        assert len(_extracted.shape) == 2

        # now that _columns_getter has seen the given _col_idxs, convert all
        # given _col_idxs to tuple to make _X[:, _col_idxs] slice right, below
        try:
            len(_col_idxs)  # except if is integer
        except:  # if is integer change to tuple
            _col_idxs = (_col_idxs,)

        assert _extracted.shape[1] == len(_col_idxs)

        # convert the og container to np for easy comparison against
        # extracted
        if isinstance(_X_wip, np.ndarray):
            _X_ref = _X_wip
        elif hasattr(_X_wip, 'columns'):
            _X_ref = _X_wip.to_numpy()
        elif hasattr(_X_wip, 'toarray'):
            _X_ref = _X_wip.toarray()
        else:
            raise Exception


        # 25_05_28 pd numeric with junky nan-likes are coming out of
        # _columns_getter as dtype object. since _columns_getter produces
        # an intermediary container that is used to find constants and
        # doesnt impact the container coming out of transform, ok to let
        # that condition persist and just fudge the dtype for this test.
        assert np.array_equal(
            _extracted.astype(np.float64),
            _X_ref[:, _col_idxs].astype(np.float64),
            equal_nan=True
        )




