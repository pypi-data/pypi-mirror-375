# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

import numpy as np

from pybear.model_selection.GSTCV._GSTCVMixin._param_conditioning._thresholds \
    import _cond_thresholds



class TestCondThresholds:


# def _cond_thresholds(
#     _thresholds: ThresholdsInputType,
# ) -> ThresholdsWIPType:


    @pytest.mark.parametrize('_ifk', (True, False))
    @pytest.mark.parametrize('_idx', (0, 5, 10))
    def test_none_returns_linspace(self, _ifk, _idx):
        assert np.array_equiv(_cond_thresholds(None), np.linspace(0, 1, 21))


    @pytest.mark.parametrize('_ifk', (True, False))
    @pytest.mark.parametrize('_idx', (0, 5, 10))
    @pytest.mark.parametrize('good_thresh',
        (0, 0.5, 1, [0,0.5,1], (0.25, 0.5, 0.75), {0.7, 0.8, 0.9})
    )
    def test_accepts_good_thresh(self, good_thresh, _ifk, _idx):

        try:
            good_thresh = list(good_thresh)
        except:
            good_thresh = [good_thresh]

        _og_good_thresh = deepcopy(good_thresh)

        out = _cond_thresholds(good_thresh)

        assert isinstance(out, list)
        assert all(map(isinstance, out, (float for i in out)))

        assert np.array_equiv(out, list(good_thresh))

        assert good_thresh == _og_good_thresh




