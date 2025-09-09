# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._SlimPolyFeatures._partial_fit._columns_getter \
    import _columns_getter



class TestColumnsGetter:


    @pytest.mark.parametrize('_format',
        ('csr_array', 'csr_matrix', 'coo_array', 'coo_matrix', 'dia_array',
         'dia_matrix', 'lil_array', 'lil_matrix', 'dok_array', 'dok_matrix',
         'bsr_array', 'bsr_matrix')
    )
    def test_block_non_csc(self, _X_factory, _format, _columns, _shape):

        # _columns_getter could onlu use ss that are indexable
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
        ((0,), (20,), (0,1), (0,200), (100,200), ((0,1), (3,200)))
    )
    def test_rejects_idx_out_of_col_range(self, _X_factory, _col_idxs, _shape):

        _out_of_range = False
        try:
            list(map(iter, _col_idxs))
            # is a tuple of tuples
            for _tuple in _col_idxs:
                for _idx in _tuple:
                    if _tuple not in range(_shape[1]):
                        _out_of_range = True
        except:
            # is tuple of ints
            for _idx in _col_idxs:
                if _idx not in range(_shape[1]):
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
    @pytest.mark.parametrize('_col_idxs',
        ((0,), (1,), (0,1), (0,2), ((0,1), (2,3)), ((0,1,2), ))
    )
    def test_accuracy(
        self, _X_factory, _col_idxs, _format, _columns, _shape
    ):

        # _columns_getter only allows ss csc.

        _X_wip = _X_factory(
            _format=_format,
            _dtype='flt',
            _has_nan=False,
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _shape=_shape
        )

        # pass _col_idxs as given to _columns_getter
        _poly = _columns_getter(_X_wip, _col_idxs)


        # assertions v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        assert isinstance(_poly, np.ndarray)
        if all(map(isinstance, _col_idxs, (int for i in _col_idxs))):
            assert _poly.shape[1] == 1
        elif all(map(isinstance, _col_idxs, (tuple for i in _col_idxs))):
            assert _poly.shape[1] == len(_col_idxs)
        else:
            raise Exception

        # now that _columns_getter has seen the given _col_idxs, convert all
        # given _col_idxs to tuple/tuple to make _X[:, _col_idxs] slice right, below
        try:
            list(map(iter, _col_idxs))  # except if is integer
        except:  # if is integer change to tuple
            _col_idxs = (_col_idxs,)

        assert _poly.shape[1] == len(_col_idxs)

        # convert the og container to np for easy comparison against out
        if isinstance(_X_wip, np.ndarray):
            _X_ref = _X_wip
        elif hasattr(_X_wip, 'columns'):
            _X_ref = _X_wip.to_numpy()
        elif hasattr(_X_wip, 'toarray'):
            _X_ref = _X_wip.toarray()
        else:
            raise Exception

        _ref_poly = np.empty((_X_wip.shape[0], 0), dtype=np.float64)
        for _idxs in _col_idxs:
            _ref_poly = np.hstack((
                _ref_poly, _X_ref[:, _idxs].prod(1).reshape((-1,1))
            ))


        assert np.array_equal(
            _poly.astype(np.float64),
            _ref_poly.astype(np.float64),
            equal_nan=True
        )




