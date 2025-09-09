# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd

from pybear.feature_extraction.text._TextLookup._shared._validation._split_always \
    import _val_split_always



class TestSplitAlways:


    @pytest.mark.parametrize('junk_split_always',
        (-2.7, -1, 0, 1, 2.7, True, False, 'trash', [0,1], (1,),
         {1,2}, {'a':1}, {1: 2}, {True: [1]}, lambda x: x)
    )
    def test_rejects_junk(self, junk_split_always):

        with pytest.raises(TypeError):
            _val_split_always(junk_split_always)


    @staticmethod
    @pytest.fixture(scope='module')
    def container_maker():

        def foo(obj: list[str], container: any):
            if container is np.array:
                out = np.array(obj)
                assert isinstance(out, np.ndarray)
            elif container is pd.Series:
                out = pd.Series(obj)
                assert isinstance(out, pd.Series)
            else:
                out = container(obj)
                assert isinstance(out, container)

            return out

        return foo


    @pytest.mark.parametrize('container', (list, set, tuple, np.array, pd.Series))
    def test_accepts_dict_str_seq_str_or_None(self, container_maker, container):

        _seq_1 = container_maker(['ONE', 'TWO', 'THREE'], container)

        assert _val_split_always(None) is None

        assert _val_split_always({'ZERO': _seq_1}) is None








