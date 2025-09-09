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

from pybear.preprocessing import ColumnDeduplicator as CDT
from pybear.utilities import check_pipeline



class TestPipeline:


    def test_accuracy_in_pipe_vs_out_of_pipe(
        self, X_np, _shape, _kwargs, y_np
    ):

        # this also incidentally tests functionality in a pipe

        # make a pipe of OneHotEncoder, CDT, and LogisticRegression
        # fit the data on the pipeline, get coef_
        # fit the data on the steps severally, compare coef_

        # pipe ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        # n_jobs confliction doesnt seem to matter
        pipe = Pipeline(
            steps = [
                ('onehot', OneHotEncoder()),
                ('cdt', CDT(**_kwargs)),
                ('MLR', LogisticRegression())
            ]
        )

        check_pipeline(pipe)

        pipe.fit(X_np, y_np)

        _coef_pipe = pipe.steps[2][1].coef_

        # END pipe ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


        # separate ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        encoded_X = OneHotEncoder().fit_transform(X_np)
        deduplicated_X = CDT(**_kwargs).fit_transform(encoded_X)
        # prove out that CDT is actually doing something
        assert 0 < deduplicated_X.shape[0] == encoded_X.shape[0]
        assert 0 < deduplicated_X.shape[1] < encoded_X.shape[1]
        # END prove out that CDT is actually doing something
        _coef_separate = LogisticRegression().fit(deduplicated_X, y_np).coef_

        # END separate ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        assert np.allclose(_coef_pipe, _coef_separate)





