# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from pybear.preprocessing import MinCountTransformer as MCT
from pybear.preprocessing import ColumnDeduplicator as CDT
from pybear.utilities import check_pipeline



# DO THIS WITHOUT ALTERING THE 0 AXIS, ALTER AXIS 1 ONLY
# CANT PASS Y TO THE PIPE, MCT WILL RETURN IT, SO THIS PRECLUDES USING
# AN ESTIMATOR THAT NEEDS Y. DO TWO TRANSFORMERS WITH OneHotEncoder.


class TestPipeline:


    def test_accuracy_in_pipe_vs_out_of_pipe(
        self, _X_factory, _shape, _kwargs
    ):

        # this also incidentally tests functionality in a pipe

        # make a pipe of MCT, OneHotEncoder, & CDT
        # fit the data on the pipeline and transform, get output
        # fit the data on the steps severally and transform, compare output

        # need some columns that wont be row-chopped and some
        # columns of constants that will be chopped
        _X_np = _X_factory(
            _format='np',
            _dtype='int',
            _columns=None,
            _dupl=None,
            _constants={k: 1 for k in range(_shape[1]) if k%2==0},
            _shape=_shape
        )


        # pipe ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        # dont use OHE sparse_output, that only puts out CSR.
        pipe = Pipeline(
            steps = [
                ('mct', MCT(**_kwargs)),
                ('onehot', OneHotEncoder()),
                ('cdt', CDT(keep='first', equal_nan=True))
            ]
        )

        check_pipeline(pipe)

        pipe.fit(_X_np)

        TRFM_X_PIPE = pipe.transform(_X_np)

        # END pipe ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


        # separate ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

        _chopped_X = MCT(**_kwargs).fit_transform(_X_np)
        assert isinstance(_chopped_X, type(_X_np))
        # prove out that MCT is actually doing something
        assert 0 < _chopped_X.shape[0] <= _X_np.shape[0]
        assert 0 < _chopped_X.shape[1] < _X_np.shape[1]
        # END prove out that MCT is actually doing something
        _ohe_X = OneHotEncoder().fit_transform(_chopped_X)
        TRFM_X_NOT_PIPE = CDT(keep='first', equal_nan=True).fit_transform(_ohe_X)


        # END separate ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # this is here because we need to manage for the different revs
        # of OHE that do/dont have a 'sparse_output' param.
        if hasattr(TRFM_X_PIPE, 'toarray'):
            TRFM_X_PIPE = TRFM_X_PIPE.toarray()

        if hasattr(TRFM_X_NOT_PIPE, 'toarray'):
            TRFM_X_NOT_PIPE = TRFM_X_NOT_PIPE.toarray()

        assert np.array_equal(TRFM_X_PIPE, TRFM_X_NOT_PIPE, equal_nan=True)





