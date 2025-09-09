# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text.__shared._validation._case_sensitive \
    import _val_case_sensitive



class TestCaseSensitive:


    @pytest.mark.parametrize('junk_case_sensitive',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [0,1], (1,), {1,2}, {'a':1},
         (True, False), {True, False}, lambda x: x)
    )
    def test_rejects_junk(self, junk_case_sensitive):

        with pytest.raises(TypeError):
            _val_case_sensitive(junk_case_sensitive, 5)


    def test_rejects_bad_len(self):

        with pytest.raises(ValueError):
            _val_case_sensitive(
                np.random.randint(0, 2, (6,)).astype(bool).tolist(),
                5
            )

        with pytest.raises(ValueError):
            _val_case_sensitive(
                np.random.randint(0, 2, (4,)).astype(bool).tolist(),
                5
            )


    def test_accepts_good(self):

        assert _val_case_sensitive(True, 5) is None

        assert _val_case_sensitive(False, 5) is None

        assert _val_case_sensitive(
            np.random.randint(0, 2, (5,)).astype(bool).tolist(),
            5
        ) is None

        _remove = np.random.randint(0, 2, (5,)).astype(bool).tolist()
        _remove[int(np.random.randint(0, 5))] = None
        assert _val_case_sensitive(
            _remove,
            5
        ) is None


