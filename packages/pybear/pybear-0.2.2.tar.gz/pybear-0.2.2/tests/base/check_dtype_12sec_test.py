# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.base._check_dtype import check_dtype

import pytest

import numpy as np
import scipy.sparse as ss
import polars as pl



class TestCheckDtype:


    @staticmethod
    @pytest.fixture(scope='module')
    def _shape():
        # this is transposed after building with X_factory. need to do
        # this so that that there arent sporadic events like, "this row
        # wants to raise for disallowed nans but this row wants to raise
        # for bad dtype." every row of data has at least one nan-like in
        # it, X_factory normally controls the number of nans in every
        # column, not by row.
        return (10, 20)


    # validation * * * * * * * * * * * * * * * * * * * * * * * * * * * *

    @pytest.mark.parametrize('junk_allowed',
        (-2.7, -1, 0, 1, 2.7, None, [0,1], (0,1), {'A':1}, lambda x: x)
    )
    def test_blocks_junk_allowed(self, junk_allowed):

        with pytest.raises(TypeError):
            check_dtype(
                np.random.randint(0, 10, (8,5)),
                allowed=junk_allowed,
                require_all_finite=False
            )


    @pytest.mark.parametrize('bad_allowed',
        ('junk', 'trash', 'garbage', 'waste', 'rubbish')
    )
    def test_blocks_bad_allowed(self, bad_allowed):

        with pytest.raises(ValueError):
            check_dtype(
                np.random.randint(0, 10, (8,5)),
                allowed=bad_allowed,
                require_all_finite=False
            )


    @pytest.mark.parametrize('good_allowed', ('numeric', 'str', 'any'))
    def test_accepts_good_allowed(self, good_allowed):

        if good_allowed in ['numeric', 'any']:
            out = check_dtype(
                np.random.randint(0, 10, (8,5)),
                allowed=good_allowed,
                require_all_finite=False
            )

        if good_allowed in ['str', 'any']:
            out = check_dtype(
                np.random.choice(list('abcde'), (8,5), replace=True),
                allowed=good_allowed,
                require_all_finite=False
            )

        assert out is None

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('junk_require_all_finite',
        (-2.7, -1, 0, 1, 2.7, None, [0,1], (0,1), {'A':1}, lambda x: x)
    )
    def test_blocks_junk_require_all_finite(self, junk_require_all_finite):

        with pytest.raises(TypeError):
            check_dtype(
                np.random.randint(0, 10, (8,5)),
                allowed='any',
                require_all_finite=junk_require_all_finite
            )


    @pytest.mark.parametrize('good_require_all_finite', (True, False))
    def test_accepts_good_require_all_finite(self, good_require_all_finite):

        out = check_dtype(
            np.random.randint(0, 10, (8,5)),
            allowed='any',
            require_all_finite=good_require_all_finite
        )

        assert out is None

    # END validation * * * * * * * * * * * * * * * * * * * * * * * * * *


    @staticmethod
    @pytest.fixture(scope='module')
    def _format_getter():
        return {
            'py_list': 'np',
            'py_tuple': 'np',
            'py_set': 'np',
            'np': 'np',
            'pd': 'pd',
            'pl': 'pl',
            'csr': 'csr',
            'csc': 'csc',
            'coo': 'coo'
        }


    @pytest.mark.parametrize('_require_all_finite', (True, False))
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_format',
        ('py_list', 'py_tuple', 'py_set', 'np', 'pd', 'pl', 'csr', 'csc', 'coo')
    )
    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'str', 'obj', 'hybrid'))
    @pytest.mark.parametrize('_has_nan', (True, False))
    def test_accuracy_any(
        self, _X_factory, _shape, _format_getter, _require_all_finite, _dim,
        _format, _dtype, _has_nan
    ):

        # skip impossible conditions -- -- -- -- -- -- -- -- -- -- -- --

        # scipy sparse can only be numeric
        if _format in ['csr', 'csc', 'coo'] and \
                _dtype in ['str', 'obj', 'hybrid']:
            pytest.skip(reason=f"impossible condition")

        # scipy sparse can only be 2D
        if _format in ['csr', 'csc', 'coo'] and _dim == 1:
            pytest.skip(reason=f"impossible condition")

        # cant be hybrid (by the conftest meaning of hybrid) for 1D
        # each column has 1 dtype, must have multiple columns to be hybrid
        if _dim == 1 and _dtype == 'hybrid':
            pytest.skip(reason=f"impossible condition")

        # cant be 2D sets
        if _dim == 2 and _format == 'py_set':
            pytest.skip(reason=f"impossible condition")

        # this wont take any nans
        if _dim == 2 and _format == 'pl' and _dtype=='hybrid':
            pytest.skip(reason=f"this wont take any nans")
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # build X -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _X_wip = _X_factory(
            _dupl=None,
            _constants=None,
            _format=_format_getter[_format],
            _zeros=None,
            _columns=None,
            _has_nan=_has_nan,
            _shape=_shape,  # conftest was built to take at least 2 columns
            _dtype=_dtype
        )

        # control of the dispersion of nans by row isnt important here.

        if _format == 'py_list':
            if _dim == 1:
                _X_wip = _X_wip[:, 0].tolist()
            elif _dim == 2:
                _X_wip = list(map(list, _X_wip))
        elif _format == 'py_tuple':
            if _dim == 1:
                _X_wip = tuple(_X_wip[:, 0].tolist())
            elif _dim == 2:
                _X_wip = tuple(map(tuple, _X_wip))
        elif _format == 'py_set':
            if _dim == 1:
                _X_wip = set(_X_wip[:, 0].tolist())
            elif _dim == 2:
                raise Exception(f'this should have been skipped')
        elif _format == 'np':
            if _dim == 1:
                _X_wip = _X_wip[:, 0]
        elif _format == 'pd':
            if _dim == 1:
                _X_wip = _X_wip.iloc[:, 0].squeeze()
        elif _format == 'pl':
            if _dim == 1:
                _X_wip = _X_wip[:, 0]
                assert isinstance(_X_wip, pl.Series)
        elif _format == 'csr':
            # can only be 2D
            assert isinstance(_X_wip, ss._csr.csr_array)
        elif _format == 'csc':
            # can only be 2D
            assert isinstance(_X_wip, ss._csc.csc_array)
        elif _format == 'coo':
            # can only be 2D
            assert isinstance(_X_wip, ss._coo.coo_array)
        else:
            raise Exception
        # END build X -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _require_all_finite and _has_nan:
            with pytest.raises(ValueError):
                check_dtype(
                    _X_wip,
                    allowed='any',
                    require_all_finite=_require_all_finite
                )
        else:
            out = check_dtype(
                _X_wip,
                allowed='any',
                require_all_finite=_require_all_finite
            )


    @pytest.mark.parametrize('_require_all_finite', (True, False))
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_format',
        ('py_list', 'py_tuple', 'py_set', 'np', 'pd', 'pl', 'csr', 'csc', 'coo')
    )
    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'str', 'obj', 'hybrid'))
    @pytest.mark.parametrize('_has_nan', (3, False))
    def test_accuracy_num(
        self, _X_factory, _shape, _format_getter, _require_all_finite, _dim,
        _format, _dtype, _has_nan
    ):

        # skip impossible conditions -- -- -- -- -- -- -- -- -- -- -- --

        # scipy sparse can only be 2D
        if _format in ['csr', 'csc', 'coo']:
            if _dim == 1:
                pytest.skip(reason=f"cant have 1D scipy sparse")
            if _dtype in ['str', 'obj', 'hybrid']:
                pytest.skip(reason=f"cant have str in scipy sparse")

        # cant be hybrid (by the conftest meaning of hybrid) for 1D
        # each column has 1 dtype, must have multiple columns to be hybrid
        if _dim == 1 and _dtype == 'hybrid':
            pytest.skip(reason=f"impossible condition")

        # cant be 2D sets
        if _dim == 2 and _format == 'py_set':
            pytest.skip(reason=f"impossible condition")

        # this wont take any nans
        if _dim == 2 and _format == 'pl' and _dtype=='hybrid':
            pytest.skip(reason=f"this wont take any nans")
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # build X -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _X_wip = _X_factory(
            _dupl=None,
            _constants=None,
            _format=_format_getter[_format],
            _zeros=None,
            _columns=None,
            _has_nan=_has_nan,
            _shape=_shape,  # conftest was built to take at least 2 columns
            _dtype=_dtype
        )

        # need to control the dispersion of shape, so that if there are
        # any nans, there is at least one in each row. see the notes in
        # the 'shape' fixture.
        _X_wip = _X_wip.transpose()    # transpose() works for np, pd, ss

        if _format == 'py_list':
            if _dim == 1:
                _X_wip = _X_wip[:, 0].tolist()
            elif _dim == 2:
                _X_wip = list(map(list, _X_wip))
        elif _format == 'py_tuple':
            if _dim == 1:
                _X_wip = tuple(_X_wip[:, 0].tolist())
            elif _dim == 2:
                _X_wip = tuple(map(tuple, _X_wip))
        elif _format == 'py_set':
            if _dim == 1:
                _X_wip = set(_X_wip[:, 0].tolist())
            elif _dim == 2:
                raise Exception(f'this should have been skipped')
        elif _format == 'np':
            if _dim == 1:
                _X_wip = _X_wip[:, 0]
        elif _format == 'pd':
            if _dim == 1:
                _X_wip = _X_wip.iloc[:, 0].squeeze()
        elif _format == 'pl':
            if _dim == 1:
                _X_wip = pl.Series(_X_wip[:, 0])
        elif _format == 'csr':
            # can only be 2D
            # csr become csc because of transpose
            assert isinstance(_X_wip, ss._csc.csc_array)
        elif _format == 'csc':
            # can only be 2D
            # csc become csr because of transpose
            assert isinstance(_X_wip, ss._csr.csr_array)
        elif _format == 'coo':
            # can only be 2D
            assert isinstance(_X_wip, ss._coo.coo_array)
        else:
            raise Exception
        # END build X -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _dtype in ['int', 'flt']:

            if _require_all_finite and _has_nan:
                with pytest.raises(ValueError):
                    check_dtype(
                        _X_wip,
                        allowed='numeric',
                        require_all_finite=_require_all_finite
                    )
            else:

                out = check_dtype(
                    _X_wip,
                    allowed='numeric',
                    require_all_finite=_require_all_finite
                )

                assert out is None

        else:

            if _require_all_finite and _has_nan:
                # this ValueError is for non-finite. this should raise before
                # the TypeErrors. this is why controlling the dispersion of
                # nans is important.
                with pytest.raises(ValueError):

                    check_dtype(
                        _X_wip,
                        allowed='numeric',
                        require_all_finite=_require_all_finite
                    )
            else:
                # this TypeError would be for bad dtype, not bad container
                # bad dtype always raises after the ValueError for non-finite.
                with pytest.raises(TypeError):

                    check_dtype(
                        _X_wip,
                        allowed='numeric',
                        require_all_finite=_require_all_finite
                    )


    @pytest.mark.parametrize('_require_all_finite', (True, False))
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_format',
        ('py_list', 'py_tuple', 'py_set', 'np', 'pd', 'pl')
    )
    @pytest.mark.parametrize('_dtype', ('flt', 'int', 'str', 'obj', 'hybrid'))
    @pytest.mark.parametrize('_has_nan', (3, False))
    def test_accuracy_str(
        self, _X_factory, _shape, _format_getter, _require_all_finite, _dim,
        _format, _dtype, _has_nan
    ):

        # skip impossible conditions -- -- -- -- -- -- -- -- -- -- -- --

        # cant be hybrid (by the conftest meaning of hybrid) for 1D
        # each column has 1 dtype, must have multiple columns to be hybrid
        if _dim == 1 and _dtype == 'hybrid':
            pytest.skip(reason=f"impossible condition")

        # cant be 2D sets
        if _dim == 2 and _format == 'py_set':
            pytest.skip(reason=f"impossible condition")

        # this wont take any nans
        if _dim == 2 and _format == 'pl' and _dtype=='hybrid':
            pytest.skip(reason=f"this wont take any nans")
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # build X -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        while True:
            # do this under a loop to control the output
            _X_wip = _X_factory(
                _dupl=None,
                _constants=None,
                _format=_format_getter[_format],
                _zeros=None,
                _columns=None,
                _has_nan=_has_nan,
                _shape=_shape,  # conftest was built to take at least 2 columns
                _dtype=_dtype
            )

            # need to control the dispersion of shape, so that if there are
            # any nans, there is at least on in each row. see the notes in
            # the 'shape' fixture.
            _X_wip = _X_wip.transpose()    # transpose() works for np & pd

            # cant have all nans in a 1D
            try:
                __ = _X_wip.iloc[:, 0].tolist()
            except:
                __ = _X_wip[:, 0]
            if not all(map(lambda x: x is np.nan, __)):
                del __
                break


        if _format == 'py_list':
            if _dim == 1:
                _X_wip = _X_wip[:, 0].tolist()
            elif _dim == 2:
                _X_wip = list(map(list, _X_wip))
        elif _format == 'py_tuple':
            if _dim == 1:
                _X_wip = tuple(_X_wip[:, 0].tolist())
            elif _dim == 2:
                _X_wip = tuple(map(tuple, _X_wip))
        elif _format == 'py_set':
            if _dim == 1:
                _X_wip = set(_X_wip[:, 0].tolist())
            elif _dim == 2:
                raise Exception(f'this should have been skipped')
        elif _format == 'np':
            if _dim == 1:
                _X_wip = _X_wip[:, 0]
        elif _format == 'pd':
            if _dim == 1:
                _X_wip = _X_wip.iloc[:, 0].squeeze()
        elif _format == 'pl':
            if _dim == 1:
                _X_wip = pl.Series(_X_wip[:, 0])
        else:
            raise Exception
        # END build X -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _dtype in ['str', 'obj']:

            if _require_all_finite and _has_nan:
                with pytest.raises(ValueError):
                    check_dtype(
                        _X_wip,
                        allowed='str',
                        require_all_finite=_require_all_finite
                    )
            else:

                out = check_dtype(
                    _X_wip,
                    allowed='str',
                    require_all_finite=_require_all_finite
                )

                assert out is None

        else:

            if _require_all_finite and _has_nan:
                # this ValueError is for non-finite. this should raise before
                # the TypeErrors. this is why controlling the dispersion of
                # nans is important.
                with pytest.raises(ValueError):
                    check_dtype(
                        _X_wip,
                        allowed='str',
                        require_all_finite=_require_all_finite
                    )
            else:
                # this TypeError would be for bad dtype, not bad container
                # bad dtype always raises after the ValueError for non-finite.
                with pytest.raises(TypeError):
                    check_dtype(
                        _X_wip,
                        allowed='str',
                        require_all_finite=_require_all_finite
                    )







