# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.base._check_n_features import check_n_features

import uuid

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

import pytest



class TestCheckNFeaturesIn:


    # def check_n_features(
    #     X,
    #     n_features_in_: int | None,
    #     reset: bool
    # ) -> int:

    # reset:
    #     bool -
    #     If True, the 'n_features_in_' attribute is set to 'X.shape[1]'
    #     If False:
    #         if n_features_in_ exists check it is equal to 'X.shape[1]'
    #         if n_features_in_ does not exist the check is skipped and
    #             n_features_in_ is not set


    @pytest.mark.parametrize('X_format', ('np', 'pd', 'pl', 'csc'))
    @pytest.mark.parametrize('X_shape',
        ((10, 5), (13, 8), (4, 25), (17, 17), (55, ))
    )
    @pytest.mark.parametrize('n_features_in_', (1, 4, 7, 10, 13, 17, 22, None))
    @pytest.mark.parametrize('_reset',  (True, False))
    def test_check_n_features(self, X_format, X_shape, n_features_in_, _reset):

        # skip impossible conditions - - - - - - - - - - - - - - - - - -
        if X_format == 'csc' and len(X_shape) != 2:
            pytest.skip(reason=f"scipy ss can only be 2D")
        # END skip impossible conditions - - - - - - - - - - - - - - - -

        _base_X = np.random.randint(0, 10, X_shape)

        if len(X_shape) == 1:
            _columns = ['y']
        else:
            _columns = [str(uuid.uuid4())[:8] for _ in range(X_shape[1])]

        if X_format == 'np':
            _X = _base_X.copy()
        elif X_format == 'pd':
            _X = pd.DataFrame(data=_base_X, columns=_columns)
        elif X_format == 'pl':
            _X = pl.from_numpy(_base_X, schema=list(_columns))
        elif X_format == 'csc':
            _X = ss.csc_array(_base_X)
        else:
            raise Exception

        if _reset is True:
            # when reset is True, doesnt matter what n_features_in_ was
            # previously, n_features_in_ is set to whatever is in the X
            # that it is currently seeing
            out = check_n_features(
                _X,
                n_features_in_,
                _reset
            )

            if len(X_shape) == 1:
                assert out == 1
            else:
                assert out == _X.shape[1]

        elif _reset is False:

            if n_features_in_ is None:

                # this basically a no-op, just returns None
                out = check_n_features(
                    _X,
                    n_features_in_,
                    _reset
                )

                assert out is None

            elif n_features_in_ is not None:

                if len(X_shape) == 1:
                    if n_features_in_ == 1:
                        out = check_n_features(
                            _X,
                            n_features_in_,
                            _reset
                        )

                        assert out == n_features_in_ == 1
                    else:
                        with pytest.raises(ValueError):
                            check_n_features(
                                _X,
                                n_features_in_,
                                _reset
                            )

                # otherwise, X_shape must be 2D
                elif n_features_in_ == X_shape[1]:
                    out = check_n_features(
                        _X,
                        n_features_in_,
                        _reset
                    )

                    assert out == n_features_in_ == X_shape[1]

                # X_shape still must be 2D
                elif n_features_in_ != X_shape[1]:
                    # new data has different num columns than previously
                    with pytest.raises(ValueError):
                        check_n_features(
                            _X,
                            n_features_in_,
                            _reset
                        )




