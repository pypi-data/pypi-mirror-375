# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest


from pybear.model_selection.GSTCV._GSTCVMixin._validation._verbose \
    import _val_verbose



class TestValVerbose:


    @pytest.mark.parametrize('junk_verbose',
        (None, 'trash', [0,1], (1,0), {1,0}, {'a': 1}, lambda x: x, float('inf'))
    )
    def test_rejects_non_numeric(self, junk_verbose):

        with pytest.raises(TypeError):
            _val_verbose(junk_verbose)


    @pytest.mark.parametrize('bad_verbose', (float('-inf'), -4, -1))
    def test_rejects_negative(self, bad_verbose):
        with pytest.raises(ValueError):
            _val_verbose(bad_verbose)


    @pytest.mark.parametrize('_can_be_raw_value', (True, False))
    @pytest.mark.parametrize('_bool', (True, False))
    def test_bools(self, _bool, _can_be_raw_value):

        if _can_be_raw_value:
            assert _val_verbose(
                _bool, _can_be_raw_value=_can_be_raw_value
            ) is None
        else:
            with pytest.raises(TypeError):
                _val_verbose(
                    _bool, _can_be_raw_value=_can_be_raw_value
                )


    @pytest.mark.parametrize('_can_be_raw_value', (True, False))
    @pytest.mark.parametrize('_float', (0.124334, 3.14, 8.8888))
    def test_floats(self, _float, _can_be_raw_value):
        if _can_be_raw_value:
            assert _val_verbose(
                _float, _can_be_raw_value=_can_be_raw_value
            ) is None
        else:
            with pytest.raises(TypeError):
                _val_verbose(
                    _float, _can_be_raw_value=_can_be_raw_value
                )


    @pytest.mark.parametrize('_int', (0, 1, 5, 200))
    def test_ints(self, _int):
        assert _val_verbose(_int, _can_be_raw_value=True) is None




