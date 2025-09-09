# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression

from pybear.preprocessing import InterceptManager as IM
from pybear.utilities import check_pipeline



class TestPipeline:


    def test_accuracy_in_pipe_vs_out_of_pipe(
        self, X_np, _shape, _kwargs, y_np
    ):

        # this also incidentally tests functionality in a pipe

        # make a pipe of OneHotEncoder, IM, and LinearRegression
        # fit the data on the pipeline, get coef_
        # fit the data on the steps severally, compare coef_

        # pipe ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        pipe = Pipeline(
            steps = [
                ('onehot', OneHotEncoder()),
                ('IM', IM(**_kwargs)),
                ('MLR', LogisticRegression())
            ]
        )

        check_pipeline(pipe)

        pipe.fit(X_np, y_np)

        _coef_pipe = pipe.steps[2][1].coef_

        # END pipe ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


        # separate ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        encoded_X = OneHotEncoder().fit_transform(X_np)
        deconstanted_X = IM(**_kwargs).fit_transform(encoded_X)
        # prove out that IM is actually doing something
        assert 0 < deconstanted_X.shape[0] == encoded_X.shape[0]
        assert deconstanted_X.shape[1] < encoded_X.shape[1]
        # END prove out that IM is actually doing something
        _coef_separate = LogisticRegression().fit(deconstanted_X, y_np).coef_

        # END separate ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        assert np.allclose(_coef_pipe, _coef_separate)





