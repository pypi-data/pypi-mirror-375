# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy
import itertools

import numpy as np

from pybear.preprocessing import ColumnDeduplicator as CDT



class TestAccuracy:


    @pytest.mark.parametrize('X_format', ('np', 'pd')) #, 'pl', 'csr_array'))
    @pytest.mark.parametrize('X_dtype', ('flt', 'int', 'str', 'obj', 'hybrid'))
    @pytest.mark.parametrize('has_nan', (True, False))
    @pytest.mark.parametrize('dupls', (None, [[0, 2, 9]], [[0, 6], [1, 8]]))
    @pytest.mark.parametrize('keep', ('first', 'last', 'random'))
    @pytest.mark.parametrize('do_not_drop', (None, [0, 5], 'pd')) #, 'pl'))
    @pytest.mark.parametrize('conflict', ('raise', 'ignore'))
    @pytest.mark.parametrize('equal_nan', (True, False))
    def test_accuracy(
        self, _X_factory, _kwargs, X_format, X_dtype, has_nan,
        dupls, keep, do_not_drop, conflict, _columns, equal_nan, _shape
    ):

        # validate the test parameters
        assert keep in ['first', 'last', 'random']
        assert isinstance(do_not_drop, (list, type(None), str))
        assert conflict in ['raise', 'ignore']
        assert isinstance(equal_nan, bool)
        # END validate the test parameters

        # skip impossible combinations v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        if X_dtype not in ['flt', 'int'] and X_format not in ['np', 'pd', 'pl']:
            pytest.skip(reason=f"scipy sparse cant take str")

        if X_format == 'np' and X_dtype == 'int' and has_nan:
            pytest.skip(reason=f"numpy int dtype cant take 'nan'")

        if do_not_drop in ['pd', 'pl']:
            if X_format not in ['pd', 'pl']:
                pytest.skip(
                    reason=f"impossible condition, str dnd and format is not pd"
                )
        # END skip impossible combinations v^v^v^v^v^v^v^v^v^v^v^v^v^v^v



        # BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        _X_wip = _X_factory(
            _dupl=dupls,
            _has_nan=has_nan,
            _format=X_format,
            _dtype=X_dtype,
            _columns=_columns,
            _constants=None,
            _noise=0,
            _zeros=None,
            _shape=_shape
        )
        # END BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        # set do_not_drop as list of strings for dfs (vs None or list of ints)
        if do_not_drop in ['pd', 'pl']:
            do_not_drop = list(map(str, [_columns[0], _columns[3], _columns[7]]))
        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # set _kwargs
        _kwargs['keep'] = keep
        _kwargs['do_not_drop'] = do_not_drop
        _kwargs['conflict'] = conflict
        _kwargs['rtol'] = 1e-5
        _kwargs['atol'] = 1e-8
        _kwargs['equal_nan'] = equal_nan

        TestCls = CDT(**_kwargs)

        # get exp_dupls & manage error conditions ----------------------
        exp_dupls = deepcopy(dupls or [])
        if has_nan and not equal_nan:
            exp_dupls = []

        _conflict_condition = (dupls is not None) and (do_not_drop is not None) \
                              and (keep == 'last') and not (has_nan and not equal_nan)
        # only because all non-None dupls and non-None do_not_drop
        # have zeros in them
        # END get exp_dupls & manage error conditions ------------------

        # v v v fit & transform v v v v v v v v v v v v v v v v v v
        if _conflict_condition and conflict == 'raise':
            with pytest.raises(ValueError):
                TestCls.fit_transform(_X_wip)
            pytest.skip(reason=f"dont do remaining tests")
        else:
            TRFM_X = TestCls.fit_transform(_X_wip)
        # ^ ^ ^ END fit & transform ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^


        # get expected number of kept columns
        exp_num_kept = _X_wip.shape[1] - sum([len(_) - 1 for _ in exp_dupls])


        # ASSERTIONS ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # attributes:
        #     'n_features_in_'
        #     'feature_names_in_'
        #     'duplicates_'
        #     'removed_columns_'
        #     'column_mask_'
        # and 'get_feature_names_out'

        # attr 'n_features_in_' is correct
        assert TestCls.n_features_in_ == _X_wip.shape[1]

        # attr 'feature_names_in_' is correct
        if X_format in ['pd', 'pl']:
            assert np.array_equal(TestCls.feature_names_in_, _columns)
            assert TestCls.feature_names_in_.dtype == object
        else:
            assert not hasattr (TestCls, 'feature_names_in_')

        # number of columns in output == number of columns in column_mask_
        assert TRFM_X.shape[1] == exp_num_kept


        # keep ('first','last','random') is correct when not muddied by do_not_drop
        # also build ref objects along the way for testing attrs
        ref_column_mask = [True for _ in range(_X_wip.shape[1])]
        ref_removed_columns = {}
        if X_format in ['pd', 'pl']:
            ref_feature_names_out = list(deepcopy(_columns))
        else:
            ref_feature_names_out = [f'x{i}' for i in range(_shape[1])]

        if not _conflict_condition:
            # in this case, column idxs cannot be overridden by do_not_drop
            for _set in exp_dupls:
                if keep == 'first':
                    for idx in _set[1:]:
                        ref_column_mask[idx] = False
                        ref_removed_columns[idx] = _set[0]
                        ref_feature_names_out[idx] = None
                elif keep == 'last':
                    for idx in _set[:-1]:
                        ref_column_mask[idx] = False
                        ref_removed_columns[idx] = _set[-1]
                        ref_feature_names_out[idx] = None
                elif keep == 'random':
                    # cop out a little here, since we cant know what index
                    # was kept, use TestCls.removed_columns_ for help
                    # (even tho removed_columns_ is something we are trying
                    # to verify)
                    ref_removed_columns = deepcopy(TestCls.removed_columns_)
                    _kept_idxs = sorted(list(
                        np.unique(list(TestCls.removed_columns_.values()))
                    ))
                    assert len(_kept_idxs) == len(exp_dupls)
                    _dropped_idxs = sorted(list(
                        np.unique(list(TestCls.removed_columns_.keys()))
                    ))
                    for idx in _dropped_idxs:
                        ref_column_mask[idx] = False
                        ref_feature_names_out[idx] = None

        elif _conflict_condition and conflict == 'raise':
            # this should have raised above
            raise Exception
        elif _conflict_condition and conflict == 'ignore':
            # this could get really complicated.
            # cop out here again, since the logic behind what index
            # was kept is really complicated, use TestCls.removed_columns_
            # for help (even tho removed_columns_ is something we are trying
            # to verify)
            ref_removed_columns = deepcopy(TestCls.removed_columns_)
            _kept_idxs = sorted(list(
                np.unique(list(TestCls.removed_columns_.values()))
            ))
            assert len(_kept_idxs) == len(exp_dupls)
            _dropped_idxs = sorted(list(
                np.unique(list(TestCls.removed_columns_.keys()))
            ))
            for idx in _dropped_idxs:
                ref_column_mask[idx] = False
                ref_feature_names_out[idx] = None
        else:
            raise Exception


        # validate TestCls attrs against ref objects v^v^v^v^v^v^v^v^v^v

        # column_mask_ ------------
        # number of columns in output is adjusted correctly for num duplicates
        assert len(ref_column_mask) == TestCls.n_features_in_
        assert sum(ref_column_mask) == exp_num_kept
        assert len(TestCls.column_mask_) == TestCls.n_features_in_
        assert sum(TestCls.column_mask_) == exp_num_kept
        assert np.array_equal(ref_column_mask, TestCls.column_mask_)
        # assert all columns that werent dupls are in the output
        _all_dupls = list(itertools.chain(*exp_dupls))
        for col_idx in range(_shape[1]):
            if col_idx not in _all_dupls:
                assert TestCls.column_mask_[col_idx] is np.True_
        # END column_mask_ ------------

        # feature_names_out ------------
        # for convenient index management, positions to be dropped from
        # ref_feature_names_out were set to None, take those out now
        ref_feature_names_out = [i for i in ref_feature_names_out if i is not None]
        assert len(TestCls.get_feature_names_out()) == exp_num_kept
        assert np.array_equal(
            ref_feature_names_out,
            TestCls.get_feature_names_out()
        )
        # END feature_names_out ------------

        # 'duplicates_' --------------------------------
        if len(exp_dupls) == 0:
            assert len(TestCls.duplicates_) == 0
        else:
            for idx, set in enumerate(exp_dupls):
                assert np.array_equal(set, exp_dupls[idx])
        # END 'duplicates_' ----------------------------

        # removed_columns_ --------------------
        _, __ = TestCls.removed_columns_, ref_removed_columns
        assert np.array_equal(sorted(list(_.keys())), sorted(list(__.keys())))
        assert np.array_equal(sorted(list(_.values())), sorted(list(__.values())))
        del _, __
        # END removed_columns_ --------------------

        # END validate TestCls attrs against ref objects v^v^v^v^v^v^v^v

        # END ASSERTIONS ** * ** * ** * ** * ** * ** * ** * ** * ** * **




