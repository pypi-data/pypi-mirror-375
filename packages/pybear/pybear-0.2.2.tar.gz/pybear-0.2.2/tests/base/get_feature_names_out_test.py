# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.base._get_feature_names_out import get_feature_names_out

import uuid

import numpy as np

import pytest



class TestGetXFeatureNamesOut:


    @staticmethod
    @pytest.fixture(scope='module')
    def _n_features_in():
        return 10


    @staticmethod
    @pytest.fixture(scope='module')
    def _feature_names_in(_master_columns, _n_features_in):
        return _master_columns.copy()[:_n_features_in]


    @staticmethod
    @pytest.fixture(scope='module')
    def _input_features(_feature_names_in):
        return _feature_names_in


    @pytest.mark.parametrize('junk_input_features',
        (float('-inf'), np.pi, True, False, 'garbage', {'junk': 3},
         list(range(10)), lambda x: x)
    )
    def test_rejects_junk(
        self, junk_input_features, _input_features, _feature_names_in,
        _n_features_in
    ):

        # _input_features
        with pytest.raises(ValueError):
            get_feature_names_out(
                junk_input_features,
                _feature_names_in,
                _n_features_in,
            )

        # feature_names_in_
        with pytest.raises(AssertionError):
            get_feature_names_out(
                _input_features,
                junk_input_features,
                _n_features_in,
            )

        # n_features_in_
        with pytest.raises(AssertionError):
            get_feature_names_out(
                _input_features,
                _feature_names_in,
                junk_input_features,
            )


    def test_input_features_conflicts(
        self, _input_features, _feature_names_in, _n_features_in
    ):

        # test input_features bad len vs _n_features_in (too short)
        with pytest.raises(ValueError):
            get_feature_names_out(
                input_features=_feature_names_in,
                feature_names_in_= \
                    np.hstack((_feature_names_in, _feature_names_in)),
                n_features_in_=_n_features_in*2
            )


        # test input_features bad len vs _n_features_in (too long)
        with pytest.raises(ValueError):
            get_feature_names_out(
                input_features=_feature_names_in,
                feature_names_in_=_feature_names_in[:_n_features_in//2],
                n_features_in_=_n_features_in//2,
            )


        # test input_features != feature_names_in_ (len too short)
        with pytest.raises(ValueError):
            get_feature_names_out(
                input_features=_feature_names_in[:len(_feature_names_in)//2],
                feature_names_in_=_feature_names_in,
                n_features_in_=_n_features_in,
            )


        # test input_features != feature_names_in_ (different names)
        with pytest.raises(ValueError):
            get_feature_names_out(
                input_features=[
                    str(uuid.uuid4())[:5] for _ in range(_n_features_in)
                ],
                feature_names_in_=_feature_names_in,
                n_features_in_=_n_features_in,
            )


    @pytest.mark.parametrize(
        '_input_features_is_passed, _feature_names_in_is_passed',
        ((True, True), (True, False), (False, True), (False, False))
    )
    def test_accuracy(
        self, _input_features_is_passed, _feature_names_in_is_passed,
        _input_features, _feature_names_in, _n_features_in
    ):


        if _input_features_is_passed and _feature_names_in_is_passed:
            out = get_feature_names_out(
                input_features=_input_features,
                feature_names_in_=_feature_names_in,
                n_features_in_=_n_features_in,
            )
            assert np.array_equiv(out, _input_features)
            assert np.array_equiv(out, _feature_names_in)

        elif _input_features_is_passed and not _feature_names_in_is_passed:

            _input_features = \
                [str(uuid.uuid4())[:5] for i in range(_n_features_in)]

            out = get_feature_names_out(
                input_features=_input_features,
                feature_names_in_=None,
                n_features_in_=_n_features_in,
            )
            assert np.array_equiv(out, _input_features)

        elif not _input_features_is_passed and _feature_names_in_is_passed:
            out = get_feature_names_out(
                input_features=None,
                feature_names_in_=_feature_names_in,
                n_features_in_=_n_features_in,
            )
            assert np.array_equiv(out, _feature_names_in)

        elif not _input_features_is_passed and not _feature_names_in_is_passed:
            out = get_feature_names_out(
                input_features=None,
                feature_names_in_=None,
                n_features_in_=_n_features_in,
            )
            assert np.array_equiv(out, [f"x{i}" for i in range(_n_features_in)])

        else:
            raise Exception()


        assert isinstance(out, np.ndarray), \
            (f"get_feature_names_out should return numpy.ndarray, but "
             f"returned {type(out)}")

        assert out.dtype == object, \
            (f"get_feature_names_out dtype should be object, but "
             f"returned {out.dtype}")








