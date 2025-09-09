# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.feature_extraction.text._TextStatistics._partial_fit. \
    _build_overall_statistics import _build_overall_statistics

from pybear.feature_extraction.text._TextStatistics._partial_fit. \
    _merge_overall_statistics import _merge_overall_statistics

from pybear.feature_extraction.text._TextStatistics._validation. \
    _overall_statistics import _val_overall_statistics



class TestMergeOverallStatistics:


    # def _merge_overall_statistics(
    #     _current_overall_statistics: OverallStatisticsType,
    #     _overall_statistics: OverallStatisticsType,
    #     _len_uniques: int
    # ) -> OverallStatisticsType:


    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @staticmethod
    @pytest.fixture(scope='module')
    def _good_overall_statistics():

        __ = {
            'size': 10,
            'average_length': 8.234234,
            'std_length': 1.2390535,
            'max_length': 13,
            'min_length': 4,
            'uniques_count': 10
        }

        _val_overall_statistics(__)

        return __


    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # basic validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @pytest.mark.parametrize('junk_cos',
        (-2.7, -1, 0, 1, 2.7, True, None, 'trash', [0,1], (0,), {0,1}, lambda x: x)
    )
    def test_rejects_junk_current_overall_statistics(
        self, junk_cos, _good_overall_statistics
    ):

        with pytest.raises(AssertionError):

            _merge_overall_statistics(
                junk_cos,
                _good_overall_statistics,
                10
            )


    @pytest.mark.parametrize('junk_os',
        (-2.7, -1, 0, 1, 2.7, True, None, 'trash', [0, 1], (0,), {0, 1}, lambda x: x)
    )
    def test_rejects_junk_overall_statistics(
        self, junk_os, _good_overall_statistics
    ):

        with pytest.raises(AssertionError):
            _merge_overall_statistics(
                _good_overall_statistics,
                junk_os,
                10
            )


    @pytest.mark.parametrize('junk_len_uniques',
        (-2.7, -1, 2.7, True, None, 'trash', [0, 1], (0,), {0, 1}, lambda x: x)
    )
    def test_rejects_junk_len_uniques(
        self, junk_len_uniques, _good_overall_statistics
    ):
        with pytest.raises(AssertionError):
            _merge_overall_statistics(
                _good_overall_statistics,
                _good_overall_statistics,
                junk_len_uniques
            )


    def test_rejects_bad_len_uniques(self, _good_overall_statistics):

        with pytest.raises(AssertionError):
            _merge_overall_statistics(
                _good_overall_statistics,
                _good_overall_statistics,
                _good_overall_statistics['uniques_count'] - 1
            )

    # END basic validation ** * ** * ** * ** * ** * ** * ** * ** * ** *


    def test_accuracy_first_pass(self, _good_overall_statistics):

        out = _merge_overall_statistics(
            _good_overall_statistics,
            {},    # must be empty
            10
        )

        assert out == _good_overall_statistics


    @pytest.mark.parametrize('case_sensitive', (True, False))
    def test_accuracy_after_first_pass(self, case_sensitive):

        string_list_1 = ['I', 'would', 'not', 'like', 'them', 'here', 'or', 'there']

        _dict_1 = _build_overall_statistics(
            string_list_1,
            case_sensitive=case_sensitive
        )
        assert isinstance(_dict_1, dict)
        assert len(_dict_1) == 6
        assert _dict_1['size'] == 8
        assert _dict_1['average_length'] == 3.5
        assert round(_dict_1['std_length'], 3) == 1.323
        assert _dict_1['max_length'] == 5
        assert _dict_1['min_length'] == 1
        assert _dict_1['uniques_count'] == 8


        string_list_2 = ['I', 'WOULD', 'NOT', 'LIKE', 'THEM', 'ANYWHERE']

        _dict_2 = _build_overall_statistics(
            string_list_2,
            case_sensitive=case_sensitive
        )
        assert isinstance(_dict_2, dict)
        assert len(_dict_2) == 6
        assert _dict_2['size'] == 6
        assert round(_dict_2['average_length'], 4) == 4.1667
        assert round(_dict_2['std_length'], 3) == 2.115
        assert _dict_2['max_length'] == 8
        assert _dict_2['min_length'] == 1
        assert _dict_2['uniques_count'] == 6

        if case_sensitive:
            _UNIQUES = set(string_list_1).union(string_list_2)
        else:
            _UNIQUES = set(
                map(str.upper, string_list_1)
            ).union(map(str.upper, string_list_2))

        out = _merge_overall_statistics(
            _dict_1,
            _dict_2,
            _len_uniques=len(_UNIQUES)
        )

        if case_sensitive:
            assert isinstance(out, dict)
            assert len(out) == 6
            assert out['size'] == 14
            assert round(out['average_length'], 3) == 3.786
            assert round(out['std_length'], 4) == 1.7394
            assert out['max_length'] == 8
            assert out['min_length'] == 1
            assert out['uniques_count'] == 13
        elif not case_sensitive:
            assert isinstance(out, dict)
            assert len(out) == 6
            assert out['size'] == 14
            assert round(out['average_length'], 3) == 3.786
            assert round(out['std_length'], 4) == 1.7394
            assert out['max_length'] == 8
            assert out['min_length'] == 1
            assert out['uniques_count'] == 9








