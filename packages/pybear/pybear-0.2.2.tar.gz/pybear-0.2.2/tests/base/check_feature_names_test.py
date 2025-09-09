# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.base._check_feature_names import check_feature_names

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

import pytest



class TestCheckFeatureNames:

    # def check_feature_names(
    #     X,
    #     feature_names_in_: npt.NDArray[object] | None,
    #     reset: bool
    # ) -> npt.NDArray[object] | None:


    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # X -- - -- - -- - -- - -- - -- - -- - -- - -- - -- - -- - -- - -- -
    # currently there is no validation for X
    # END X -- - -- - -- - -- - -- - -- - -- - -- - -- - -- - -- - -- -

    # feature_names_in_ -- - -- - -- - -- - -- - -- - -- - -- - -- - --
    @pytest.mark.parametrize('junk_feature_names_in',
        (-1, 0, 1, True, False, np.pi, {'a': 1}, 'junk', min, lambda x: x)
    )
    def test_rejects_junk_fni(self, _X_np, junk_feature_names_in):
        with pytest.raises(TypeError):
            check_feature_names(_X_np, junk_feature_names_in, True)


    @pytest.mark.parametrize('bad_fni',
        (
            list(range(4)),
            np.arange(4, dtype=object),
            set(range(4))
        )
    )
    def test_rejects_non_str(self, _X_np, bad_fni):

        with pytest.raises(TypeError):
            check_feature_names(_X_np, bad_fni, False)


    def test_feature_names_in_accepts_listlike_of_strings_or_None(
        self, _X_np, _columns
    ):

        check_feature_names(
            _X_np,
            feature_names_in_=_columns,
            reset=True
        )

        check_feature_names(
            _X_np,
            feature_names_in_=None,
            reset=True
        )

    # END feature_names_in_ -- - -- - -- - -- - -- - -- - -- - -- - -- -

    # reset -- - -- - -- - -- - -- - -- - -- - -- - -- - -- - -- - -- -
    @pytest.mark.parametrize('junk_reset',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', np.pi, [1,2], {'a': 1}, lambda x: x)
    )
    def test_reset_rejects_non_bool(self, _X_np, _columns, junk_reset):

        with pytest.raises(AssertionError):
            check_feature_names(
                _X_np,
                _columns,
                junk_reset
            )

    @pytest.mark.parametrize('_reset', (True, False))
    def test_reset_accepts_bool(self, _X_np, _columns, _reset):

        check_feature_names(
            _X_np,
            _columns,
            _reset
        )
    # END reset -- - -- - -- - -- - -- - -- - -- - -- - -- - -- - -- -

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # accuracy ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csr'))
    @pytest.mark.parametrize('_columns_is_passed_on_X', (True, False))
    @pytest.mark.parametrize('_previously_saw_feature_names', (True, False))
    def test_reset_True_always_returns_currently_seen_feature_names(
        self, _X_np, _columns, _format, _columns_is_passed_on_X,
        _previously_saw_feature_names
    ):

        # already seen feature names are irrelevant

        if _format == 'np':
            _X_wip = _X_np
        elif _format == 'pd':
            _X_wip = pd.DataFrame(
                data=_X_np,
                columns=_columns if _columns_is_passed_on_X else None
            )
        elif _format == 'pl':
            _X_wip = pl.from_numpy(
                data=_X_np,
                schema=list(_columns) if _columns_is_passed_on_X else None
            )
        elif _format == 'csr':
            _X_wip = ss.csr_array(_X_np)
        else:
            raise Exception

        out = check_feature_names(
            _X_wip,
            feature_names_in_=_columns if _previously_saw_feature_names else None,
            reset=True  # <+========================
        )

        # the only thing that should return an actual header is for DF
        if _format in ['pd', 'pl'] and _columns_is_passed_on_X:
            assert np.array_equal(out, _columns)
        elif _format == 'pl':   # could only be explicit columns not passed
            assert np.array_equal(out, [f'column_{i}' for i in range(_X_np.shape[1])])
        else:
            assert out is None


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csr'))
    @pytest.mark.parametrize('_columns_is_passed_on_X', (True, False))
    def test_reset_False_no_feature_names_at_first_fit(
        self, _X_np, _columns, _format, _columns_is_passed_on_X
    ):

        # if no feature names on current data, a-ok
        # if current X has feature names, then warns

        if _format == 'np':
            _X_wip = _X_np
        elif _format == 'pd':
            _X_wip = pd.DataFrame(
                data=_X_np,
                columns=_columns if _columns_is_passed_on_X else None
            )
        elif _format == 'pl':
            _X_wip = pl.from_numpy(
                data=_X_np,
                schema=list(_columns) if _columns_is_passed_on_X else None
            )
        elif _format == 'csr':
            _X_wip = ss.csr_array(_X_np)
        else:
            raise Exception

        # the only thing that should return an actual header is for DF
        # this should warn because feature names were not previously seen
        if (_format == 'pd' and _columns_is_passed_on_X) or _format == 'pl':
            with pytest.warns():
                out = check_feature_names(
                    _X_wip,
                    feature_names_in_=None,  # <+========================
                    reset=False  # <+========================
                )
        else:
            out = check_feature_names(
                _X_wip,
                feature_names_in_=None,  # <+========================
                reset=False  # <+========================
            )

        assert out is None


    @pytest.mark.parametrize('_format', ('np', 'pd', 'pl', 'csr'))
    @pytest.mark.parametrize('_columns_is_passed_on_X', (True, False))
    def test_reset_False_feature_names_at_first_fit(
        self, _X_np, _columns, _format, _columns_is_passed_on_X
    ):

        # if no feature names on current data, warns
        # if current X has feature names, then a-ok

        if _format == 'np':
            _X_wip = _X_np
        elif _format == 'pd':
            _X_wip = pd.DataFrame(
                data=_X_np,
                columns=_columns if _columns_is_passed_on_X else None
            )
        elif _format == 'pl':
            _X_wip = pl.from_numpy(
                data=_X_np,
                schema=list(_columns) if _columns_is_passed_on_X else None
            )
        elif _format == 'csr':
            _X_wip = ss.csr_array(_X_np)
        else:
            raise Exception

        # the only thing that should return an actual header is for DF
        # this should not warn
        if (_format in ['pd', 'pl'] and _columns_is_passed_on_X):
            out = check_feature_names(
                _X_wip,
                feature_names_in_=_columns,  # <+========================
                reset=False  # <+========================
            )

            # this verifies that the correct header is returned when
            # feature_names_in_ exists and the currently seen header matches
            assert np.array_equal(out, _columns)
        elif _format == 'pl':   # could only be explicit columns not passed

            _default_columns = [f'column_{i}' for i in range(_X_np.shape[1])]

            out = check_feature_names(
                _X_wip,
                feature_names_in_=_default_columns,  # <+========================
                reset=False  # <+========================
            )

            assert np.array_equal(out, _default_columns)
        else:
            with pytest.warns():
                out = check_feature_names(
                    _X_wip,
                    feature_names_in_=_columns,  # <+========================
                    reset=False  # <+========================
            )

            # this verifies that feature_names_in_ is returned when
            # feature_names_in_ exists and there is no current header
            assert np.array_equal(out, _columns)


    @pytest.mark.parametrize('X_shape', ((20, 4), (20, 5), (20, 6)))
    @pytest.mark.parametrize('_current_header_is_flipped', (True, False))
    def test_reset_False_feature_names_dont_match(
        self, _X_factory, _master_columns, _columns, X_shape, _shape,
        _current_header_is_flipped
    ):


        _current_features = _master_columns.copy()[:X_shape[1]]
        if _current_header_is_flipped:
            _current_features = np.flip(_current_features)

        _previously_seen_features = _master_columns.copy()[:_shape[1]]

        _X_wip = pd.DataFrame(
            data=np.random.randint(0, 10, X_shape),
            columns=_current_features
        )

        if X_shape[1] == _shape[1] and not _current_header_is_flipped:

            out = check_feature_names(
                _X_wip,
                feature_names_in_=_previously_seen_features,
                reset=False
            )

            assert np.array_equal(out, _columns)

        else:
            with pytest.raises(ValueError):
                check_feature_names(
                    _X_wip,
                    feature_names_in_=_previously_seen_features,
                    reset=False
                )





