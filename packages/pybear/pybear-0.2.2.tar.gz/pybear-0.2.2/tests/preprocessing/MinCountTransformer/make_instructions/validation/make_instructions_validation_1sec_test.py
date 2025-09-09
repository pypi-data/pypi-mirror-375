# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._MinCountTransformer._make_instructions. \
    _validation._make_instructions_validation import _make_instructions_validation



class TestMakeInstructionsValidation:

    # all the internals of it are validated in other modules, just make
    # sure that it works

    def test_it_works(self):

        TCBC = {0:{0:15,1:20}, 1:{3.14:5, 3.15:15}, 2:{'a':25, 'b':5, 'c':15}}

        _make_instructions_validation(
            _count_threshold=10,
            _ignore_float_columns=True,
            _ignore_non_binary_integer_columns=True,
            _ignore_columns=np.array([], dtype=int),
            _ignore_nan=True,
            _handle_as_bool=np.array([], dtype=int),
            _delete_axis_0=False,
            _original_dtypes=np.array(['int', 'float', 'obj'], dtype='<U5'),
            _n_features_in=3,
            _feature_names_in=np.array(list('abc'), dtype=object),
            _total_counts_by_column=TCBC
        )



