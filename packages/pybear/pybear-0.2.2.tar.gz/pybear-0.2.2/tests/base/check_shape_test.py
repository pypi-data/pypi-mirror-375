# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

from pybear.base._check_shape import check_shape



class TestCheckShape:


    # the validation at the top of check_shape is not tested here.
    # it is tested in _validate_data_test.

    @pytest.mark.parametrize('X_format', ('np', 'pd', 'pl', 'coo'))
    @pytest.mark.parametrize('dimensionality', (1, 2, 3, 4, 5))
    @pytest.mark.parametrize('allowed_dimensionality', ((1,), (2,), (1,2)))
    def test_rejects_disallowed_dimensionality(
        self, X_format, dimensionality, allowed_dimensionality
    ):

        # skip impossible conditions - - - - - - - - - - - - - - - - - -

        if X_format == 'coo' and dimensionality != 2:
            pytest.skip(reason=f"scipy sparse can only be 2D")

        if X_format in ['pd', 'pl'] and dimensionality > 2:
            pytest.skip(reason=f"pd/pl dataframe must be 1 or 2D")

        # END skip impossible conditions - - - - - - - - - - - - - - - -

        # create the shape tuple
        _shape = tuple(np.random.randint(2, 10, dimensionality).tolist())

        _base_X = np.random.randint(0, 10, _shape)

        if X_format == 'np':
            _X = _base_X
        elif X_format == 'pd':
            _X = pd.DataFrame(data=_base_X)
            if dimensionality == 1:
                _X = _X.iloc[:, 0].squeeze()
        elif X_format == 'pl':
            _X = pl.from_numpy(_base_X)
            if dimensionality == 1:
                _X = _X[:, 0]
        elif X_format == 'coo':
            _X = ss.coo_array(_base_X)
        else:
            raise Exception

        if dimensionality in allowed_dimensionality:
            out = check_shape(
                _X,
                allowed_dimensionality=allowed_dimensionality
            )

            assert out == _shape

        elif dimensionality not in allowed_dimensionality:
            with pytest.raises(ValueError):
                check_shape(
                    _X,
                    allowed_dimensionality=allowed_dimensionality
                )


    @pytest.mark.parametrize('X_format', ('np', 'pd', 'pl', 'dok'))
    @pytest.mark.parametrize('dimensionality', (1, 2))
    @pytest.mark.parametrize('features', (0, 1, 2, 100))
    @pytest.mark.parametrize('min_features', (0, 1, 2))
    def test_rejects_too_few_features(
        self, X_format, dimensionality, features, min_features
    ):

        # skip impossible conditions - - - - - - - - - - - - - - - - - -

        if dimensionality == 1 and features != 1:
            pytest.skip(reason=f"impossible condition")

        if X_format == 'dok' and features != 2:
            pytest.skip(reason=f"scipy sparse must be 2D")

        if X_format == 'pl' and features < 1:
            # zero feature polars also sets row dim to zero, even if
            # passed empty X has dim on axis 0
            pytest.skip(reason=f"cant have zero feature polars")

        # END skip impossible conditions - - - - - - - - - - - - - - - -

        _n_samples = 100

        if dimensionality == 1:
            # features == 1
            _shape = (_n_samples, )
            _base_X = np.random.randint(0, 10, _shape)
        elif dimensionality == 2:
            _shape = (_n_samples, features)
            _base_X = np.random.randint(0, 10, _shape)

        if X_format == 'np':
            _X = _base_X
        elif X_format == 'pd':
            _X = pd.DataFrame(data=_base_X)
            if dimensionality == 1:
                _X = _X.squeeze()
        elif X_format == 'pl':
            _X = pl.from_numpy(_base_X)
            if dimensionality == 1:
                _X = _X[:, 0]
        elif X_format == 'dok':
            _X = ss.dok_array(_base_X)
        else:
            raise Exception

        assert _X.shape[0] == _n_samples
        if dimensionality > 1:
            assert _X.shape[1] == features

        if features >= min_features:
            out = check_shape(
                _X,
                min_features=min_features
            )

            assert out == _shape

        elif features < min_features:
            with pytest.raises(ValueError):
                check_shape(
                    _X,
                    min_features=min_features
                )


    @pytest.mark.parametrize('X_format', ('np', 'pd', 'pl', 'dok'))
    @pytest.mark.parametrize('dimensionality', (1, 2))
    @pytest.mark.parametrize('features', (0, 1, 20, 100))
    @pytest.mark.parametrize('min_features', (0, 1, 2))
    @pytest.mark.parametrize('max_features', (1, 2, None))
    def test_rejects_too_many_features(
        self, X_format, dimensionality, features, min_features, max_features
    ):

        # also tests that max_features must be >= min features

        # skip impossible conditions - - - - - - - - - - - - - - - - - -

        if dimensionality == 1 and features != 1:
            pytest.skip(reason=f"impossible condition")

        if X_format == 'dok' and features != 2:
            pytest.skip(reason=f"scipy sparse must be 2D")

        if X_format == 'pl' and features < 1:
            # zero feature polars also sets row dim to zero, even if
            # passed empty X has dim on axis 0
            pytest.skip(reason=f"cant have zero feature polars")

        # END skip impossible conditions - - - - - - - - - - - - - - - -

        _n_samples = 100

        if dimensionality == 1:
            # features == 1
            _shape = (_n_samples, )
        elif dimensionality == 2:
            _shape = (_n_samples, features)

        _base_X = np.random.randint(0, 10, _shape)

        if X_format == 'np':
            _X = _base_X
        elif X_format == 'pd':
            _X = pd.DataFrame(data=_base_X)
            if dimensionality == 1:
                _X = _X.squeeze()
        elif X_format == 'pl':
            _X = pl.from_numpy(_base_X)
            if dimensionality == 1:
                _X = _X[:, 0]
        elif X_format == 'dok':
            _X = ss.dok_array(_base_X)
        else:
            raise Exception

        assert _X.shape[0] == _n_samples
        if dimensionality > 1:
            assert _X.shape[1] == features

        if max_features and max_features < min_features:
            # raise fo max_features < min_features
            with pytest.raises(ValueError):
                check_shape(
                    _X,
                    min_features=min_features,
                    max_features=max_features
                )
            pytest.skip(reason=f"cant do more tests after exception")


        if features >= min_features:

            if max_features is None:
                # no max limit on number of features
                out = check_shape(
                    _X,
                    min_features=min_features,
                    max_features=max_features
                )
                assert out == _shape
            elif features <= max_features:  # max_features is not None
                # this is OK
                out = check_shape(
                    _X,
                    min_features=min_features,
                    max_features=max_features
                )
                assert out == _shape
            elif features > max_features:   # max_features is not None
                # too many feature
                with pytest.raises(ValueError):
                    check_shape(
                        _X,
                        min_features=min_features,
                        max_features=max_features
                    )
            else:
                raise Exception

        elif features < min_features:
            with pytest.raises(ValueError):
                check_shape(
                    _X,
                    min_features=min_features,
                    max_features=max_features
                )


    @pytest.mark.parametrize('X_format', ('np', 'pd', 'pl', 'dok'))
    @pytest.mark.parametrize('dimensionality', (1, 2))
    @pytest.mark.parametrize('samples', (10, 20, 100))
    @pytest.mark.parametrize('sample_check', (5, 10, 20, None))
    def test_rejects_wrong_number_of_samples(
        self, X_format, dimensionality, samples, sample_check
    ):

        # this is handled by the 'sample_check' machinery

        # skip impossible conditions - - - - - - - - - - - - - - - - - -
        if X_format == 'dok' and dimensionality != 2:
            pytest.skip(reason=f"scipy sparse must be 2D")
        if X_format == 'pd' and dimensionality == 1 and samples == 1:
            pytest.skip(reason=f"1x1 pandas squeezes to a number.")
        # END skip impossible conditions - - - - - - - - - - - - - - - -


        if dimensionality == 1:
            _shape = (samples,)
            _base_X = np.random.randint(0, 10, _shape)
        elif dimensionality == 2:
            _shape = (samples, 5)
            _base_X = np.random.randint(0, 10, _shape)

        if X_format == 'np':
            _X = _base_X
        elif X_format == 'pd':
            _X = pd.DataFrame(data=_base_X)
            if dimensionality == 1:
                _X = _X.squeeze()
        elif X_format == 'pl':
            _X = pl.from_numpy(_base_X)
            if dimensionality == 1:
                _X = _X[:, 0]
        elif X_format == 'dok':
            _X = ss.dok_array(_base_X)
        else:
            raise Exception

        if dimensionality == 1:
            assert len(_X.shape) == 1
            assert _X.shape[0] == samples
        elif dimensionality == 2:
            assert len(_X.shape) == 2
            assert _X.shape[0] == samples
            assert _X.shape[1] == 5
        else:
            raise Exception

        if sample_check is None:
            # this is OK, samples not checked for exact count
            out = check_shape(
                _X,
                min_samples=0,
                sample_check=sample_check
            )

            assert out == _shape

        elif samples == sample_check:  # sample_check is not None
            out = check_shape(
                _X,
                min_samples=0,
                sample_check=sample_check
            )

            assert out == _shape

        elif samples != sample_check:   # sample_check is not None
            # fails the check
            with pytest.raises(ValueError):
                check_shape(
                    _X,
                    min_samples=0,
                    sample_check=sample_check
                )


    @pytest.mark.parametrize('X_format', ('np', 'pd', 'pl', 'lil'))
    @pytest.mark.parametrize('dimensionality', (1, 2))
    @pytest.mark.parametrize('samples', (0, 1, 2, 100))
    @pytest.mark.parametrize('min_samples', (0, 1, 2))
    def test_rejects_too_few_samples(
        self, X_format, dimensionality, samples, min_samples
    ):

        # this is handled by the 'min_samples' machinery

        # skip impossible conditions - - - - - - - - - - - - - - - - - -
        if X_format == 'lil' and dimensionality != 2:
            pytest.skip(reason=f"scipy sparse must be 2D")
        if X_format == 'pd' and dimensionality == 1 and samples == 1:
            pytest.skip(reason=f"1x1 pandas squeezes to a number.")
        if X_format == 'pl' and dimensionality == 1 and samples == 0:
            # empty polars vector to df sets col dim to zero
            pytest.skip(reason=f"cant have zero feature polars")
        # END skip impossible conditions - - - - - - - - - - - - - - - -


        if dimensionality == 1:
            _shape = (samples,)
            _base_X = np.random.randint(0, 10, _shape)
        elif dimensionality == 2:
            _shape = (samples, 5)
            _base_X = np.random.randint(0, 10, _shape)

        if X_format == 'np':
            _X = _base_X
        elif X_format == 'pd':
            _X = pd.DataFrame(data=_base_X)
            if dimensionality == 1:
                _X = _X.iloc[:, 0].squeeze()
        elif X_format == 'pl':
            _X = pl.from_numpy(_base_X)
            if dimensionality == 1:
                _X = _X[:, 0]
        elif X_format == 'lil':
            _X = ss.lil_array(_base_X)
        else:
            raise Exception

        if dimensionality == 1:
            assert len(_X.shape) == 1
            assert _X.shape[0] == samples
        elif dimensionality == 2:
            assert len(_X.shape) == 2
            assert _X.shape[0] == samples
            assert _X.shape[1] == 5
        else:
            raise Exception

        if samples >= min_samples:
            out = check_shape(
                _X,
                min_samples=min_samples
            )

            assert out == _shape

        elif samples < min_samples:
            with pytest.raises(ValueError):
                check_shape(
                    _X,
                    min_samples=min_samples
                )




