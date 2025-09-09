# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text._TextStripper._transform import _transform



class TestTransform:


    def test_accuracy(self):

        _text_1 = ["   ", "     junky ", "data       "]

        _text_1_exp_stripped = ["", "junky", "data"]

        _text_2 = [
            ["   Even  ", "  more  ", "so"],
            ["Because    ", "    of", "  being  ", "     alone"],
            ["   The   ", "  moon ", " is ", " a  ", " friend.   "]
        ]

        _text_2_exp_stripped = [
            ["Even", "more", "so"],
            ["Because", "of", "being", "alone"],
            ["The", "moon", "is", "a", "friend."]
        ]


        # 1D -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        out = _transform(_text_1)
        assert np.array_equal(out, _text_1_exp_stripped)
        # END 1D -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # 2D -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        out = _transform(_text_2)
        assert all(map(np.array_equal, out, _text_2_exp_stripped))
        # END 2D -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --





