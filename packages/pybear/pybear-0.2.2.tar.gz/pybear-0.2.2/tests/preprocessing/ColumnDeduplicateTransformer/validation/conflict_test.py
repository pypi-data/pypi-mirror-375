# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.preprocessing._ColumnDeduplicator._validation.\
    _conflict import _val_conflict



class TestConflict:


    @pytest.mark.parametrize('junk_conflict',
        (-1, 0, 1, 3.14, True, min, [1], (1,), {1,2}, {'a':1}, lambda x: x)
    )
    def test_typeerror_junk_conflict(self, junk_conflict):
        with pytest.raises(TypeError):
            _val_conflict(junk_conflict)


    @pytest.mark.parametrize('bad_conflict',
        ('junk', 'trash', 'garbage', 'waste')
    )
    def test_valueerror_bad_conflict(self, bad_conflict):
        with pytest.raises(ValueError):
            _val_conflict(bad_conflict)


    @pytest.mark.parametrize('_conflict', ('raise', 'ignore'))
    def test_valueerror_bad_conflict(self, _conflict):
            _val_conflict(_conflict)



