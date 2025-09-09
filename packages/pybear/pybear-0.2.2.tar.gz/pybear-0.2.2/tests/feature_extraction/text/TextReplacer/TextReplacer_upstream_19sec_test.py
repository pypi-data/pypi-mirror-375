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



# Run an operation with TextReplacer, then test all the other text modules are
# able to do an operation on mutated output as expected.



class TestUpstreamImpactOnLaterModules:


    def test_ngram_merger(self):

        TR = TextReplacer(replace=(('a', ''), ('sorry', 'sad')))
        out = TR.fit_transform([['a', 'sorry', 'list', 'of', 'words']])

        assert np.array_equal(out[0], ['', 'sad', 'list', 'of', 'words'])

        TestClass = NGramMerger(ngrams=(('sad', 'list'),), sep='_')

        out2 = TestClass.fit_transform(out)

        assert np.array_equal(out2[0], ['', 'sad_list', 'of', 'words'])


    def test_stopremover(self):

        TR = TextReplacer(replace=(('TWELVE', 'ELEVEN'),))
        out = TR.fit_transform([['TWELVE', 'METER', 'PAPER', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['ELEVEN', 'METER', 'PAPER', 'LIST', 'OF', 'WORDS'])

        TestCls = StopRemover(supplemental=['ELEVEN', 'WORDS'])
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['METER', 'PAPER', 'LIST'])


    def test_text_joiner(self):

        TR = TextReplacer(replace=(('ANOTHER', 'OTHER'),))
        out = TR.fit_transform([['ANOTHER', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['OTHER', 'LIST', 'OF', 'WORDS'])

        TestCls = TextJoiner(sep=' ')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2, ['OTHER LIST OF WORDS'])


    def test_text_justifier(self):

        TR = TextReplacer(replace=(('deep','pan'),))
        out = TR.fit_transform(['more deep fried long words'])

        assert np.array_equal(out, ['more pan fried long words'])

        TestCls = TextJustifier(n_chars=20)
        out2 = TestCls.fit_transform(out)

        assert out2[0] == 'more pan fried long '
        assert out2[1] == 'words'


    def test_text_lookup(self):

        TR = TextReplacer(replace=(('PFDSLF', 'SLOPPY'),))
        out = TR.fit_transform([['A', 'LOT', 'OF', 'PFDSLF', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'LOT', 'OF', 'SLOPPY', 'WORDS'])

        TestCls = TextLookup(
            update_lexicon=False, auto_delete=True, DELETE_ALWAYS=['SLOPPY']
        )
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'LOT', 'OF', 'WORDS'])


    def test_text_lookuprealtime(self):

        TR = TextReplacer(replace=((re.compile('[^a-z0-9]', re.I), ''),))
        out = TR.fit_transform([['MORE', 'OF', 'FRIED', '#($^#($', ' SALAD']])

        assert np.array_equal(out[0], ['MORE', 'OF', 'FRIED', '', 'SALAD'])

        TestCls = TextLookupRealTime(
            update_lexicon=False, auto_delete=True, DELETE_ALWAYS=['']
        )
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['MORE', 'OF', 'FRIED', 'SALAD'])


    def test_text_normalizer(self):

        TR = TextReplacer(replace=(('ABOUT', 'ABOUND'),))
        out = TR.fit_transform(['LONG LIST SILLY WORDS ABOUT'])

        assert np.array_equal(out, ['LONG LIST SILLY WORDS ABOUND'])

        TestCls = TextNormalizer(upper=False)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2, ['long list silly words abound'])


    def test_text_padder(self):

        TR = TextReplacer(replace=(('LONG', 'SHORT'),))
        out = TR.fit_transform([['LONG', 'LIST', 'SILLY'], ['WORDS', 'ABOUT']])

        assert np.array_equal(out[0], ['SHORT', 'LIST', 'SILLY'])
        assert np.array_equal(out[1], ['WORDS', 'ABOUT'])

        TestCls = TextPadder(fill='NOTHING')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['SHORT', 'LIST', 'SILLY'])
        assert np.array_equal(out2[1], ['WORDS', 'ABOUT', 'NOTHING'])


    def test_text_remover(self):

        TR = TextReplacer(replace=((re.compile('[^a-z0-9]', re.I), ''),))
        out = TR.fit_transform([[' THIS', '%@CRAZY##$', 'LONG', '(*&(%)', 'SHOOTER']])

        assert np.array_equal(out[0], ['THIS', 'CRAZY', 'LONG', '', 'SHOOTER'])

        TestCls = TextRemover(remove=('', 'CRAZY'))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['THIS', 'LONG', 'SHOOTER'])


    def test_text_replacer(self):

        TR = TextReplacer(replace=(('filthy', 'clean'),))
        out = TR.fit_transform([['a', 'list', 'of', 'filthy', 'words']])

        assert np.array_equal(out[0], ['a', 'list', 'of', 'clean', 'words'])

        TestCls = TextReplacer(replace=(('clean', 'dirty'), ('words', 'towels')))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['a', 'list', 'of', 'dirty', 'towels'])


    def test_text_splitter(self):

        TR = TextReplacer(replace=((re.compile('[^a-z0-9]', re.I), ' '),))
        out = TR.fit_transform(['DATA-ENGINEER'])

        assert np.array_equal(out, ['DATA ENGINEER'])

        TestCls = TextSplitter(sep=re.compile('\s'))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['DATA', 'ENGINEER'])


    def test_text_stripper(self):

        TR = TextReplacer(replace=((' LONG ', ' SHORT '),))
        out = TR.fit_transform(['A ', ' VERY', ' LONG ', '  LIST', 'OF ', ' WORDS '])

        assert np.array_equal(
            out, ['A ', ' VERY', ' SHORT ', '  LIST', 'OF ', ' WORDS ']
        )

        out2 = TextStripper().fit_transform(out)

        assert np.array_equal(out2, ['A', 'VERY', 'SHORT', 'LIST', 'OF', 'WORDS'])





