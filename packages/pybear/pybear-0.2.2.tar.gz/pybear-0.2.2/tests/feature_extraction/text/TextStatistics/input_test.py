# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.feature_extraction.text._TextStatistics.TextStatistics import \
    TextStatistics




class TestTextStatisticsInputs:


    def test_rejects_numeric(self, X_np):


        with pytest.raises(TypeError):
            TextStatistics().fit(X_np)


        _X = [['I', 'like', 'green'], ['eggs', 'and', 13]]
        with pytest.raises(TypeError):
            TextStatistics().fit(_X)


    def test_weird_characters(self):

        TS = TextStatistics(store_uniques=True)

        X = ['\n', '\t', '\r']
        TS.partial_fit(X)

        assert TS.character_frequency_ == {'\t': 1, '\n': 1, '\r': 1}


    def test_1D_inputs(self):

        _X = ['Say!', 'I', 'like', 'green', 'eggs', 'and', 'ham!']

        TS = TextStatistics(store_uniques=True)

        _counter = 0

        TS.partial_fit(list(_X))
        _counter += 1
        assert TS.string_frequency_['green'] == _counter

        TS.partial_fit(set(_X))
        _counter += 1
        assert TS.string_frequency_['green'] == _counter

        TS.partial_fit(tuple(_X))
        _counter += 1
        assert TS.string_frequency_['green'] == _counter

        TS.partial_fit(np.array(_X))
        _counter += 1
        assert TS.string_frequency_['green'] == _counter

        TS.partial_fit(pd.Series(_X))
        _counter += 1
        assert TS.string_frequency_['green'] == _counter

        TS.partial_fit(pl.Series(_X))
        _counter += 1
        assert TS.string_frequency_['green'] == _counter


    def test_2D_inputs(self):

        _2D_X = [['I', 'like', 'green'], ['eggs', 'and', 'ham!']]

        TS = TextStatistics(store_uniques=True)

        _counter = 0

        TS.partial_fit(list(_2D_X))
        _counter += 1
        assert TS.string_frequency_['green'] == _counter

        TS.partial_fit(np.array(_2D_X))
        _counter += 1
        assert TS.string_frequency_['green'] == _counter

        TS.partial_fit(pd.DataFrame(_2D_X))
        _counter += 1
        assert TS.string_frequency_['green'] == _counter

        TS.partial_fit(pl.from_numpy(np.array(_2D_X)))
        _counter += 1
        assert TS.string_frequency_['green'] == _counter





