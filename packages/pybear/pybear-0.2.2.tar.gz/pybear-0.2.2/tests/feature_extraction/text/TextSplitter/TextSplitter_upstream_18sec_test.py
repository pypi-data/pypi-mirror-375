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



# Run an operation with TextSplitter, then test all the other text modules are
# able to do an operation on mutated output as expected.



class TestUpstreamImpactOnLaterModules:


    def test_ngram_merger(self):

        TS = TextSplitter(sep=' ')
        out = TS.fit_transform(['a sorry list of words'])

        assert np.array_equal(out[0], ['a', 'sorry', 'list', 'of', 'words'])

        TestClass = NGramMerger(ngrams=(('sorry', 'list'),), sep='_')

        out2 = TestClass.fit_transform(out)

        assert np.array_equal(out2[0], ['a', 'sorry_list', 'of', 'words'])


    def test_stopremover(self):

        TS = TextSplitter(sep=' ')
        out = TS.fit_transform(['TWELVE METER PAPER LIST OF WORDS'])

        assert np.array_equal(
            out[0], ['TWELVE', 'METER', 'PAPER', 'LIST', 'OF', 'WORDS']
        )

        TestCls = StopRemover(supplemental=['TWELVE', 'WORDS'])
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['METER', 'PAPER', 'LIST'])


    def test_text_joiner(self):

        TS = TextSplitter(sep=' ')
        out = TS.fit_transform(['ANOTHER LIST OF WORDS'])

        assert np.array_equal(out[0], ['ANOTHER', 'LIST', 'OF', 'WORDS'])

        TestCls = TextJoiner(sep=' ')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2, ['ANOTHER LIST OF WORDS'])


    def test_text_justifier(self):

        TS = TextSplitter(sep=' ')
        out = TS.fit_transform(['more deep fried long words'])

        assert np.array_equal(out[0], ['more', 'deep', 'fried', 'long', 'words'])

        TestCls = TextJustifier(n_chars=20)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['more', 'deep', 'fried'])
        assert np.array_equal(out2[1], ['long', 'words'])


    def test_text_lookup(self):

        TS = TextSplitter(sep=' ')
        out = TS.fit_transform(['A LOT OF PFDSLF WORDS'])

        assert np.array_equal(out[0], ['A', 'LOT', 'OF', 'PFDSLF', 'WORDS'])

        TestCls = TextLookup(
            update_lexicon=False, auto_delete=True, DELETE_ALWAYS=['PFDSLF']
        )
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'LOT', 'OF', 'WORDS'])


    def test_text_lookuprealtime(self):

        TS = TextSplitter(sep=' ')
        out = TS.fit_transform(['MORE OF FRIED DAFSAS SALAD'])

        assert np.array_equal(out[0], ['MORE', 'OF', 'FRIED', 'DAFSAS', 'SALAD'])

        TestCls = TextLookupRealTime(update_lexicon=False, auto_delete=True)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['MORE', 'OF', 'FRIED', 'SALAD'])


    def test_text_normalizer(self):

        TS = TextSplitter(sep=' ')
        out = TS.fit_transform(['LONG LIST SILLY WORDS ABOUT'])

        assert np.array_equal(out[0], ['LONG', 'LIST', 'SILLY', 'WORDS', 'ABOUT'])

        TestCls = TextNormalizer(upper=False)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['long', 'list', 'silly', 'words', 'about'])


    def test_text_padder(self):

        TS = TextSplitter(sep=' ')
        out = TS.fit_transform(['LONG LIST SILLY', 'WORDS ABOUT'])

        assert np.array_equal(out[0], ['LONG', 'LIST', 'SILLY'])
        assert np.array_equal(out[1], ['WORDS', 'ABOUT'])

        TestCls = TextPadder(fill='NULL')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['LONG', 'LIST', 'SILLY'])
        assert np.array_equal(out2[1], ['WORDS', 'ABOUT', 'NULL'])


    def test_text_remover(self):

        TS = TextSplitter(sep=' ')
        out = TS.fit_transform(['THIS CRAZY LONG SALAD SHOOTER'])

        assert np.array_equal(out[0], ['THIS', 'CRAZY', 'LONG', 'SALAD', 'SHOOTER'])

        TestCls = TextRemover(remove=('CRAZY', 'SHOOTER'))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['THIS', 'LONG', 'SALAD'])


    def test_text_replacer(self):

        TS = TextSplitter(sep=' ')
        out = TS.fit_transform(['a list of filthy words'])

        assert np.array_equal(out[0], ['a', 'list', 'of', 'filthy', 'words'])

        TestCls = TextReplacer(replace=(('filthy', 'holy'), ('words', 'books')))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['a', 'list', 'of', 'holy', 'books'])


    def test_text_splitter(self):

        TS = TextSplitter(sep=' ')
        out = TS.fit_transform(['another sequence of words'])

        assert out[0] == ['another', 'sequence', 'of', 'words']

        # TextSplitter needs 1D, so rejoin the previously split
        joined = TextJoiner(sep=' ').fit_transform(out)
        assert np.array_equal(joined, ['another sequence of words'])

        TestCls = TextSplitter(sep=' ')
        out2 = TestCls.fit_transform(joined)

        assert np.array_equal(out2[0], ['another', 'sequence', 'of', 'words'])


    def test_text_stripper(self):

        TS = TextSplitter(sep=' ')
        out = TS.fit_transform(['A VERY  LONG LIST OF    WORDS'])

        assert np.array_equal(
            out[0], ['A', 'VERY', '', 'LONG', 'LIST', 'OF', '', '', '', 'WORDS']
        )

        out2 = TextStripper().fit_transform(out)

        assert np.array_equal(
            out2[0], ['A', 'VERY', '', 'LONG', 'LIST', 'OF', '', '', '', 'WORDS']
        )



