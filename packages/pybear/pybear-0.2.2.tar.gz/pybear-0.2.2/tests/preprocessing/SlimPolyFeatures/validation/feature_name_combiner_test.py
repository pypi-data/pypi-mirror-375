# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#




from pybear.preprocessing._SlimPolyFeatures._validation._feature_name_combiner \
    import _val_feature_name_combiner

import numpy as np

import pytest



class TestValFeatureNameCombiner:


    @pytest.mark.parametrize('_fnc_string_literals',
        ('junk', 'trash', 'as_indices', 'garbage', 'as_feature_names')
    )
    def test_string_literals(self, _fnc_string_literals):

        if _fnc_string_literals in ('as_indices', 'as_feature_names'):
            _val_feature_name_combiner(_fnc_string_literals)
        else:
            with pytest.raises(ValueError):
                _val_feature_name_combiner(_fnc_string_literals)


    @pytest.mark.parametrize('_fnc_callable',
        (
            -np.e, -1, 0, 1, np.e, True, False, None, [0,1], (0,), {0,1},
            {'a':1}, 'string', lambda x: x, lambda x, y: x + y
        )
    )
    def test_accepts_callable(self, _fnc_callable):

        if callable(_fnc_callable):
            _val_feature_name_combiner(_fnc_callable)
        else:
            with pytest.raises(ValueError):
                _val_feature_name_combiner(_fnc_callable)































