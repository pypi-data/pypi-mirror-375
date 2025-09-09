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



# Run an operation with NGramMerger, then test all the other text modules are
# able to do an operation on mutated output as expected.



class TestUpstreamImpactOnLaterModules:


    def test_ngram_merger(self):

        NGM = NGramMerger(ngrams=(('DEEP', 'FRIED', 'EGG'),), sep='_')
        out = NGM.fit_transform([['DEEP', 'FRIED', 'EGG', 'SALAD', 'SHOOTER']])

        assert np.array_equal(out[0], ['DEEP_FRIED_EGG', 'SALAD', 'SHOOTER'])

        TestCls = NGramMerger(ngrams=(('DEEP_FRIED_EGG', 'SALAD'),), sep='_')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['DEEP_FRIED_EGG_SALAD', 'SHOOTER'])


    def test_stop_remover(self):

        NGM = NGramMerger(ngrams=(('DEEP', 'FRIED', 'EGG'),), sep='_')
        out = NGM.fit_transform([['DEEP', 'FRIED', 'EGG', 'SALAD', 'SHOOTER']])

        assert np.array_equal(out[0], ['DEEP_FRIED_EGG', 'SALAD', 'SHOOTER'])

        TestCls = StopRemover(supplemental=['DEEP_FRIED_EGG', 'SHOOTER'])
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['SALAD'])


    def test_text_joiner(self):

        NGM = NGramMerger(ngrams=(('EGG', 'SALAD', 'SHOOTER'),), sep='_')
        out = NGM.fit_transform([['DEEP', 'FRIED', 'EGG', 'SALAD', 'SHOOTER']])

        assert np.array_equal(out[0], ['DEEP', 'FRIED', 'EGG_SALAD_SHOOTER'])

        TestCls = TextJoiner(sep='&')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2, ['DEEP&FRIED&EGG_SALAD_SHOOTER'])


    def test_text_justifier(self):

        NGM = NGramMerger(ngrams=(('FRIED', 'EGG', 'SALAD'),), sep='_')
        out = NGM.fit_transform(
            [['CHALLENGER', 'DEEP', 'FRIED', 'EGG', 'SALAD', 'SHOOTER']]
        )

        assert np.array_equal(
            out[0],
            ['CHALLENGER', 'DEEP', 'FRIED_EGG_SALAD', 'SHOOTER']
        )

        TestCls = TextJustifier(n_chars=25)
        out2 = TestCls.fit_transform(out)

        assert all(map(
            np.array_equal,
            out2,
            [['CHALLENGER', 'DEEP'], ['FRIED_EGG_SALAD', 'SHOOTER']]
        ))


    def test_text_lookup(self):

        NGM = NGramMerger(ngrams=(('EGG', 'SALAD', 'SHOOTER'),), sep='_')
        out = NGM.fit_transform(
            [['CHALLENGER', 'DEEP', 'FRIED', 'EGG', 'SALAD', 'SHOOTER']]
        )

        assert np.array_equal(
            out[0],
            ['CHALLENGER', 'DEEP', 'FRIED', 'EGG_SALAD_SHOOTER']
        )

        TestCls = TextLookup(update_lexicon=False, auto_delete=True)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['CHALLENGER', 'DEEP', 'FRIED'])


    def test_text_lookuprealtime(self):

        NGM = NGramMerger(ngrams=(('CHALLENGER', 'DEEP'),), sep='_')
        out = NGM.fit_transform(
            [['CHALLENGER', 'DEEP', 'FRIED', 'EGG', 'SALAD', 'SHOOTER']]
        )

        assert np.array_equal(
            out[0],
            ['CHALLENGER_DEEP', 'FRIED', 'EGG', 'SALAD', 'SHOOTER']
        )

        TestCls = TextLookupRealTime(update_lexicon=False, auto_delete=True)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['FRIED', 'EGG', 'SALAD', 'SHOOTER'])


    def test_text_normalizer(self):

        NGM = NGramMerger(ngrams=(('FRIED', 'EGG', 'SALAD'),), sep='_')
        out = NGM.fit_transform(
            [['CHALLENGER', 'DEEP', 'FRIED', 'EGG', 'SALAD', 'SHOOTER']]
        )

        assert np.array_equal(
            out[0],
            ['CHALLENGER', 'DEEP', 'FRIED_EGG_SALAD', 'SHOOTER']
        )

        TestCls = TextNormalizer(upper=False)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(
            out2[0],
            ['challenger', 'deep', 'fried_egg_salad', 'shooter']
        )


    def test_text_padder(self):

        NGM = NGramMerger(ngrams=(('FRIED', 'EGG'),), sep='_')
        out = NGM.fit_transform(
            [['CHALLENGER', 'DEEP'], ['FRIED', 'EGG', 'SALAD', 'SHOOTER']]
        )

        assert np.array_equal(out[0], ['CHALLENGER', 'DEEP'])
        assert np.array_equal(out[1], ['FRIED_EGG', 'SALAD', 'SHOOTER'])

        TestCls = TextPadder(fill='NULL')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['CHALLENGER', 'DEEP', 'NULL'])
        assert np.array_equal(out2[1], ['FRIED_EGG', 'SALAD', 'SHOOTER'])


    def test_text_remover(self):

        NGM = NGramMerger(ngrams=(('EGG', 'SALAD'),), sep='_')
        out = NGM.fit_transform(
            [['CHALLENGER', 'DEEP', 'FRIED', 'EGG', 'SALAD', 'SHOOTER']]
        )

        assert np.array_equal(
            out[0], ['CHALLENGER', 'DEEP', 'FRIED', 'EGG_SALAD', 'SHOOTER']
        )

        TestCls = TextRemover(remove=('CHALLENGER', 'EGG_SALAD'))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['DEEP', 'FRIED', 'SHOOTER'])



    def test_text_replacer(self):

        NGM = NGramMerger(ngrams=(('DEEP', 'FRIED', 'EGG'),), sep=' ')
        out = NGM.fit_transform(
            [['CHALLENGER', 'DEEP', 'FRIED', 'EGG', 'SALAD', 'SHOOTER']]
        )

        assert np.array_equal(
            out[0], ['CHALLENGER', 'DEEP FRIED EGG', 'SALAD', 'SHOOTER']
        )

        TestCls = TextReplacer(replace=(('DEEP FRIED EGG', 'BACON'),('ER', 'ING')))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['CHALLENGING', 'BACON', 'SALAD', 'SHOOTING'])


    def test_text_splitter(self):

        NGM = NGramMerger(ngrams=(('FRIED', 'EGG', 'SALAD'),), sep='=')
        out = NGM.fit_transform(
            [['CHALLENGER', 'DEEP', 'FRIED', 'EGG', 'SALAD', 'SHOOTER']]
        )

        # need to convert to 1D, TextSplitter requires 1D
        out = TextJoiner(sep=' ').fit_transform(out)

        assert np.array_equal(out, ['CHALLENGER DEEP FRIED=EGG=SALAD SHOOTER'])

        TestCls = TextSplitter(sep=(' ', '='))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(
            out2[0], ['CHALLENGER', 'DEEP', 'FRIED', 'EGG', 'SALAD', 'SHOOTER']
        )


    def test_text_stripper(self):

        NGM = NGramMerger(ngrams=(('   FRIED', 'EGG', 'SALAD   '),), sep='>')
        out = NGM.fit_transform(
            [['CHALLENGER', 'DEEP', '   FRIED', 'EGG', 'SALAD   ', 'SHOOTER']]
        )

        assert np.array_equal(
            out[0], ['CHALLENGER', 'DEEP',  '   FRIED>EGG>SALAD   ',  'SHOOTER']
        )

        out2 = TextStripper().fit_transform(out)

        assert np.array_equal(
            out2[0], ['CHALLENGER', 'DEEP',  'FRIED>EGG>SALAD',  'SHOOTER']
        )








