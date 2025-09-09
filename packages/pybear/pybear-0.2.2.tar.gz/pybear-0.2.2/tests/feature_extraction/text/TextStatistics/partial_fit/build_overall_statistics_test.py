# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy as np

import pytest

from pybear.feature_extraction.text._TextStatistics._partial_fit. \
    _build_overall_statistics import _build_overall_statistics





class TestBuildCurrentOverallStatistics:

    # def _build_overall_statistics(
    #    STRINGS: Sequence[str]
    # ) -> OverallStatisticsType:


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @pytest.mark.parametrize('junk_STRINGS',
        (-2.7, -1, 0, 1, 2.7, True, False, None, 'junk', [1,2], (1,), {1,2},
         {'a': 1}, np.random.randint(0, 10, (10,)), lambda x: x)
    )
    def test_STRINGS_rejects_non_list_like(self, junk_STRINGS):

        with pytest.raises(TypeError):
            _build_overall_statistics(
                junk_STRINGS,
                case_sensitive=True
            )


    @pytest.mark.parametrize('junk_case_sensitive',
        (-2.7, -1, 0, 1, 2.7, None, 'junk', [1,2], (1,), {1,2},
         {'a': 1}, np.random.randint(0, 10, (10,)), lambda x: x)
    )
    def test_case_sensitive_rejects_non_bool(self, junk_case_sensitive):

        with pytest.raises(TypeError):
            _build_overall_statistics(
                ['Do', 'You', 'Like', 'Green', 'Eggs', 'And', 'Ham'],
                junk_case_sensitive
            )


    @pytest.mark.parametrize('case_sensitive', (True, False))
    def test_accepts_good(self, case_sensitive):

        _build_overall_statistics(
            ['THAT', 'SAM-I-AM', 'THAT', 'SAM-I-AM', 'I', 'DO',
             'NOT', 'LIKE', 'THAT' 'SAM-I-AM'],
            case_sensitive=case_sensitive
        )

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    def test_accuracy(self):

        STRINGS = ['I', 'Am', 'Sam', 'I', 'AM', 'SAM', 'sam', 'i', 'am']

        # case_sensitive False -- -- -- -- -- -- -- -- -- -- -- -- -- --
        out = _build_overall_statistics(STRINGS, case_sensitive=False)

        assert isinstance(out, dict)

        assert 'size' in out
        assert isinstance(out['size'], int)
        assert out['size'] == 9

        assert 'uniques_count' in out
        assert isinstance(out['uniques_count'], int)
        assert out['uniques_count'] == 3

        assert 'average_length' in out
        assert isinstance(out['average_length'], float)
        assert out['average_length'] == (sum(map(len, STRINGS)) / len(STRINGS))

        assert 'std_length' in out
        assert isinstance(out['std_length'], float)
        assert out['std_length'] == float(np.std(list(map(len, STRINGS))))

        assert 'max_length' in out
        assert isinstance(out['max_length'], int)
        assert out['max_length'] == max(map(len, STRINGS))

        assert 'min_length' in out
        assert isinstance(out['min_length'], int)
        assert out['min_length'] == min(map(len, STRINGS))

        # case_sensitive True -- -- -- -- -- -- -- -- -- -- -- -- -- --
        out = _build_overall_statistics(STRINGS, case_sensitive=True)

        assert isinstance(out, dict)

        assert 'size' in out
        assert isinstance(out['size'], int)
        assert out['size'] == 9

        assert 'uniques_count' in out
        assert isinstance(out['uniques_count'], int)
        assert out['uniques_count'] == 8

        assert 'average_length' in out
        assert isinstance(out['average_length'], float)
        assert out['average_length'] == (sum(map(len, STRINGS)) / len(STRINGS))

        assert 'std_length' in out
        assert isinstance(out['std_length'], float)
        assert out['std_length'] == float(np.std(list(map(len, STRINGS))))

        assert 'max_length' in out
        assert isinstance(out['max_length'], int)
        assert out['max_length'] == max(map(len, STRINGS))

        assert 'min_length' in out
        assert isinstance(out['min_length'], int)
        assert out['min_length'] == min(map(len, STRINGS))










