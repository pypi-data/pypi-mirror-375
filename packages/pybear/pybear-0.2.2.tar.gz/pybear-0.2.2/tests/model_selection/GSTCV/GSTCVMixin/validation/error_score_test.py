# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.model_selection.GSTCV._GSTCVMixin._validation._error_score \
    import _val_error_score



class TestVaErrorScore:


    @pytest.mark.parametrize('junk_error_score',
        (bool, None, [0,1], (0,1), {0,1}, {'a':1}, min, lambda x: x)
    )
    def test_type_error_non_str_non_num(self, junk_error_score):
        with pytest.raises(TypeError):
            _val_error_score(junk_error_score)


    @pytest.mark.parametrize('bad_error_score',
        ('trash', 'garbage', 'junk', 'rubbish', 'refuse', 'waste')
    )
    def test_value_error_bad_str(self, bad_error_score):
        with pytest.raises(ValueError):
            _val_error_score(bad_error_score)


    @pytest.mark.parametrize('good_error_score',
        (-1000, -np.pi, -1, 0, 1, np.pi, 1000000, np.nan, 'raise')
    )
    def test_accepts_literal_raise_any_num(self, good_error_score):

        assert _val_error_score(good_error_score) is None






