# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.preprocessing.__shared._validation._any_bool import _val_any_bool



class TestValAnyBool:


    @pytest.mark.parametrize('junk_name',
        (-2.7, -1, 0, 1, 2.7, True, False, None, [0,1], (1,), {1,2}, {'a':1},
         lambda x: x)
    )
    def test_rejects_junk_name(self, junk_name):

        with pytest.raises(TypeError):
            _val_any_bool(True, _name=junk_name)


    @pytest.mark.parametrize('_name', ('eat', 'more', 'chikn'))
    def test_accepts_good_name(self, _name):

        assert _val_any_bool(False, _name=_name) is None


    # -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('junk_can_be_None',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [0,1], (1,), {1,2}, {'a':1},
         lambda x: x)
    )
    def test_rejects_junk_can_be_None(self, junk_can_be_None):

        with pytest.raises(TypeError):
            _val_any_bool(
                False, _name='whatever', _can_be_None=junk_can_be_None
            )


    @pytest.mark.parametrize('_can_be_None', (True, False))
    def test_accepts_good_can_be_None(self, _can_be_None):

        assert _val_any_bool(
            True, _name='whatever', _can_be_None=_can_be_None
        ) is None




    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('_param', (True, False, None))
    @pytest.mark.parametrize('_name', ('brevity', 'is', 'wit'))
    @pytest.mark.parametrize('_can_be_None', (True, False))
    def test_accuracy(self, _param, _name, _can_be_None):


        if _param is None and not _can_be_None:
            with pytest.raises(TypeError):
                _val_any_bool(_param, _name, _can_be_None)
        else:
            assert _val_any_bool(_param, _name, _can_be_None) is None







