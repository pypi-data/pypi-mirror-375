# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.feature_extraction.text._TextJoiner._validation._validation import \
    _validation



class TestValidation:

    # the brunt of the test is handled by the individual modules. just
    # test that this accepts and passes good parameters.


    @pytest.mark.parametrize('_X_format',
        ('list_of_lists', 'tuple_of_tuples', 'np', 'pd', 'pl')
    )
    @pytest.mark.parametrize('_sep', (-2, 2.7, True, [0,1], ' ', '', 'help'))
    def test_passes_good(self, _X_format, _sep):


        _np_base = np.random.choice(list('abcdefg'), (37, 13), replace=True)

        if _X_format == 'list_of_lists':
            _X_wip = list(map(list, _np_base))
        elif _X_format == 'tuple_of_tuples':
            _X_wip = tuple(map(tuple, _np_base))
        elif _X_format == 'np':
            _X_wip = _np_base.copy()
        elif _X_format == 'pd':
            _X_wip = pd.DataFrame(_np_base)
        elif _X_format == 'pl':
            _X_wip = pl.from_numpy(_np_base)
        else:
            raise Exception


        if isinstance(_sep, str):
            assert _validation(_X_wip, _sep) is None
        else:
            with pytest.raises(TypeError):
                _validation(_X_wip, _sep)






