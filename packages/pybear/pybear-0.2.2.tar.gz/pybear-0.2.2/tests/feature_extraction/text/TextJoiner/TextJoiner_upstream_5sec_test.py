# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text._NGramMerger.NGramMerger import NGramMerger
from pybear.feature_extraction.text._StopRemover.StopRemover import StopRemover
from pybear.feature_extraction.text._TextJoiner.TextJoiner import TextJoiner
from pybear.feature_extraction.text._TextJustifier.TextJustifier import TextJustifier
from pybear.feature_extraction.text._TextLookup.TextLookup import TextLookup
from pybear.feature_extraction.text._TextLookup.TextLookupRealTime import \
    TextLookupRealTime
from pybear.feature_extraction.text._TextNormalizer.TextNormalizer import TextNormalizer
from pybear.feature_extraction.text._TextPadder.TextPadder import TextPadder
from pybear.feature_extraction.text._TextRemover.TextRemover import TextRemover
from pybear.feature_extraction.text._TextReplacer.TextReplacer import TextReplacer
from pybear.feature_extraction.text._TextSplitter.TextSplitter import TextSplitter
from pybear.feature_extraction.text._TextStripper.TextStripper import TextStripper



# Run an operation with TextJoiner, then test all the other text modules are
# able to do an operation on mutated output as expected.



class TestUpstreamImpactOnLaterModules:


    def test_ngram_merger(self):

        # TextJoiner requires 2D and puts out 1D. NGM requires 2D, so
        # TJ could never directly feed into NGM.
        pass


    def test_stop_remover(self):

        # TextJoiner requires 2D and puts out 1D. StopRemover requires
        # 2D, so TJ could never directly feed into SR.
        pass


    def test_text_joiner(self):

        # TextJoiner requires 2D and puts out 1D. A second TextJoiner
        # requires 2D, so TJ could never directly feed itself.
        pass


    def test_text_justifier(self):

        TJ = TextJoiner(sep=' ')
        out = TJ.fit_transform([['TWELVE', 'METER', 'PAPER', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out, ['TWELVE METER PAPER LIST OF WORDS'])

        TestCls = TextJustifier(n_chars=20)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2, ['TWELVE METER PAPER ', 'LIST OF WORDS'])


    def test_text_lookup(self):

        # TextJoiner requires 2D and puts out 1D. TextLookup requires
        # 2D, so TJ could never directly feed into SR.
        pass


    def test_text_lookuprealtime(self):

        # TextJoiner requires 2D and puts out 1D. TextLookupRealTime
        # requires 2D, so TJ could never directly feed into SR.
        pass


    def test_text_normalizer(self):

        TJ = TextJoiner(sep=' ')
        out = TJ.fit_transform([['MORE', 'DEEP', 'FRIED', 'LONG', 'WORDS']])

        assert np.array_equal(out, ['MORE DEEP FRIED LONG WORDS'])

        TestCls = TextNormalizer(upper=False)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2, ['more deep fried long words'])


    def test_text_padder(self):

        # TextJoiner requires 2D and puts out 1D. TextPatter
        # requires 2D, so TJ could never directly feed into TP.
        pass


    def test_text_remover(self):

        TJ = TextJoiner(sep=' ')
        out = TJ.fit_transform([['THIS', 'CRAZY', 'LONG', 'SALAD', 'SHOOTER']])

        assert np.array_equal(out, ['THIS CRAZY LONG SALAD SHOOTER'])

        TestCls = TextRemover(remove='THIS CRAZY LONG SALAD SHOOTER')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2, [])


    def test_text_replacer(self):

        TJ = TextJoiner(sep=' ')
        out = TJ.fit_transform([['A', 'LIST', 'OF', 'FILTHY', 'WORDS']])

        assert np.array_equal(out, ['A LIST OF FILTHY WORDS'])

        TestCls = TextReplacer(replace=(('A LIST OF FILTHY WORDS', 'WHAT')))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2, ['WHAT'])


    def test_text_splitter(self):

        TJ = TextJoiner(sep=' ')
        out = TJ.fit_transform([['ANOTHER', 'SEQUENCE', 'OF', 'WORDS']])

        assert np.array_equal(out, ['ANOTHER SEQUENCE OF WORDS'])

        TestCls = TextSplitter(sep=(' ', '='))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['ANOTHER', 'SEQUENCE', 'OF', 'WORDS'])


    def test_text_stripper(self):

        TJ = TextJoiner(sep=' ')
        out = TJ.fit_transform(
            [['  A', 'VERY', '   LONG', 'LIST', 'OF   ', 'WORDS    ']]
        )

        assert np.array_equal(out, ['  A VERY    LONG LIST OF    WORDS    '])

        out2 = TextStripper().fit_transform(out)

        assert np.array_equal(out2, ['A VERY    LONG LIST OF    WORDS'])






