# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

from pybear.feature_extraction.text._TextStatistics._validation. \
    _overall_statistics import _val_overall_statistics



class TestValOverallStatistics:


    @staticmethod
    @pytest.fixture(scope='module')
    def _good_osd():

        _allowed_keys = [
            'size', 'uniques_count', 'max_length',
            'min_length', 'average_length', 'std_length'
        ]

        return dict((zip(_allowed_keys, [10, 9, 6, 4, 4.925738, 1.237356])))


    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @pytest.mark.parametrize('junk_osd',
        (
            -2.7, -1, 0, 1, 2.7, True, False, None, 'trash', [0,1], (1,), {0,1},
            lambda x: 1
        )
    )
    def test_rejects_non_dict(self, junk_osd):

        with pytest.raises(AssertionError):
            _val_overall_statistics(junk_osd)


    def test_rejects_bad_keys(self, _good_osd):

        # integers
        with pytest.raises(AssertionError):
            _val_overall_statistics(
                dict((zip(range(6), [10, 10, 6, 3, 4.5, 1.2])))
            )

        # invalid strings
        with pytest.raises(AssertionError):
            _val_overall_statistics(
                dict((zip(list('abcde'), [10, 10, 6, 3, 4.5, 1.2])))
            )

        # too long
        _long_osd = deepcopy(_good_osd)
        _long_osd['crazy key'] = 12

        with pytest.raises(AssertionError):
            _val_overall_statistics(_long_osd)

        # too short
        _short_osd = deepcopy(_good_osd)
        del _short_osd['size']

        with pytest.raises(AssertionError):
            _val_overall_statistics(_short_osd)


    @pytest.mark.parametrize('junk_size',
        (
            -2.7, -1, 2.7, True, False, None, 'trash', [0,1], (1,), {0,1},
            lambda x: 1
         )
    )
    def test_size_rejects_bad_values(self, junk_size, _good_osd):

        _wip_osd = deepcopy(_good_osd)
        _wip_osd['size'] = junk_size

        with pytest.raises(AssertionError):
            _val_overall_statistics(_wip_osd)


    @pytest.mark.parametrize('junk_unq_ct',
        (
            -2.7, -1, 2.7, True, False, None, 'trash', [0,1], (1,), {0,1},
            lambda x: 1
         )
    )
    def test_uniques_count_rejects_bad_values(self, junk_unq_ct, _good_osd):

        _wip_osd = deepcopy(_good_osd)
        _wip_osd['uniques_count'] = junk_unq_ct

        with pytest.raises(AssertionError):
            _val_overall_statistics(_wip_osd)


    @pytest.mark.parametrize('junk_max_len',
        (
            -2.7, -1, 2.7, True, False, None, 'trash', [0,1], (1,), {0,1},
            lambda x: 1
         )
    )
    def test_max_len_rejects_bad_values(self, junk_max_len, _good_osd):

        _wip_osd = deepcopy(_good_osd)
        _wip_osd['max_length'] = junk_max_len

        with pytest.raises(AssertionError):
            _val_overall_statistics(_wip_osd)


    @pytest.mark.parametrize('junk_min_len',
        (
            -2.7, -1, 2.7, True, False, None, 'trash', [0,1], (1,), {0,1},
            lambda x: 1
         )
    )
    def test_min_len_rejects_bad_values(self, junk_min_len, _good_osd):

        _wip_osd = deepcopy(_good_osd)
        _wip_osd['min_length'] = junk_min_len

        with pytest.raises(AssertionError):
            _val_overall_statistics(_wip_osd)


    @pytest.mark.parametrize('junk_average_len',
        (
            -2.7, -1, True, False, None, 'trash', [0,1], (1,), {0,1},
            lambda x: 1
         )
    )
    def test_avg_len_rejects_bad_values(self, junk_average_len, _good_osd):

        _wip_osd = deepcopy(_good_osd)
        _wip_osd['average_length'] = junk_average_len

        with pytest.raises(AssertionError):
            _val_overall_statistics(_wip_osd)


    @pytest.mark.parametrize('junk_std',
        (
            -2.7, -1, True, False, None, 'trash', [0,1], (1,), {0,1},
            lambda x: 1
         )
    )
    def test_std_len_rejects_bad_values(self, junk_std, _good_osd):

        _wip_osd = deepcopy(_good_osd)
        _wip_osd['std_length'] = junk_std

        with pytest.raises(AssertionError):
            _val_overall_statistics(_wip_osd)


    def test_relative_values(self, _good_osd):

        # num uniques must be <= size
        _wip_osd = deepcopy(_good_osd)
        _wip_osd['uniques_count'] = _wip_osd['size'] + 1

        with pytest.raises(AssertionError):
            _val_overall_statistics(_wip_osd)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # min_length <= max_length
        _wip_osd = deepcopy(_good_osd)
        _wip_osd['min_length'] = _wip_osd['max_length'] + 1

        with pytest.raises(AssertionError):
            _val_overall_statistics(_wip_osd)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # average_length <= max_length
        _wip_osd = deepcopy(_good_osd)
        _wip_osd['average_length'] = _wip_osd['max_length'] + 1

        with pytest.raises(AssertionError):
            _val_overall_statistics(_wip_osd)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # average_length >= min_length
        _wip_osd = deepcopy(_good_osd)
        _wip_osd['average_length'] = _wip_osd['min_length'] - 1

        with pytest.raises(AssertionError):
            _val_overall_statistics(_wip_osd)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    def test_accepts_good(self, _good_osd):

        _val_overall_statistics(_good_osd)






