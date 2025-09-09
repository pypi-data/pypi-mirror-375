# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.GSTCV._GSTCVMixin._validation._thresholds \
    import _val_thresholds



class TestValThresholds:


    # 'is_from_kwargs' ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_ifk',
        (0, 1, 3.14, None, min, 'junk', [0,1], {'a':1}, lambda x: x)
    )
    def test_rejects_non_bool(self, standard_thresholds, junk_ifk):

        with pytest.raises(TypeError):
            _val_thresholds(standard_thresholds, junk_ifk, 0)


    @pytest.mark.parametrize('good_ifk', (True, False))
    def test_accepts_bool(self, standard_thresholds, good_ifk):
        # 'is_from_kwargs'
        assert _val_thresholds(standard_thresholds, good_ifk, 0) is None

    # END 'is_from_kwargs' ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # 'idx' ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    @pytest.mark.parametrize('junk_idx',
        (-1, True, False, 3.14, None, min, 'junk', [0,1], {'a':1}, lambda x: x)
    )
    def test_idx_rejects_junk(self, standard_thresholds, junk_idx):
        # 'is_from_kwargs'
        with pytest.raises((TypeError, ValueError)):
            _val_thresholds(standard_thresholds, True, junk_idx)


    @pytest.mark.parametrize('good_idx', (0, 1, 100))
    def test_idx_accepts_int(self, standard_thresholds, good_idx):
        assert _val_thresholds(standard_thresholds, True, good_idx) is None

    # END 'idx' ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * *


    @pytest.mark.parametrize('_ifk', (True, False))
    @pytest.mark.parametrize('_idx', (0, 5, 10))
    @pytest.mark.parametrize('junk_thresh',
        (True, False, 'trash', min, {'a':1}, lambda x: x)
    )
    def test_rejects_non_num_none_iter(self, junk_thresh, _ifk, _idx):
        with pytest.raises(TypeError):
            _val_thresholds(junk_thresh, _ifk, _idx)


    @pytest.mark.parametrize('_ifk', (True, False))
    @pytest.mark.parametrize('_idx', (0, 5, 10))
    def test_None(self, _ifk, _idx):
        assert _val_thresholds(
            None, _ifk, _idx, _must_be_list_like=False
        ) is None


    @pytest.mark.parametrize('_ifk', (True, False))
    @pytest.mark.parametrize('_idx', (0, 5, 10))
    @pytest.mark.parametrize('bad_thresh', (-1, 2, 10))
    def test_rejects_thresh_out_of_range(self, bad_thresh, _ifk, _idx):
        with pytest.raises(ValueError):
            _val_thresholds(bad_thresh, _ifk, _idx, _must_be_list_like=False)


    @pytest.mark.parametrize('_ifk', (True, False))
    @pytest.mark.parametrize('_idx', (0, 5, 10))
    def test_junk_in_list(self, _ifk, _idx):

        with pytest.raises(TypeError):
            _val_thresholds(['a','b','c'], _ifk, _idx)

        with pytest.raises(ValueError):
            _val_thresholds([-3.14, 3.14], _ifk, _idx)


    @pytest.mark.parametrize('_ifk', (True, False))
    @pytest.mark.parametrize('_idx', (0, 5, 10))
    @pytest.mark.parametrize('good_thresh',
        (0, 0.5, 1, [0,0.5,1], (0.25, 0.5, 0.75), {0.7, 0.8, 0.9})
    )
    def test_accepts_good_thresh(self, good_thresh, _ifk, _idx):

        assert _val_thresholds(
            good_thresh, _ifk, _idx, _must_be_list_like=False
        ) is None









