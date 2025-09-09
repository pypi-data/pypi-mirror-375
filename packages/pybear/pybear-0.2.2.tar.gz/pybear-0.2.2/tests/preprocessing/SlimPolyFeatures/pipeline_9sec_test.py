# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

from pybear.preprocessing import SlimPolyFeatures as SlimPoly
from pybear.utilities import check_pipeline



class TestPipeline:


    def test_accuracy_in_pipe_vs_out_of_pipe(
        self, X_np, _shape, _kwargs, y_np
    ):

        # this also incidentally tests functionality in a pipe

        # make a pipe of StandardScaler, SlimPoly, and LinearRegression
        # fit the data on the pipeline, get coef_
        # fit the data on the steps severally, compare coef_

        # pipe ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        pipe = Pipeline(
            steps = [
                ('onehot', StandardScaler(with_std=True, with_mean=True)),
                ('SlimPoly', SlimPoly(**_kwargs)),
                ('MLR', LinearRegression(fit_intercept = True, n_jobs = 1))
            ]
        )

        check_pipeline(pipe)

        pipe.fit(X_np, y_np)

        _coef_pipe = pipe.steps[2][1].coef_

        # END pipe ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


        # separate ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        encoded_X = StandardScaler(with_std=True, with_mean=True).fit_transform(X_np)
        slim_X = SlimPoly(**_kwargs).fit_transform(encoded_X)
        # prove out that SPF is actually doing something
        assert 0 < slim_X.shape[0] == encoded_X.shape[0]
        assert 0 < encoded_X.shape[1] < slim_X.shape[1]
        # END prove out that SPF is actually doing something
        _coef_separate = LinearRegression().fit(slim_X, y_np).coef_

        # END separate ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        assert np.allclose(_coef_pipe, _coef_separate)





