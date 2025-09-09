# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

from pybear.feature_extraction.text.__shared._validation._compile_holder \
    import _val_compile_holder



class TestValCompileHolder:


    @pytest.mark.parametrize('junk_bad_n_rows',
        (-2.7, -1, 2.7, True, False, None, 'trash', [0,1], (1,),
         {1,2}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_bad_n_rows(self, junk_bad_n_rows):

        with pytest.raises(AssertionError):
            _val_compile_holder(None, junk_bad_n_rows)


    @pytest.mark.parametrize('good_n_rows', (0, 2, 3, 100_000_000))
    def test_accepts_good_n_rows(self, good_n_rows):

        assert _val_compile_holder(None, good_n_rows) is None

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('junk_name',
        (-2.7, -1, 0, 1, 2.7, True, False, None, [0,1], (1,), {1,2},
         {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_name(self, junk_name):

        with pytest.raises(AssertionError):
            _val_compile_holder(None, 5, junk_name)


    def test_accepts_good_name(self):

        assert _val_compile_holder(None, 5, 'whatever') is None


    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('junk_ch',
        (-2.7, -1, 0, 1, 2.7, True, False, 'trash', [0,1], (1,),
         {1,2}, {'a':1}, lambda x: x, tuple('abc'), (list('abc')))
    )
    def test_rejects_junk_ch(self, junk_ch):

        with pytest.raises(TypeError):
            _val_compile_holder(junk_ch, 5)


    def test_rejects_bad_ch(self):

        _bad_ch = [re.compile('a'), re.compile('b'), re.compile('c')]

        # too long
        with pytest.raises(ValueError):
            _val_compile_holder(_bad_ch, 2)

        # too short
        with pytest.raises(ValueError):
            _val_compile_holder(_bad_ch, 4)


    @pytest.mark.parametrize('good_ch',
        (None, re.compile('a'), (re.compile('b'), re.compile('c', re.I)),
        [None, re.compile('a'), (re.compile('b'), re.compile('c', re.I))])
    )
    def test_accepts_good_ch(self, good_ch):

        assert _val_compile_holder(good_ch, 3) is None




