# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#


import pytest

from copy import deepcopy

from pybear.utilities._check_pipeline import check_pipeline

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression






class TestCheckPipeline:


    @staticmethod
    @pytest.fixture(scope='function')
    def _pipe():

        return Pipeline(
            steps=[
                ('standard_scaler', StandardScaler()),
                ('logistic', LogisticRegression())
            ]
        )


    def test_rejects_pipe_class(self):

        with pytest.raises(ValueError):
            check_pipeline(Pipeline)


    @pytest.mark.parametrize('junk_steps',
        (-1, 0, 1, 3.14, 'junk', None, True, {'a': 1}, min, lambda x: x)
    )
    def test_rejects_junk_steps(self, _pipe, junk_steps):

        with pytest.raises(ValueError):
            _pipe.steps = junk_steps
            check_pipeline(_pipe)


    def test_rejects_bad_pipes(self, _pipe):

        # name not str ** * ** * ** * ** * ** * ** *
        bad_pipe = deepcopy(_pipe)
        bad_pipe.steps[0] = (5, StandardScaler())

        with pytest.raises(ValueError):
            check_pipeline(bad_pipe)

        bad_pipe = deepcopy(_pipe)
        bad_pipe.steps[1] = (True, LogisticRegression())

        with pytest.raises(ValueError):
            check_pipeline(bad_pipe)

        # END name not str ** * ** * ** * ** * ** * ** *

        # step wrong len ** * ** * ** * ** * ** * ** *
        bad_pipe = deepcopy(_pipe)
        bad_pipe.steps[0] = (0, 1, 2, 3, 4)

        with pytest.raises(ValueError):
            check_pipeline(bad_pipe)

        bad_pipe = deepcopy(_pipe)
        bad_pipe.steps[1] = (3,)

        with pytest.raises(ValueError):
            check_pipeline(bad_pipe)

        bad_pipe = deepcopy(_pipe)
        bad_pipe.steps[1] = [0]

        with pytest.raises(ValueError):
            check_pipeline(bad_pipe)

        # END step wrong len ** * ** * ** * ** * ** * ** *


        # not instance ** * ** * ** * ** * ** * ** * ** *
        bad_pipe = deepcopy(_pipe)
        bad_pipe.steps[0] = ('standard_scaler', StandardScaler)

        with pytest.raises(ValueError):
            check_pipeline(bad_pipe)

        bad_pipe = deepcopy(_pipe)
        bad_pipe.steps[1] = ('logistic', LogisticRegression)

        with pytest.raises(ValueError):
            check_pipeline(bad_pipe)

        # END not instance ** * ** * ** * ** * ** * ** * ** *


    def test_accepts_good_pipe(self, _pipe):

        assert check_pipeline(_pipe) is None




