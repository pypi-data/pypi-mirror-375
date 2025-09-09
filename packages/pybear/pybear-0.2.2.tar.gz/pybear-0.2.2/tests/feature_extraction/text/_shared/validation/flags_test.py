# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.feature_extraction.text.__shared._validation._flags \
    import _val_flags



class TestValFlags:


    # must be None, numbers.Integral, list[numbers.Integral | None]


    @pytest.mark.parametrize('junk_single_flags',
        (-2.7, 2.7, True, False, 'garbage', (0,1), {1,2}, {'A': 1}, lambda x: x)
    )
    def test_rejects_junk_single_flags(self, junk_single_flags):

        with pytest.raises(TypeError):
            _val_flags(junk_single_flags, 2)


    @pytest.mark.parametrize('junk_seq_flags',
        (list((1, False)), list('ab'), set(list((1, 2))), tuple(list((1, 2))))
    )
    def test_rejects_junk_seq_flags(self, junk_seq_flags):

        with pytest.raises(TypeError):
            _val_flags(junk_seq_flags, 2)


    def test_rejects_bad_seq_flags(self):

        # too long
        with pytest.raises(ValueError):
            _val_flags(np.random.randint(0,100, (6,)).tolist(), 5)

        # too short
        with pytest.raises(ValueError):
            _val_flags(np.random.randint(0,100, (4,)).tolist(), 5)


    def test_accepts_single_None_single_int(self):

        assert _val_flags(None, 2) is None

        assert _val_flags(-20, 2) is None

        assert _val_flags(10_000, 2) is None

        assert _val_flags(0, 2) is None

        assert _val_flags(re.I | re.X, 2) is None


    def test_accepts_list_of_None_int(self):


        for trial in range(20):

            _flags = np.random.choice(
                [int(np.random.randint(-1000, 1000)), re.I | re.X, None],
                (5, ),
                replace=True
            ).tolist()

            _val_flags(_flags, 5)















