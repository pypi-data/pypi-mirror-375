# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text._TextStatistics._get._get_shortest_strings \
    import _get_shortest_strings



class TestGetShortestStrings:

    # _val_string_frequency tested elsewhere

    # _val_n tested elsewhere


    def test_empty_string_frequency_returns_empty_dict(self):

        out = _get_shortest_strings({})
        assert isinstance(out, dict)
        assert len(out) == 0


    @pytest.mark.parametrize('n', (1, 2, 3, 7, 10))
    def test_accuracy(self, n):

        FREQ_DICT_1 = {
            'A': 5,
            'BE': 3,
            'CAT': 1,
            'DICK': 1,
            'ENTER': 2,
            'FARTHER': 1,
            'GOOFBALL': 1
        }

        _ref_n = min(n, len(FREQ_DICT_1))
        _mask = np.lexsort((
            list(FREQ_DICT_1.keys()),
            list(map(len, FREQ_DICT_1.keys()))
        ))[:_ref_n]
        _ref_strs = np.array(list(FREQ_DICT_1.keys()))[_mask].tolist()
        _ref_freqs = np.array(list(FREQ_DICT_1.values()))[_mask].tolist()
        del _ref_n, _mask


        out = _get_shortest_strings(FREQ_DICT_1, n)

        assert isinstance(out, dict)
        assert all(map(isinstance, out.keys(), (str for _ in out.keys())))
        assert all(map(isinstance, out.values(), (int for _ in out.values())))

        assert np.array_equal(list(out.keys()), _ref_strs)

        assert np.array_equal(list(out.values()), _ref_freqs)


        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        FREQ_DICT_2 = {
            'FOUR': 1,
            'SCORE': 1,
            'AND': 1,
            'SEVEN': 1,
            'YEARS': 1,
            'AGO': 1
        }

        _ref_n = min(n, len(FREQ_DICT_2))
        _mask = np.lexsort((
            list(FREQ_DICT_2.keys()),
            list(map(len, FREQ_DICT_2.keys()))
        ))[:_ref_n]
        _ref_strs = np.array(list(FREQ_DICT_2.keys()))[_mask].tolist()
        _ref_freqs = np.array(list(FREQ_DICT_2.values()))[_mask].tolist()
        del _ref_n, _mask


        out = _get_shortest_strings(FREQ_DICT_2, n)

        assert isinstance(out, dict)
        assert all(map(isinstance, out.keys(), (str for _ in out.keys())))
        assert all(map(isinstance, out.values(), (int for _ in out.values())))

        assert np.array_equal(list(out.keys()), _ref_strs)

        assert np.array_equal(list(out.values()), _ref_freqs)


        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        FREQ_DICT_3 = {
            'ZOOLOGIST': 1,
            'YELLOW': 2,
            'WHILE': 3,
            'VERY': 4,
            'USE': 5,
            'TO': 6
        }

        _ref_n = min(n, len(FREQ_DICT_3))
        _mask = np.lexsort((
            list(FREQ_DICT_3.keys()),
            list(map(len, FREQ_DICT_3.keys()))
        ))[:_ref_n]
        _ref_strs = np.array(list(FREQ_DICT_3.keys()))[_mask].tolist()
        _ref_freqs = np.array(list(FREQ_DICT_3.values()))[_mask].tolist()
        del _ref_n, _mask


        out = _get_shortest_strings(FREQ_DICT_3, n)

        assert isinstance(out, dict)
        assert all(map(isinstance, out.keys(), (str for _ in out.keys())))
        assert all(map(isinstance, out.values(), (int for _ in out.values())))

        assert np.array_equal(list(out.keys()), _ref_strs)

        assert np.array_equal(list(out.values()), _ref_freqs)




