# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy as np

import pytest

from pybear.feature_extraction.text._TextStatistics._partial_fit. \
    _merge_startswith_frequency import _merge_startswith_frequency



class TestMergeStartswithFrequency:

    # all validation is handled by _val_startswith_frequency, which is
    # tested elsewhere

    def test_accuracy(self):

        _wf_1 = {'a': 1, 'b': 2, 'c': 3}

        _wf_2 = {'A': 99, 'b': 1, 'C': 1}

        _wf_3 = {'b': 99, 'o': 99, 't': 99, 'W': 99}


        out1 = _merge_startswith_frequency(_wf_1, _wf_2)
        assert isinstance(out1, dict)
        assert all(map(isinstance, out1.keys(), (str for _ in out1)))
        assert all(map(isinstance, out1.values(), (int for _ in out1)))

        _ref_dict_1 = {'a': 1, 'A': 99, 'b': 3, 'c': 3, 'C': 1}

        assert np.array_equal(
            sorted(list(out1.keys())),
            sorted(list(_ref_dict_1.keys()))
        )

        for k, v in _ref_dict_1.items():

            assert out1[k] == v


        out2 = _merge_startswith_frequency(_wf_3, out1)
        assert isinstance(out2, dict)
        assert all(map(isinstance, out2.keys(), (str for _ in out2)))
        assert all(map(isinstance, out2.values(), (int for _ in out2)))

        _ref_dict_2 = {
            'a': 1, 'A': 99, 'b': 102, 'c': 3, 'C': 1,'o': 99, 't': 99, 'W': 99
        }

        assert np.array_equal(
            sorted(list(out2.keys())),
            sorted(list(_ref_dict_2.keys()))
        )

        for k, v in _ref_dict_2.items():

            assert out1[k] == v








