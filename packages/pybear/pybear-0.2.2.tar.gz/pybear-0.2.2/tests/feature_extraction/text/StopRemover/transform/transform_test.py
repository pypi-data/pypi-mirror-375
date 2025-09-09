# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text._StopRemover._transform._transform import \
    _transform



class TestTransform:


    @staticmethod
    @pytest.fixture(scope='module')
    def _stop_words():
        return ['A', 'AND', 'AT', 'IN', 'IS', 'IT', 'OF', 'ON', 'THE', 'TO']


    @staticmethod
    @pytest.fixture(scope='module')
    def _text():

        return [
            ["Is","this", "the", "real", "life?"],
            ["Is", "this", "just", "fantasy?"],
            ["Caught", "in", "a", "landside"],
            ["No", "escape", "from", "reality"],
            ["Open", "your", "eyes"],
            ["Look", "up", "to", "the", "skies", "and", "see"],
            ["A", "Is", "aNd"]
        ]

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    def test_accuracy_remove_empty_rows(self, _text, _stop_words):

        out_data, out_support_mask = _transform(
            _text,
            lambda x, y: x.upper() == y.upper(),
            _stop_words,
            _remove_empty_rows = True,
            _n_jobs=1
        )

        assert isinstance(out_data, list)
        for row in out_data:
            assert isinstance(row, list)
            assert all(map(isinstance, row, (str for _ in row)))

        _exp_1 = [
            ["this", "real", "life?"],
            ["this", "just", "fantasy?"],
            ["Caught", "landside"],
            ["No", "escape", "from", "reality"],
            ["Open", "your", "eyes"],
            ["Look", "up", "skies", "see"]
        ]

        assert all(map(np.array_equal, out_data, _exp_1))

        assert np.array_equal(out_support_mask, [True] * 6 + [False])


    def test_accuracy_do_not_remove_empty_rows(self, _text, _stop_words):

        out_data, out_support_mask = _transform(
            _text,
            lambda x, y: x.upper() == y.upper(),
            _stop_words,
            _remove_empty_rows = False,
            _n_jobs=1
        )

        assert isinstance(out_data, list)
        for row in out_data:
            assert isinstance(row, list)
            assert all(map(isinstance, row, (str for _ in row)))

        _exp_2 = [
            ["this", "real", "life?"],
            ["this", "just", "fantasy?"],
            ["Caught", "landside"],
            ["No", "escape", "from", "reality"],
            ["Open", "your", "eyes"],
            ["Look", "up", "skies", "see"],
            []
        ]

        assert all(map(np.array_equal, out_data, _exp_2))

        assert np.array_equal(out_support_mask, [True] * 7)



