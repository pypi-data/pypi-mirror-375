# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.feature_extraction.text._NGramMerger._transform._wrap_manager \
    import _wrap_manager



class TestWrapManager:


    @pytest.mark.parametrize('_first_hits', ([], [0], [1], [1, 3]))
    @pytest.mark.parametrize('_second_hits', ([], [0], [3], [1, 3]))
    @pytest.mark.parametrize('_ngcallable, _sep', (
        (None, None),
        (lambda x: '&'.join(x), None),
        (None, '__'),
        (None, '@')
    ))
    def test_accuracy(self, _first_hits, _second_hits, _ngcallable, _sep):

        _first_line = ['BLACK', 'HOLE', 'SHOT', 'CLOCK', 'WORK']

        _second_line = ['BENCH', 'PRESS', 'BOARD', 'ROOM', 'MATE']

        _ngram = (re.compile('work', re.I), re.compile('bench', re.I))

        _sep = _sep or '_'

        if _ngcallable is None:
            _ngcallable = lambda x: _sep.join(x)
            _exp_sep = _sep
        else:
            _exp_sep = '&'



        first_line, second_line = _wrap_manager(
            _first_line,
            _second_line,
            _first_hits,
            _second_hits,
            _ngram,
            _ngcallable,
            _sep
        )


        _will_wrap = False
        if 3 in _first_hits or 0 in _second_hits:
            pass
        else:
            _will_wrap = True



        if _will_wrap:
            assert np.array_equal(
                first_line, ['BLACK', 'HOLE', 'SHOT', 'CLOCK', f'WORK{_exp_sep}BENCH']
            )
            assert np.array_equal(
                second_line, ['PRESS', 'BOARD', 'ROOM', 'MATE']
            )
        else:
            assert np.array_equal(
                first_line, ['BLACK', 'HOLE', 'SHOT', 'CLOCK', 'WORK']
            )
            assert np.array_equal(
                second_line, ['BENCH', 'PRESS', 'BOARD', 'ROOM', 'MATE']
            )






