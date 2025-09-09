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



# Run an operation with TextStripper, then test all the other text modules are
# able to do an operation on mutated output as expected.



class TestUpstreamImpactOnLaterModules:


    def test_ngram_merger(self):

        TR = TextRemover(remove=('SORRY', 'OF'))
        out = TR.fit_transform([['A', 'SORRY', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'LIST', 'WORDS'])

        TestClass = NGramMerger(ngrams=(('LIST', 'WORDS'),), sep='_')

        out2 = TestClass.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'LIST_WORDS'])


    def test_stopremover(self):

        TR = TextRemover(remove=('TWELVE', 'METER'))
        out = TR.fit_transform([['TWELVE', 'METER', 'PAPER', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['PAPER', 'LIST', 'OF', 'WORDS'])

        TestCls = StopRemover(supplemental=['TWELVE', 'WORDS'])
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['PAPER', 'LIST'])


    def test_text_joiner(self):

        TR = TextRemover(remove=['  ANOTHER '])
        out = TR.fit_transform([['  ANOTHER ', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['LIST', 'OF', 'WORDS'])

        TestCls = TextJoiner(sep=' ')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2, ['LIST OF WORDS'])


    def test_text_justifier(self):

        TR = TextRemover(remove='more')
        out = TR.fit_transform([['more', 'deep', 'fried', 'long', 'words']])

        assert np.array_equal(out[0], ['deep', 'fried', 'long', 'words'])

        TestCls = TextJustifier(n_chars=20)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['deep', 'fried', 'long'])
        assert np.array_equal(out2[1], ['words'])


    def test_text_lookup(self):

        TR = TextRemover(remove=('PFDSLF',))
        out = TR.fit_transform([['A', 'LOT', 'OF', 'PFDSLF', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'LOT', 'OF', 'WORDS'])

        TestCls = TextLookup(
            update_lexicon=False, auto_delete=True, DELETE_ALWAYS=['WORDS']
        )
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'LOT', 'OF'])


    def test_text_lookuprealtime(self):

        TR = TextRemover(remove=('DAFSAS',))
        out = TR.fit_transform([['MORE', 'OF', 'FRIED ', 'DAFSAS', 'SALAD']])

        assert np.array_equal(out[0], ['MORE', 'OF', 'FRIED ', 'SALAD'])

        TestCls = TextLookupRealTime(update_lexicon=False, auto_delete=True)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['MORE', 'OF', 'SALAD'])


    def test_text_normalizer(self):

        TR = TextRemover(remove=['ABOUT'])
        out = TR.fit_transform([['LONG', 'LIST', 'SILLY', 'WORDS', 'ABOUT']])

        assert np.array_equal(out[0], ['LONG', 'LIST', 'SILLY', 'WORDS'])

        TestCls = TextNormalizer(upper=False)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['long', 'list', 'silly', 'words'])


    def test_text_padder(self):

        TR = TextRemover(remove=('SILLY', 'ABOUT'))
        out = TR.fit_transform([['LONG', 'LIST', 'SILLY'], ['WORDS', 'ABOUT']])

        assert np.array_equal(out[0], ['LONG', 'LIST'])
        assert np.array_equal(out[1], ['WORDS'])

        TestCls = TextPadder(fill='NULL')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['LONG', 'LIST'])
        assert np.array_equal(out2[1], ['WORDS', 'NULL'])


    def test_text_remover(self):

        TR = TextRemover(remove=('THIS', 'LONG'))
        out = TR.fit_transform([['THIS', 'CRAZY', 'LONG', 'SALAD', 'SHOOTER']])

        assert np.array_equal(out[0], ['CRAZY', 'SALAD', 'SHOOTER'])

        TestCls = TextRemover(remove=('CRAZY', 'SHOOTER'))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['SALAD'])


    def test_text_replacer(self):

        TR = TextRemover(remove=('a', 'filthy'))
        out = TR.fit_transform([['a', 'list', 'of', 'filthy', 'words']])

        assert np.array_equal(out[0], ['list', 'of', 'words'])

        TestCls = TextReplacer(replace=(('words', 'books'),))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['list', 'of', 'books'])


    def test_text_splitter(self):

        TR = TextRemover(remove=('another',))
        out = TR.fit_transform(['another', 'sequence of words'])

        assert np.array_equal(out, ['sequence of words'])

        TestCls = TextSplitter(sep=' ')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['sequence', 'of', 'words'])


    def test_text_stripper(self):

        TR = TextRemover(remove=(' LONG',))
        out = TR.fit_transform(['A ', ' LONG', 'LIST', ' OF ', '   WORDS'])

        assert np.array_equal(out, ['A ', 'LIST', ' OF ', '   WORDS'])

        out2 = TextStripper().fit_transform(out)

        assert np.array_equal(out2, ['A', 'LIST', 'OF', 'WORDS'])





