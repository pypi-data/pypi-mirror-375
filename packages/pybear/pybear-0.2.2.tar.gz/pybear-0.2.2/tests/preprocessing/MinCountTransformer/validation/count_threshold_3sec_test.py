# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.preprocessing._MinCountTransformer._validation. \
    _count_threshold import _val_count_threshold



class TestValCountThreshold:


    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @staticmethod
    @pytest.fixture(scope='module')
    def err_quip_1():                   
        return "is passed as a single integer it must be"


    @staticmethod
    @pytest.fixture(scope='module')
    def err_quip_2():
        return "the length of the sequence also must "

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    # other validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # dont need to test _val_any_integer, handled elsewhere

    @pytest.mark.parametrize(f'junk_allowed',
        (-2.7, -1, 0, 1, 2.7, True, None, 'trash', {'a':1}, lambda x: x)
    )
    def test_rejects_junk_allowed(self, junk_allowed):

        with pytest.raises(TypeError):
            _val_count_threshold(
                _count_threshold=2,
                _allowed=junk_allowed,
                _n_features_in=5
            )


    @pytest.mark.parametrize(f'bad_allowed',
        ([], ['that', 'was', 'trash'], ['INT'], ['SEQUENCE[INT]'])
    )
    def test_rejects_bad_allowed(self, bad_allowed):

        with pytest.raises(ValueError):
            _val_count_threshold(
                _count_threshold=2,
                _allowed=bad_allowed,
                _n_features_in=5
            )


    @pytest.mark.parametrize(f'container', (list, set, tuple, np.array))
    @pytest.mark.parametrize(f'threshold,value',
        (
            (2, ['int']),
            ([2, 2], ['Sequence[int]']),
            (2, ['int', 'Sequence[int]'])
        )
    )
    def test_accepts_good_allowed(self, container, threshold, value):

        _allowed = container(value)

        if container is np.array:
            assert isinstance(_allowed, np.ndarray)
        else:
            assert isinstance(_allowed, container)

        _val_count_threshold(
            _count_threshold=threshold,
            _allowed=_allowed,
            _n_features_in=2
        )

    # END other validation ** * ** * ** * ** * ** * ** * ** * ** * ** *


    @pytest.mark.parametrize('_junk_count_threshold',
        (None, 'junk', {'a':1}, lambda x: x)
)
    def test_junk_count_threshold(
        self, _junk_count_threshold, err_quip_1, err_quip_2
    ):

        # valid is single number or could be sequence of numbers

        with pytest.raises(TypeError) as exc:
            _val_count_threshold(
                _count_threshold=_junk_count_threshold,
                _allowed=['int', 'Sequence[int]'],
                _n_features_in=5
            )

        # these are sequences so would enter into the sequence handling and
        # return errors only for sequences
        if isinstance(_junk_count_threshold, (str, dict)):
            assert re.escape(err_quip_1) not in re.escape(str(exc))
            assert re.escape(err_quip_2) in re.escape(str(exc))
        else:  # the rest will bounce of both and return both error messages
            assert re.escape(err_quip_1) in re.escape(str(exc))
            assert re.escape(err_quip_2) in re.escape(str(exc))


    @pytest.mark.parametrize('_bad_count_threshold',
        (-2.7, -1, 0, 1, 2.7, True, False)
    )
    def test_bad_count_threshold_as_single_value(
        self, _bad_count_threshold, err_quip_1, err_quip_2
    ):

        # must be integer >= 2

        if isinstance(_bad_count_threshold, bool):

            with pytest.raises(TypeError) as exc:
                _val_count_threshold(
                    _bad_count_threshold,
                    _allowed=['int', 'Sequence[int]'],
                    _n_features_in=5
                )
        else:
            with pytest.raises(ValueError) as exc:
                _val_count_threshold(
                    _bad_count_threshold,
                    _allowed=['int', 'Sequence[int]'],
                    _n_features_in=5
                )

        assert re.escape(err_quip_1) in re.escape(str(exc))
        assert re.escape(err_quip_2) not in re.escape(str(exc))


    @pytest.mark.parametrize('_bad_count_threshold',
        (
            [-1, 0, 1],      # 2 numbers below 1, no number >= 2
            [2.7, 2.8, 2.9],  # floats
            list('abc'),      # strings
            np.random.randint(0, 10, (3, 3)),     # bad shape
            [2, 3, 4, 5, 6]      # bad len
        )
    )
    def test_bad_count_threshold_as_sequence(
        self, _bad_count_threshold, err_quip_1, err_quip_2
    ):

        # must be 1D, only integers >= 1 with at least 1 >= 2

        with pytest.raises(ValueError) as exc:
            _val_count_threshold(
                _bad_count_threshold,
                _allowed=['int', 'Sequence[int]'],
                _n_features_in=3
            )

        assert re.escape(err_quip_1) not in re.escape(str(exc))
        assert re.escape(err_quip_2) in re.escape(str(exc))


    @pytest.mark.parametrize('_count_threshold',
        (2, [1, 1, 2], [10, 20, 30])
    )
    def test_accepts_good_count_threshold(self, _count_threshold):

        out = _val_count_threshold(
            _count_threshold,
            _allowed=['int', 'Sequence[int]'],
            _n_features_in=3
        )

        assert out is None


    @pytest.mark.parametrize('_threshold', (2, [2, 3, 1, 1]))
    @pytest.mark.parametrize('_allowed',
        (['int'], ['Sequence[int]'], ['int', 'Sequence[int]'])
    )
    def test_rejects_disallowed_dtype(self, _threshold, _allowed):

        will_fail = False

        if isinstance(_threshold, int) and 'int' not in _allowed:
            will_fail = True
        if isinstance(_threshold, list) and 'Sequence[int]' not in _allowed:
            will_fail = True

        if will_fail:
            with pytest.raises(TypeError):
                _val_count_threshold(
                    _threshold,
                    _allowed=_allowed,
                    _n_features_in=4
                )
        else:
            out = _val_count_threshold(
                _threshold,
                _allowed=_allowed,
                _n_features_in=4
            )

            assert out is None




