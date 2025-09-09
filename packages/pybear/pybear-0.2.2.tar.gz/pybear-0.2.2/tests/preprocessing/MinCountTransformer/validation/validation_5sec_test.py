# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._MinCountTransformer._validation._validation \
    import _validation



class TestMCTValidation:

    # all the internals of it are validated in other modules, just make
    # sure that it works

    def test_it_works(self):


        _validation(
            _X=np.random.randint(0, 10, (10, 10)),
            _count_threshold=10,
            _ignore_float_columns=True,
            _ignore_non_binary_integer_columns=True,
            _ignore_nan=True,
            _delete_axis_0=False,
            _ignore_columns=None,
            _handle_as_bool=None,
            _reject_unseen_values=True,
            _max_recursions=2,
            _n_features_in=10,
            _feature_names_in=None,
        )


        _validation(
            _X=np.random.randint(0, 10, (10, 10)),
            _count_threshold=[2 for i in range(10)],
            _ignore_float_columns=False,
            _ignore_non_binary_integer_columns=False,
            _ignore_nan=False,
            _delete_axis_0=True,
            _ignore_columns=[0, 2, 4],
            _handle_as_bool=['f', 'g', 'h'],
            _reject_unseen_values=False,
            _max_recursions=1,
            _n_features_in=10,
            _feature_names_in=np.array(list('abcdefghij'))
        )







