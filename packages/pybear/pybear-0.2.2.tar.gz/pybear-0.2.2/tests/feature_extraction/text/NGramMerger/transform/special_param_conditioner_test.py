# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text._NGramMerger._transform. \
    _special_param_conditioner import _special_param_conditioner

import re

import pytest



class TestSpecialParamConditioner:

    # no validation


    # as of 25_04_07_11_02_00 validation for the main transform
    # method is now blocking anything passed to
    # 'flags' and/or 'ngcallable' when 'ngrams' is None, but this
    # module should still flow thru.


    @pytest.mark.parametrize('_case_sensitive', (True, False))
    @pytest.mark.parametrize('_flags', (None, re.I, re.I | re.M | re.X))
    def test_ngrams_None_flows_thru(self, _case_sensitive, _flags):


        assert _special_param_conditioner(
            _ngrams=None,
            _case_sensitive=_case_sensitive,
            _flags=_flags
        ) is None


    @pytest.mark.parametrize('_ngrams',
        (None, ((re.compile('pigs', re.M), 'in'),),
         ((re.compile('pigs', re.M), 'in'),  ('a', '$blanket')))
    )
    @pytest.mark.parametrize('_case_sensitive', (True, False))
    @pytest.mark.parametrize('_flags', (None, re.I, re.I | re.M))
    def test_accuracy(self, _ngrams, _case_sensitive, _flags):


        out = _special_param_conditioner(
            _ngrams=_ngrams,
            _case_sensitive=_case_sensitive,
            _flags=_flags
        )

        if _ngrams is None:
            assert out is None
        else:

            # we should be looking at something like [(n1_1, n1_2), (n2_1, n2_2)]

            _base_exp_flags = re.U   # the default assigned by re.compile
            if not _case_sensitive:
                _base_exp_flags |= re.I
            if _flags is not None:
                _base_exp_flags |= _flags

            assert isinstance(out, list)

            for _n_idx, _ngram in enumerate(out):

                assert isinstance(_ngram, tuple)
                assert all(map(isinstance, _ngram, (re.Pattern for _ in _ngram)))

                for _pattern_idx, _pattern in enumerate(_ngram):

                    # pull apart each Pattern, if originally str was passed
                    # .pattern must equal escaped str. flags must equal
                    # the expected + whatever was originally in any ngram passed
                    # in a compile.
                    _og_ngram = _ngrams[_n_idx][_pattern_idx]

                    if isinstance(_og_ngram, str):
                        assert _pattern.pattern == re.escape(_og_ngram)
                        assert _pattern.flags == _base_exp_flags
                    elif isinstance(_og_ngram, re.Pattern):
                        assert _pattern.pattern == _og_ngram.pattern
                        assert _pattern.flags == _base_exp_flags | _og_ngram.flags
                    else:
                        raise Exception










