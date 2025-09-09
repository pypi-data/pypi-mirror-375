# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest



from pybear.preprocessing._SlimPolyFeatures._validation._X_supplemental \
    import _val_X_supplemental



class TestValX:


    @pytest.mark.parametrize('junk_intx_only',
        (-2.7, -1, 0, 1, 2.7, None, 'junk', [0,1], (0,1), {'a':1}, lambda x: x)
    )
    def test_rejects_junk_intx_only(self, X_np, junk_intx_only):

        with pytest.raises(AssertionError):
            _val_X_supplemental(X_np, _interaction_only=junk_intx_only)


    @pytest.mark.parametrize('_intx_only', (True, False))
    def test_accepts_bool_intx_only(self, X_np, _intx_only):

        assert _val_X_supplemental(X_np, _interaction_only=_intx_only) is None


    @pytest.mark.parametrize('_columns', (1, 2, 3))
    @pytest.mark.parametrize('_intx_only', (True, False))
    def test_quirks_of_shape_and_intx_only(self, X_np, _columns, _intx_only):

        # if interaction only must have at least 2 columns
        # if not interaction only can have 1 column

        _X = X_np[:, :_columns]

        if _intx_only and _columns < 2:
            with pytest.raises(ValueError):
                _val_X_supplemental(_X, _intx_only)
        elif not _intx_only and _columns < 1:
            with pytest.raises(ValueError):
                _val_X_supplemental(_X, _intx_only)
        else:
            assert _val_X_supplemental(_X, _intx_only) is None





