# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text._NGramMerger._validation._validation import \
    _validation

import re

import pytest



class TestValidation:

    # all the submodules have their own tests. just test that validation
    # works and passes all good

    @pytest.mark.parametrize('_X', ([list('abc')], [tuple('abcde')]))
    @pytest.mark.parametrize('_ngrams',
        ([['a', 'b']], ((re.compile('[.]+'), 'q'),), None)
    )
    @pytest.mark.parametrize('_callable', (lambda x, y: x + y, None))
    @pytest.mark.parametrize('_sep', ('_', '', '&', None))
    @pytest.mark.parametrize('_wrap', (True, False))
    @pytest.mark.parametrize('_case_sensitive', (True, False))
    @pytest.mark.parametrize('_remove_empty_rows', (True, False))
    @pytest.mark.parametrize('_flags', (re.I | re.M, None))
    def test_passes_all_good(
        self, _X, _ngrams, _callable, _sep, _wrap, _case_sensitive,
        _remove_empty_rows, _flags
    ):

        # 'ngcallable' and 'flags' are blocked when 'ngrams' is None

        if _ngrams is None and \
                any(map(lambda x: x is not None, (_callable, _sep, _flags))):
            with pytest.raises(ValueError):
                _validation(
                    _X,
                    _ngrams,
                    _callable,
                    _sep,
                    _wrap,
                    _case_sensitive,
                    _remove_empty_rows,
                    _flags
                )

        else:
            assert _validation(
                _X,
                _ngrams,
                _callable,
                _sep,
                _wrap,
                _case_sensitive,
                _remove_empty_rows,
                _flags
            ) is None









