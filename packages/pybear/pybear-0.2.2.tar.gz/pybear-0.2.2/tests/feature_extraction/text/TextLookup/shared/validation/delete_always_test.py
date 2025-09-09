# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd

from pybear.feature_extraction.text._TextLookup._shared._validation._delete_always \
    import _val_delete_always



class TestDeleteAlways:


    @pytest.mark.parametrize('junk_delete_always',
        (-2.7, -1, 0, 1, 2.7, True, False, 'trash', [0,1], (1,),
         {1,2}, {'a':1}, lambda x: x)
    )
    def test_rejects_junk(self, junk_delete_always):

        with pytest.raises(TypeError):
            _val_delete_always(junk_delete_always)


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
    def test_accepts_seq_str_or_None(self, container_maker, container):


        _seq_1 = container_maker(['ONE', 'TWO', 'THREE'], container)
        _seq_2 = container_maker(['1', '2', '3'], container)
        _seq_3 = container_maker(['ichi', 'ni', 'sa'], container)

        assert _val_delete_always(None) is None

        assert _val_delete_always(_seq_1) is None

        assert _val_delete_always(_seq_2) is None

        assert _val_delete_always(_seq_3) is None







