# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text._NGramMerger._transform._match_finder import \
    _match_finder

from pybear.feature_extraction.text._NGramMerger._transform._replacer import \
    _replacer

import pytest

import re

import numpy as np



class TestSlider:

    # def _replacer(
    #     _line: list[str],
    #     _ngram: Sequence[str | re.Pattern],
    #     _hits: Sequence[int],
    #     _ngcallable: Callable[[Sequence[str]], str] | None,
    #     _sep: str | None
    # ) -> list[str]:


    @pytest.mark.parametrize('_sep', (None, '@', '&', '__'))
    def test_accuracy_sep(self, _sep):

        _exp_sep = _sep or '_'

        _line1 = ['EGG', 'SANDWICHES', 'AND', 'ICE', 'CREAM']

        _ngram1 = (re.compile('EGG'), re.compile('sandwich[es]+', re.I))

        indices = _match_finder(_line1, _ngram1)
        out = _replacer(_line1, _ngram1, indices, None, _sep)

        exp = [f'EGG{_exp_sep}SANDWICHES', 'AND', 'ICE', 'CREAM']

        assert np.array_equal(out, exp)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        _line2 = out.copy()

        _ngram2 = (re.compile('ICE'), re.compile('CREAM'))

        indices = _match_finder(_line2, _ngram2)

        out2 = _replacer(_line2, _ngram2, indices, None, _sep)

        exp2 = [f'EGG{_exp_sep}SANDWICHES', 'AND', f'ICE{_exp_sep}CREAM']

        assert np.array_equal(out2, exp2)



    def test_accuracy_callable(self):

        _line1 = ['BIG', 'BIG', 'MONEY', 'NO', 'WHAMMY', 'YES', 'WHAMMY']

        _ngram1 = (re.compile('big', re.I), re.compile('money', re.I))

        indices = _match_finder(_line1, _ngram1)

        def _callable1(_matches):
            return '__'.join(np.flip(list(_matches)).tolist())

        out = _replacer(_line1, _ngram1, indices, _callable1, _sep='(&#(&$)#!(*$')

        exp = ['BIG', 'MONEY__BIG', 'NO', 'WHAMMY', 'YES', 'WHAMMY']

        assert np.array_equal(out, exp)

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        _line2 = out.copy()

        _ngram2 = (re.compile('NO'), re.compile('WHAMM.+', re.I))

        indices = _match_finder(_line2, _ngram2)

        def _callable2(_matches):
            return 'BEER&BRATS'

        out2 = _replacer(_line2, _ngram2, indices, _callable2, None)

        exp2 = ['BIG', 'MONEY__BIG', 'BEER&BRATS', 'YES', 'WHAMMY']

        assert np.array_equal(out2, exp2)


    def test_ignores_empty_hits(self):

        _line = ['NEW', 'MEXICO', 'NEW', 'HAMPSHIRE']

        out = _replacer(
            ['NEW', 'MEXICO', 'NEW', 'HAMPSHIRE'],
            (re.compile('NEW'), re.compile('YORK')),
            [],
            lambda x: '_'.join(x),
            None
        )
        assert isinstance(out, list)
        assert np.array_equal(out, _line)


    def test_bad_callable(self):

        with pytest.raises(TypeError):

            _line = ['SILLY', 'STRING']

            _replacer(_line, (re.compile('SILLY'), ), [0], lambda x: _line, None)






