# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numbers
import uuid

import numpy as np

from pybear.feature_extraction.text._Lexicon.Lexicon import Lexicon



# there is no 'fit', everything should be accessible at initialization
class TestAttrAccess:


    # _attrs
    # [
    #     'size_',
    #     'lexicon_',
    #     'stop_words_',
    #     'overall_statistics_',
    #     'startswith_frequency_',
    #     'character_frequency_',
    #     'string_frequency_',
    #     'uniques_'
    # ]


    def test_attr_access(self):

        TestCls = Lexicon()


        # 'size_',
        out = getattr(TestCls, 'size_')
        assert isinstance(out, int)
        assert out >= 1

        # 'lexicon_',
        out = getattr(TestCls, 'lexicon_')
        assert isinstance(out, list)
        assert len(out) >= 1
        assert all(map(isinstance, out, (str for _ in out)))
        assert len(out) == TestCls.size_

        # 'stop_words_',
        out = getattr(TestCls, 'stop_words_')
        assert isinstance(out, list)
        assert len(out) >= 1
        assert all(map(isinstance, out, (str for _ in out)))

        # 'overall_statistics_',
        out = getattr(TestCls, 'overall_statistics_')
        assert isinstance(out, dict)
        assert all(map(isinstance, out, (str for _ in out)))
        for key in ['size', 'uniques_count', 'max_length', 'min_length']:
            assert key in out
        assert all(map(
            isinstance, out.values(),
            (numbers.Real for _ in out)
        ))

        # 'startswith_frequency_',
        out = getattr(TestCls, 'startswith_frequency_')
        assert isinstance(out, dict)
        assert all(map(isinstance, out, (str for _ in out)))
        assert all(map(lambda x: len(x) == 1, out))
        assert all(map(
            isinstance, out.values(), (numbers.Integral for _ in out)
        ))
        assert all(map(lambda x: x >= 1, out.values()))

        # 'character_frequency_',
        out = getattr(TestCls, 'character_frequency_')
        assert isinstance(out, dict)
        assert all(map(isinstance, out, (str for _ in out)))
        assert all(map(lambda x: len(x) == 1, out))
        assert all(map(
            isinstance, out.values(), (numbers.Integral for _ in out)
        ))
        assert all(map(lambda x: x >= 1, out.values()))

        # 'string_frequency_',
        out = getattr(TestCls, 'string_frequency_')
        assert isinstance(out, dict)
        assert all(map(isinstance, out, (str for _ in out)))
        assert all(map(
            isinstance, out.values(), (numbers.Integral for _ in out)
        ))

        # 'uniques_'
        out = getattr(TestCls, 'uniques_')
        assert isinstance(out, list)
        assert len(out) >= 1
        assert all(map(isinstance, out, (str for _ in out)))
        assert len(out) == TestCls.size_


        del TestCls



class TestMethodAccess:


    # methods
    # [
    #     '_reset',   # blocked
    #     'get_params',  # blocked
    #     'partial_fit',  # blocked
    #     'fit',   # blocked
    #     'transform'   # blocked
    #     'score'   # blocked
    #     'print_overall_statistics',
    #     'print_startswith_frequency',
    #     'print_character_frequency',
    #     'print_string_frequency',
    #     'get_longest_strings',
    #     'print_longest_strings',
    #     'get_shortest_strings',
    #     'print_shortest_strings',
    #     'lookup_substring',
    #     'lookup_string',
    # ]



    def test_method_access(self):


        TestCls = Lexicon()

        _X = [str(uuid.uuid4())[:5] for _ in range(100)]

        # blocked ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # '_reset'   # blocked
        with pytest.raises(AttributeError):
            getattr(TestCls, '_reset')()

        # 'get_params'  # blocked
        with pytest.raises(AttributeError):
            getattr(TestCls, 'get_params')()

        # 'partial_fit'  # blocked
        with pytest.raises(AttributeError):
            getattr(TestCls, 'partial_fit')(_X)

        # 'fit'   # blocked
        with pytest.raises(AttributeError):
            getattr(TestCls, 'fit')(_X)

        # 'transform'   # blocked
        with pytest.raises(AttributeError):
            getattr(TestCls, 'transform')(_X)

        # 'score'   # blocked
        with pytest.raises(AttributeError):
            getattr(TestCls, 'score')(_X)

        # END blocked ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

        # 'find_duplicates'
        out = getattr(TestCls, 'find_duplicates')()
        assert isinstance(out, dict)
        assert len(out) == 0

        # 'check_order'
        out = getattr(TestCls, 'check_order')()
        assert isinstance(out, list)
        assert len(out) == 0

        # 'add_words'
        assert getattr(TestCls, 'add_words')('APPLE') is None

        # 'delete_words'
        assert getattr(TestCls, 'delete_words')('ZYZCZCK') is None

        # 'print_overall_statistics'
        assert getattr(TestCls, 'print_overall_statistics')() is None

        # 'print_startswith_frequency'
        assert getattr(TestCls, 'print_startswith_frequency')() is None

        # 'print_character_frequency'
        assert getattr(TestCls, 'print_character_frequency')() is None

        # 'print_string_frequency'
        assert getattr(TestCls, 'print_string_frequency')(n=10) is None

        # 'get_longest_strings'
        out = getattr(TestCls, 'get_longest_strings')(n=10)
        assert isinstance(out, dict)
        assert all(map(isinstance, out, (str for _ in out)))
        assert all(map(
            isinstance, out.values(), (numbers.Integral for _ in out)
        ))

        # 'print_longest_strings'
        assert getattr(TestCls, 'print_longest_strings')(n=10) is None

        # 'get_shortest_strings'
        out = getattr(TestCls, 'get_shortest_strings')(n=10)
        assert isinstance(out, dict)
        assert all(map(isinstance, out, (str for _ in out)))
        assert all(map(
            isinstance, out.values(), (numbers.Integral for _ in out)
        ))

        # 'print_shortest_strings'
        assert getattr(TestCls, 'print_shortest_strings')(n=10) is None

        # 'lookup_substring'
        out = getattr(TestCls, 'lookup_substring')('AARD')
        assert isinstance(out, list)
        assert all(map(isinstance, out, (str for _ in out)))
        assert np.array_equiv(
            out,
            ["AARDVARK", "AARDVARKS", "AARDWOLF", "AARDWOLVES"]
        )

        out = TestCls.lookup_substring('pxlq')
        assert isinstance(out, list)
        assert np.array_equiv(out, [])


        # 'lookup_string'
        out = getattr(TestCls, 'lookup_string')('AARDVARK')
        assert isinstance(out, list)
        assert np.array_equal(out, ['AARDVARK'])

        out = getattr(TestCls, 'lookup_string')('pxlq')
        assert isinstance(out, list)
        assert len(out) == 0






