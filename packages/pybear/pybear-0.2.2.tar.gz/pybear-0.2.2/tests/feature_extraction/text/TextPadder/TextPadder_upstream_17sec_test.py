# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

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



# Run an operation with TextPadder, then test all the other text modules are
# able to do an operation on mutated output as expected.



class TestUpstreamImpactOnLaterModules:


    def test_ngram_merger(self):

        TP = TextPadder(fill='-')
        out = TP.fit_transform([['A', 'SORRY', 'LIST'], ['OF', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'SORRY', 'LIST'])
        assert np.array_equal(out[1], ['OF', 'WORDS', '-'])

        TestClass = NGramMerger(ngrams=(('SORRY', 'LIST'),), sep='_')

        out2 = TestClass.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'SORRY_LIST'])
        assert np.array_equal(out2[1], ['OF', 'WORDS', '-'])


    def test_stopremover(self):

        TP = TextPadder(fill='-')
        out = TP.fit_transform([['A', 'LONG', 'LIST'], ['OF', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'LONG', 'LIST'])
        assert np.array_equal(out[1], ['OF', 'WORDS', '-'])

        TestCls = StopRemover()
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['LIST'])
        assert np.array_equal(out2[1], ['WORDS', '-'])


    def test_text_joiner(self):

        TP = TextPadder(fill='@')
        out = TP.fit_transform([['ANOTHER', 'LIST', 'OF'], ['WORDS']])

        assert np.array_equal(out[0], ['ANOTHER', 'LIST', 'OF'])
        assert np.array_equal(out[1], ['WORDS', '@', '@'])

        TestCls = TextJoiner(sep=' ')
        out2 = TestCls.fit_transform(out)

        assert out2[0] == 'ANOTHER LIST OF'
        assert out2[1] == 'WORDS @ @'


    def test_text_justifier(self):

        TP = TextPadder(fill='!')
        out = TP.fit_transform([['ANOTHER', 'LIST', 'OF'], ['WORDS']])

        assert np.array_equal(out[0], ['ANOTHER', 'LIST', 'OF'])
        assert np.array_equal(out[1], ['WORDS', '!', '!'])

        TestCls = TextJustifier(n_chars=22, sep=' ')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['ANOTHER', 'LIST', 'OF', 'WORDS'])
        assert np.array_equal(out2[1], ['!', '!'])


    def test_text_lookup(self):

        TP = TextPadder(fill='EGZ')
        out = TP.fit_transform([['TAWDRY', 'LIST', 'OF'], ['WORDS']])

        assert np.array_equal(out[0], ['TAWDRY', 'LIST', 'OF'])
        assert np.array_equal(out[1], ['WORDS', 'EGZ', 'EGZ'])

        TestCls = TextLookup(update_lexicon=False, auto_delete=True)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['TAWDRY', 'LIST', 'OF'])
        assert np.array_equal(out2[1], ['WORDS'])


    def test_text_lookuprealtime(self):

        TP = TextPadder(fill='EGZ')
        out = TP.fit_transform([['TAWDRY', 'LIST', 'OF'], ['WORDS']])

        assert np.array_equal(out[0], ['TAWDRY', 'LIST', 'OF'])
        assert np.array_equal(out[1], ['WORDS', 'EGZ', 'EGZ'])


        TestCls = TextLookupRealTime(update_lexicon=False, auto_delete=True)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['TAWDRY', 'LIST', 'OF'])
        assert np.array_equal(out2[1], ['WORDS'])


    def test_text_normalizer(self):

        TP = TextPadder(fill='NULL')
        out = TP.fit_transform([['LONG', 'LIST', 'OF'], ['WORDS']])

        assert np.array_equal(out[0], ['LONG', 'LIST', 'OF'])
        assert np.array_equal(out[1], ['WORDS', 'NULL', 'NULL'])

        TN = TextNormalizer(upper=False)
        out2 = TN.fit_transform(out)

        assert np.array_equal(out2[0], ['long', 'list', 'of'])
        assert np.array_equal(out2[1], ['words', 'null', 'null'])


    def test_text_patter(self):

        TP = TextPadder(fill='NULL')
        out = TP.fit_transform([['LONG', 'LIST', 'OF'], ['WORDS']])

        assert np.array_equal(out[0], ['LONG', 'LIST', 'OF'])
        assert np.array_equal(out[1], ['WORDS', 'NULL', 'NULL'])

        TN = TextPadder(fill='null')
        out2 = TN.fit_transform(out)

        assert np.array_equal(out2[0], ['LONG', 'LIST', 'OF'])
        assert np.array_equal(out2[1], ['WORDS', 'NULL', 'NULL'])


    def test_text_remover(self):

        TP = TextPadder(fill='QQQ')
        out = TP.fit_transform([['another', 'list', 'of'], ['words']])

        assert np.array_equal(out[0], ['another', 'list', 'of'])
        assert np.array_equal(out[1], ['words', 'QQQ', 'QQQ'])

        TestCls = TextRemover(remove=('list', 'of', re.compile('Q+')))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['another'])
        assert np.array_equal(out2[1], ['words'])


    def test_text_replacer(self):

        TP = TextPadder(fill='!@#')
        out = TP.fit_transform([['RECORDING', 'OF', 'MANY'], ['EXPLICIT', 'WORDS']])

        assert np.array_equal(out[0], ['RECORDING', 'OF', 'MANY'])
        assert np.array_equal(out[1], ['EXPLICIT', 'WORDS', '!@#'])

        TestCls = TextReplacer(
            replace=(('ING', 'S'), ('WORDS', 'BOOKS'), ('!@#', ''))
        )
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['RECORDS', 'OF', 'MANY'])
        assert np.array_equal(out2[1], ['EXPLICIT', 'BOOKS', ''])


    def test_text_splitter(self):

        TP = TextPadder(fill='@')
        out = TP.fit_transform([['ANOTHER', 'LIST', 'OF'], ['WORDS']])

        assert np.array_equal(out[0], ['ANOTHER', 'LIST', 'OF'])
        assert np.array_equal(out[1], ['WORDS', '@', '@'])

        joined = TextJoiner(sep=' ').fit_transform(out)
        assert joined[0] == 'ANOTHER LIST OF'
        assert joined[1] == 'WORDS @ @'

        TestCls = TextSplitter(sep=(' ', '='))
        out2 = TestCls.fit_transform(joined)

        assert np.array_equal(out2[0], ['ANOTHER', 'LIST', 'OF'])
        assert np.array_equal(out2[1], ['WORDS', '@', '@'])


    def test_text_stripper(self):

        TP = TextPadder(fill='@')
        out = TP.fit_transform([['   ANOTHER', 'LIST', 'OF   '], ['WORDS    ']])

        assert np.array_equal(out[0], ['   ANOTHER', 'LIST', 'OF   '])
        assert np.array_equal(out[1], ['WORDS    ', '@', '@'])

        out2 = TextStripper().fit_transform(out)

        assert np.array_equal(out2[0], ['ANOTHER', 'LIST', 'OF'])
        assert np.array_equal(out2[1], ['WORDS', '@', '@'])




