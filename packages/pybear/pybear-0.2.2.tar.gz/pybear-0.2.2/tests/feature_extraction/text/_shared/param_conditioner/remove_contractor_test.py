# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



# this doesnt test an actual module
# it just reaffirms that python == works for re.compile(pattern, flags)


import pytest

import re



class TestReCompileEquality:


    @pytest.mark.parametrize('pattern1', ('abc', 'def', 'ghi'))
    @pytest.mark.parametrize('pattern2', ('abc', 'def', 'jkl'))
    @pytest.mark.parametrize('flags1', (re.X, re.I | re.X, re.I | re.M | re.X))
    @pytest.mark.parametrize('flags2', (re.X, re.I | re.X, 0))
    def test_accuracy(self, pattern1, flags1, pattern2, flags2):

        _ref = (pattern1 == pattern2) and (flags1 == flags2)

        compile1 = re.compile(pattern1, flags=flags1)
        compile2 = re.compile(pattern2, flags=flags2)

        assert (compile1 == compile2) is _ref


    def test_nones(self):

        compile1 = None
        compile2 = None

        assert compile1 == compile2







