# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#




import pytest

import re

import numpy as np

from pybear.feature_extraction.text._TextReplacer._validation._validation \
    import _validation




class TestValidation:

    # the brunt of the test is done at the individual module level.
    # just test that this takes and passes good args


    @pytest.mark.parametrize('_len', (0, 10, 1000))
    @pytest.mark.parametrize('_replace',
        (None, 'tuple_1', 'tuple_2', 'list_1', 'list_2', 'list_3')
    )
    @pytest.mark.parametrize('_case_sensitive',
        ('bool_1', 'bool_2', 'list_1', 'list_2', 'list_3')
    )
    @pytest.mark.parametrize('_flags',
        (None, 'flag_1', 'flag_2', 'list_1', 'list_2', 'list_3')
    )
    def test_accuracy(self, _len, _replace, _case_sensitive, _flags):


        _X = np.random.choice(list('abcdef'), _len, replace=True)

        if _replace is None:
            _replace = None
        elif _replace == 'tuple_1':
            _replace = ('a', '')
        elif _replace == 'tuple_2':
            _replace = (re.compile('a', re.I), lambda x: 'new_word')
        elif _replace == 'list_1':
            _replace = [('b', 'B') for _ in range(_len)]
        elif _replace == 'list_2':
            _replace = [(re.compile('b', re.M), 'B') for _ in range(_len)]
        elif _replace == 'list_3':
            _replace = [None for _ in range(_len)]
        else:
            raise Exception

        if _case_sensitive == 'bool_1':
            _case_sensitive = True
        elif _case_sensitive == 'bool_2':
            _case_sensitive = False
        elif _case_sensitive == 'list_1':
            _case_sensitive = [True for _ in range(_len)]
        elif _case_sensitive == 'list_2':
            _case_sensitive = [False for _ in range(_len)]
        elif _case_sensitive == 'list_3':
            _case_sensitive = [None for _ in range(_len)]
        else:
            raise Exception

        if _flags is None:
            _flags = None
        elif _flags == 'flag_1':
            _flags = re.I
        elif _flags == 'flag_2':
            _flags = re.I | re.M
        elif _flags == 'list_1':
            _flags = [None for _ in range(_len)]
        elif _flags == 'list_2':
            _flags = [re.I for _ in range(_len)]
        elif _flags == 'list_3':
            _flags = [re.I | re.M for _ in range(_len)]
        else:
            raise Exception


        assert _validation(
            _X,
            _replace,
            _case_sensitive,
            _flags
        ) is None






