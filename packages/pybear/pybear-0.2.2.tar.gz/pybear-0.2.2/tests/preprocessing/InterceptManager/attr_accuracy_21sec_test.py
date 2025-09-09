# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

import numpy as np

from pybear.preprocessing import InterceptManager as IM

from pybear.utilities import nan_mask



class TestAccuracy:


    @pytest.mark.parametrize('X_format', ('np', 'pl')) #, 'pd', 'csr_array'))
    @pytest.mark.parametrize('X_dtype', ('flt', 'int', 'str', 'obj', 'hybrid'))
    @pytest.mark.parametrize('has_nan', (True, False))
    @pytest.mark.parametrize('equal_nan', (True, False))
    @pytest.mark.parametrize('constants',
        ('constants1', 'constants2', 'constants3')
    )
    @pytest.mark.parametrize('keep',
        ('first', 'last', 'random', 'none', 'int', 'string', 'callable',
        {'Intercept': 1})
    )
    def test_accuracy(
        self, _X_factory, _kwargs, X_format, X_dtype, has_nan, equal_nan,
        constants, keep, _columns, _shape
    ):

        # validate the test parameters
        assert keep in ['first', 'last', 'random', 'none'] or \
                    isinstance(keep, (int, dict, str)) or callable(keep)
        assert isinstance(has_nan, bool)
        assert isinstance(equal_nan, bool)
        # dont need to validate X_format, X_factory will do it
        assert X_dtype in ('flt', 'int', 'str', 'obj', 'hybrid')
        # END validate the test parameters

        # skip impossible combinations v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        if X_dtype not in ['flt', 'int'] and X_format not in ['np', 'pd', 'pl']:
            pytest.skip(reason=f"scipy sparse cant take str")

        if X_format == 'np' and X_dtype == 'int' and has_nan:
            pytest.skip(reason=f"numpy int dtype cant take 'nan'")
        # END skip impossible combinations v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # set constants v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        if constants == 'constants1':
            constants = None
        elif constants == 'constants2':
            if X_dtype in ('flt', 'int'):
                constants = {0: 1, 2: 1, 9: 1}
            elif X_dtype in ('str', 'obj', 'hybrid'):
                constants = {0: 1, 2: 'a', 9: 'b'}
            else:
                raise Exception
        elif constants == 'constants3':
            if X_dtype in ('flt', 'int'):
                constants = {0: 1, 1: 1, 6: np.nan, 8: 1}
            elif X_dtype in ('str', 'obj', 'hybrid'):
                constants = {0: 'a', 1: 'b', 6: 'nan', 8: '1'}
            else:
                raise Exception
        else:
            raise Exception
        # END set constants v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
        _X_wip = _X_factory(
            _dupl=None,
            _has_nan=has_nan,
            _format=X_format,
            _dtype=X_dtype,
            _columns=_columns,
            _constants=constants,
            _noise=0,
            _zeros=None,
            _shape=_shape
        )
        # END BUILD X v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

        # set keep v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
        if keep == 'string':
            keep = _columns[0]
        elif keep == 'int':
            if constants:
                keep = sorted(list(constants.keys()))[-1]
            else:
                keep = 0
        elif keep == 'callable':
            if constants:
                keep = lambda x: sorted(list(constants.keys()))[-1]
            else:
                keep = lambda x: 0
        else:
            # keep is not changed
            pass
        # END set keep v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # set _kwargs
        _kwargs['keep'] = keep
        _kwargs['equal_nan'] = equal_nan

        TestCls = IM(**_kwargs)

        # get exp_constants & manage error conditions ------------------
        exp_constants = deepcopy(constants or {})
        if has_nan and not equal_nan:
            exp_constants = {}

        # if there are constants, and any of them are nan-like, but
        # not equal_nan, then that column cant be a constant, so remove
        if not equal_nan and len(exp_constants) and \
                any(nan_mask(np.array(list(exp_constants.values())))):
            exp_constants = \
                {k:v for k,v in exp_constants.items() if str(v) != 'nan'}

        # if data is not pd/pl and user put in keep as feature_str, will raise
        raise_for_no_header_str_keep = False
        if X_format not in ['pd', 'pl'] and isinstance(keep, str) and \
                keep not in ('first', 'last', 'random', 'none'):
            raise_for_no_header_str_keep += 1

        # if data has no constants and
        # user put in keep as feature_str/int/callable, will raise
        raise_for_keep_non_constant = False
        if not exp_constants:
            if callable(keep):
                raise_for_keep_non_constant += 1
            if isinstance(keep, int):
                raise_for_keep_non_constant += 1
            if isinstance(keep, str) and \
                    keep not in ('first', 'last', 'random', 'none'):
                raise_for_keep_non_constant += 1
        # END get exp_constants & manage error conditions --------------

        # v v v fit & transform v v v v v v v v v v v v v v v v v v
        if raise_for_no_header_str_keep or raise_for_keep_non_constant:
            with pytest.raises(ValueError):
                TestCls.fit(_X_wip)
            pytest.skip(reason=f"cant do anymore tests without fit")
        else:
            TRFM_X = TestCls.fit_transform(_X_wip)
        # ^ ^ ^ END fit & transform ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^

        del raise_for_keep_non_constant, raise_for_no_header_str_keep

        # get expected number of kept columns
        exp_num_kept = _shape[1]  # start with full num of columns
        if not has_nan or (has_nan and equal_nan):
            if len(exp_constants):
                # if there are constants, 'none' removes all n of them,
                # but all other 'keep' arguments remove n-1
                exp_num_kept -= len(exp_constants)
                exp_num_kept +=  (keep != 'none') # this catches dict
            else:
                # if there are no constants, all that could happen is that
                # keep dict is appended
                exp_num_kept += isinstance(keep, dict)
        elif has_nan and not equal_nan:
            # in this case there are no constant columns, all that could
            # happen is that keep dict is appended
            exp_num_kept += isinstance(keep, dict)
        else:
            raise Exception(f"algorithm failure")


        # ASSERTIONS ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # attributes:
        #     'n_features_in_'
        #     'feature_names_in_'
        #     'constant_columns_'
        #     'kept_columns_'
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

        # number of columns in output == number of expected
        assert TRFM_X.shape[1] == exp_num_kept


        # keep ('first','last','random','none') is correct
        # also build ref objects along the way for testing attrs
        ref_column_mask = [True for _ in range(_X_wip.shape[1])]
        ref_kept_columns = {}
        ref_removed_columns = {}
        if X_format in ['pd', 'pl']:
            ref_feature_names_out = list(deepcopy(_columns))
        else:
            ref_feature_names_out = [f'x{i}' for i in range(_shape[1])]

        _sorted_constant_idxs = sorted(list(exp_constants.keys()))

        if keep == 'first':
            if len(_sorted_constant_idxs):
                _first = _sorted_constant_idxs[0]
                ref_kept_columns[_first] = exp_constants[_first]
                del _first

                for idx in _sorted_constant_idxs[1:]:
                    ref_column_mask[idx] = False
                    ref_removed_columns[idx] = exp_constants[idx]
                    ref_feature_names_out[idx] = None
            # if there are no constants, then ref objects do not change
        elif keep == 'last':
            if len(_sorted_constant_idxs):
                _last = _sorted_constant_idxs[-1]
                ref_kept_columns[_last] = exp_constants[_last]
                del _last

                for idx in _sorted_constant_idxs[:-1]:
                    ref_column_mask[idx] = False
                    ref_removed_columns[idx] = exp_constants[idx]
                    ref_feature_names_out[idx] = None
            # if there are no constants, then ref objects do not change
        elif keep == 'random':
            # cop out a little here, since we cant know what index
            # was kept, use TestCls attr for help
            # (even tho the attrs are something we are trying
            # to verify)
            if len(_sorted_constant_idxs):
                assert len(TestCls.kept_columns_) == 1
                _kept_idx = list(TestCls.kept_columns_.keys())[0]
                assert _kept_idx in exp_constants
                ref_kept_columns[_kept_idx] = exp_constants[_kept_idx]
                assert _kept_idx not in TestCls.removed_columns_

                for idx in _sorted_constant_idxs:
                    if idx == _kept_idx:
                        continue
                    ref_column_mask[idx] = False
                    ref_removed_columns[idx] = exp_constants[idx]
                    ref_feature_names_out[idx] = None
                del _kept_idx
            # if there are no constants, then ref objects do not change
        elif keep == 'none':
            # ref_kept_columns does not change
            for idx in _sorted_constant_idxs:
                ref_column_mask[idx] = False
                ref_removed_columns[idx] = exp_constants[idx]
                ref_feature_names_out[idx] = None
        elif isinstance(keep, dict):
            # ref_kept_columns does not change
            for idx in _sorted_constant_idxs:
                ref_column_mask[idx] = False
                ref_removed_columns[idx] = exp_constants[idx]
                ref_feature_names_out[idx] = None
            ref_feature_names_out.append(list(keep.keys())[0])
        elif isinstance(keep, int):
            # if no constants, should have excepted and skipped above
            ref_kept_columns[keep] = exp_constants[keep]
            for idx in _sorted_constant_idxs:
                if idx == keep:
                    continue
                else:
                    ref_column_mask[idx] = False
                    ref_removed_columns[idx] = exp_constants[idx]
                    ref_feature_names_out[idx] = None
        elif isinstance(keep, str):  # must be a feature str
            # if no constants, should have excepted and skipped above
            # if no header, should have excepted and skipped above
            _kept_idx = np.arange(len(_columns))[_columns == keep][0]
            ref_kept_columns[_kept_idx] = exp_constants[_kept_idx]
            for idx in _sorted_constant_idxs:
                if idx == _kept_idx:
                    continue
                else:
                    ref_column_mask[idx] = False
                    ref_removed_columns[idx] = exp_constants[idx]
                    ref_feature_names_out[idx] = None
            del _kept_idx
        elif callable(keep):
            # if no constants, should have excepted and skipped above
            _kept_idx = keep(_X_wip)
            ref_kept_columns[_kept_idx] = exp_constants[_kept_idx]
            for idx in _sorted_constant_idxs:
                if idx == _kept_idx:
                    continue
                else:
                    ref_column_mask[idx] = False
                    ref_removed_columns[idx] = exp_constants[idx]
                    ref_feature_names_out[idx] = None
        else:
            raise Exception


        # validate TestCls attrs against ref objects v^v^v^v^v^v^v^v^v^v

        # column_mask_ ------------
        # number of columns in output is adjusted correctly for num constants
        # column_mask_ is never adjusted for keep is dict. it is always
        # meant to be applied to pre-transform data.
        assert len(ref_column_mask) == TestCls.n_features_in_
        assert sum(ref_column_mask) + isinstance(keep, dict) == exp_num_kept
        assert len(TestCls.column_mask_) == TestCls.n_features_in_
        assert sum(TestCls.column_mask_) + isinstance(keep, dict) == exp_num_kept
        assert np.array_equal(ref_column_mask, TestCls.column_mask_)
        # assert all columns that werent constants are in the output
        for col_idx in range(_shape[1]):
            if col_idx not in _sorted_constant_idxs:
                assert TestCls.column_mask_[col_idx] is np.True_
        # END column_mask_ ------------

        # feature_names_out ------------
        # for convenient index management, positions to be dropped from
        # ref_feature_names_out were set to None, take those out now
        ref_feature_names_out = [i for i in ref_feature_names_out if i is not None]
        assert len(TestCls.get_feature_names_out()) == exp_num_kept
        assert np.array_equal(
            TestCls.get_feature_names_out(),
            ref_feature_names_out
        )
        # END feature_names_out ------------

        # constant_columns_ , kept_columns_, removed_columns_ ----------

        # all are dictionaries
        # compare keys of act vs exp and
        # compare values of act vs exp

        for _act, _exp in (
            (TestCls.constant_columns_, exp_constants),
            (TestCls.kept_columns_, ref_kept_columns),
            (TestCls.removed_columns_, ref_removed_columns)
        ):

            assert len(_act) == len(_exp)

            # attr keys, which should always be col idxs (ints) -- -- --
            assert np.array_equal(
                sorted(list(_act.keys())),
                sorted(list(_exp.keys()))
            )
            # END attr keys, which should always be col idxs (ints) --

            # attr values, which could be str or num -- -- -- -- -- --
            _act = list(_act.values())
            _exp = list(_exp.values())

            try:
                np.array(_act).astype(np.float64)
                np.array(_exp).astype(np.float64)
                raise UnicodeError
            except UnicodeError:
                # dict values are numeric
                assert np.allclose(
                    np.array(_act, dtype=np.float64),
                    np.array(_exp, dtype=np.float64),
                    equal_nan=True
                )
            except Exception as e:
                # dict values are str

                # if values are not num, could be num and str mixed
                # together array_equal is not working in this case.
                # need to iterate over all constant values and check
                # separately.

                for idx in range(len(_act)):
                    try:
                        list(map(float, [_act[idx], _exp[idx]]))
                        if str(_act[idx]) == 'nan' or str(_exp[idx]) == 'nan':
                            raise Exception
                        raise UnicodeError
                    except UnicodeError:
                        # is num
                        assert np.isclose(float(_act[idx]), float(_exp[idx]))
                    except Exception as e:
                        # is str or nan
                        assert str(_act[idx]) == str(_exp[idx])
            # END attr values, which could be str or num -- -- -- -- --

        # END constant_columns_ , kept_columns_, removed_columns_ ------

        # END validate TestCls attrs against ref objects v^v^v^v^v^v^v^v

        # END ASSERTIONS ** * ** * ** * ** * ** * ** * ** * ** * ** * **




