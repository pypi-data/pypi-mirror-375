# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



# the accuracy of get_feature_names_out() output relies solely on
# base._get_feature_names_out() and MCT.get_support(). the accuracy of
# both are thoroughly tested elsewhere. test this module minimally.
# test that raises before fit and column_mask_ slice is applied to
# _get_feature_names_out().


import pytest

from copy import deepcopy

import numpy as np

from pybear.preprocessing import MinCountTransformer as MCT

# base._get_feature_names_out handles validation, tested elsewhere.


@pytest.mark.parametrize('_format', ('np', 'pd', 'pl'), scope='module')
@pytest.mark.parametrize('_instance_state',
    ('after_fit', 'after_transform'), scope='module'
)
class TestInputFeaturesRejects:


    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @staticmethod
    @pytest.fixture(scope='class')
    def _TestCls(_instance_state, _X_factory, _format, _columns, _shape):

        TestCls = MCT()

        _X = _X_factory(
            _format=_format,
            _dupl=None,
            _dtype='int',
            _columns=_columns if _format in ['pd', 'pl'] else None,
            _constants=None,
            _noise=0,
            _shape=_shape
        )

        if _instance_state == 'after_fit':
            TestCls.fit(_X)
            return TestCls
        elif _instance_state == 'after_transform':
            TestCls.fit_transform(_X)
            return TestCls
        else:
            raise Exception

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    @pytest.mark.parametrize('junk_input_features',
        (float('inf'), np.pi, 'garbage', {'junk': 3}, list(range(10)))
    )
    def test_input_features_rejects_junk(self, _TestCls, junk_input_features):

        # **** CAN ONLY TAKE LIST-TYPE OF STRS OR None

        with pytest.raises(ValueError):
            _TestCls.get_feature_names_out(junk_input_features)


    def test_input_features_rejects_bad(self, _format, _TestCls, _shape):
        # -------------
        # SHOULD RAISE ValueError IF
        # len(input_features) != n_features_in_
        with pytest.raises(ValueError):
            # columns too long
            _TestCls.get_feature_names_out([f"x{i}" for i in range(2 * _shape[1])])

        with pytest.raises(ValueError):
            # columns too short
            _TestCls.get_feature_names_out([f"x{i}" for i in range(_shape[1]//2)])

        if _format in ['pd', 'pl']:
            # WITH HEADER PASSED, SHOULD RAISE ValueError IF
            # column names not same as originally passed during fit
            with pytest.raises(ValueError):
                _TestCls.get_feature_names_out([f"x{i}" for i in range(_shape[1])])

        # -------------


class TestGetFeatureNamesOut:


    @pytest.mark.parametrize('_format, _columns_is_passed',
        (('np', False), ('pd', True), ('pd', False), ('pl', True), ('pl', False)),
        scope='module'
    )
    @pytest.mark.parametrize('_instance_state',
        ('after_fit', 'after_transform'), scope='module'
    )
    @pytest.mark.parametrize('_input_features_is_passed', (True, False))
    def test_accuracy(
        self, _X_factory, _instance_state, _kwargs, _format,
        _columns, _shape, _input_features_is_passed, _columns_is_passed
    ):

        # build X ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        _dropped_col_idx = np.random.choice(_shape[1])

        # a set of data that will have one column removed
        _X_wip = _X_factory(
            _dupl=None,
            _format=_format,
            _dtype='flt',
            _columns=_columns if _columns_is_passed else None,
            _constants={_dropped_col_idx: 1},
            _noise=0,
            _shape=_shape
        )

        # END build X ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # prepare the MCT instance ** * ** * ** * ** * ** * ** * ** * **
        _new_kwargs = deepcopy(_kwargs)
        _new_kwargs['count_threshold'] = _shape[0] // 5
        _new_kwargs['ignore_float_columns'] = True
        _new_kwargs['ignore_non_binary_integer_columns'] = False

        TestCls = MCT(**_new_kwargs)

        if _instance_state == 'after_fit':
            TestCls.fit(_X_wip)
        elif _instance_state == 'after_transform':
            TestCls.fit_transform(_X_wip)
        else:
            raise Exception
        # END prepare the IM instance ** * ** * ** * ** * ** * ** * ** *

        # get actual ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        if _input_features_is_passed:
            if _format == 'pl' and not _columns_is_passed:
                with pytest.raises(ValueError):
                    TestCls.get_feature_names_out(_columns)
                # get the actual feature names anyway
                out = TestCls.get_feature_names_out(None)
            else:
                out = TestCls.get_feature_names_out(_columns)
        elif not _input_features_is_passed:
            out = TestCls.get_feature_names_out(None)
        # END get actual ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        # determine expected ** * ** * ** * ** * ** * ** * ** * ** * **
        # WITH NO HEADER PASSED AND input_features=None, SHOULD RETURN
        # ['x0', ..., 'x(n-1)][column_mask_]
        # this is controlled by pybear _get_feature_names_out for when
        # a pd dataframe does not have a header
        _PD_GENERIC_HEADER = np.array(
            [f"x{i}" for i in range(_shape[1])],
            dtype=object
        )
        # this controlled by polars. unlike pd, always has a str hdr
        # even if columns is not passed at construction. the pl default
        # is str header, pd default is num.
        _PL_GENERIC_HEADER = np.array(
            [f"column_{i}" for i in range(_shape[1])],
            dtype=object
        )

        # WITH HEADER PASSED TO input_features SHOULD RETURN
        # self.feature_names_in_[column_mask_]
        # self.feature_names_in_ is being passed here to input_features

        if _format == 'np':
            _EXP_HEADER = _columns if _input_features_is_passed else _PD_GENERIC_HEADER
        elif _format == 'pd':
            if _columns_is_passed:
                _EXP_HEADER = _columns
            elif not _columns_is_passed:
                if _input_features_is_passed:
                    _EXP_HEADER = _columns
                else:
                    _EXP_HEADER = _PD_GENERIC_HEADER
        elif _format == 'pl':
            if _columns_is_passed:
                _EXP_HEADER = _columns
            elif not _columns_is_passed:
                _EXP_HEADER = _PL_GENERIC_HEADER
        else:
            raise Exception

        # build column_mask_ - - - - - - - - - - - - - - - - - - - - - -
        MASK = np.ones((_shape[1], ), dtype=bool)
        MASK[_dropped_col_idx] = False
        # END build column_mask_ - - - - - - - - - - - - - - - - - - - -

        _EXP_HEADER = _EXP_HEADER[MASK]
        del MASK
        # END determine expected ** * ** * ** * ** * ** * ** * ** * ** *

        assert isinstance(out, np.ndarray), \
            (f"get_feature_names_out should return numpy.ndarray, but "
             f"returned {type(out)}")

        assert out.dtype == object, \
            (f"get_feature_names_out dtype should be object, but "
             f"returned {out.dtype}")

        if _format == 'np':
            # WHEN NO HEADER PASSED TO (partial_)fit()
            if _input_features_is_passed:
                # SHOULD RETURN SLICED PASSED input_features
                assert np.array_equiv(out, _EXP_HEADER), \
                    (f"get_feature_names_out(_columns) after fit() != "
                     f"sliced array of valid input features")
            if not _input_features_is_passed:
                assert np.array_equiv(out, _EXP_HEADER), \
                    (f"get_feature_names_out(None) after fit() != sliced "
                     f"array of generic headers")
        elif _format in ['pd', 'pl']:
            if _columns_is_passed:
                assert np.array_equiv(out, _EXP_HEADER), \
                    (f"get_feature_names_out(_columns) after fit() != "
                     f"sliced array of feature_names_in_")
            elif not _columns_is_passed:
                if _input_features_is_passed:
                    assert np.array_equiv(out, _EXP_HEADER), \
                        (f"get_feature_names_out(_columns) after fit() != "
                         f"sliced array of valid input features")
                elif not _input_features_is_passed:
                    assert np.array_equiv(out, _EXP_HEADER), \
                        (f"get_feature_names_out(None) after fit() != "
                         f"sliced array of generic headers")
        else:
            raise Exception





