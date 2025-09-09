# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text.__shared._utilities._view_text_snippet \
    import view_text_snippet



class TestViewSnippet:


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    @pytest.mark.parametrize('junk_vector',
        (-2.7, -1, 0, 1, 2.7, True, None, 'junk', [0,1], (1,), {1,2}, {'a':1},
         lambda x: x)
    )
    def test_rejects_junk_vector(self, junk_vector):

        with pytest.raises(TypeError):
            view_text_snippet(junk_vector, 0)


    @pytest.mark.parametrize('junk_idx',
        (-2.7, 2.7, True, False, None, 'junk', [0,1], (1,), {1,2}, {'a':1},
         lambda x: x)
    )
    def test_rejects_junk_idx(self, junk_idx):

        with pytest.raises(TypeError):
            view_text_snippet(list('abcde'), junk_idx)


    @pytest.mark.parametrize('bad_idx', (-1, 10, 250000))
    def test_rejects_bad_idx(self, bad_idx):

        with pytest.raises(ValueError):
            view_text_snippet(list('abcde'), bad_idx)


    @pytest.mark.parametrize('junk_span',
        (-2.7, 2.7, True, False, None, 'junk', [0,1], (1,), {1,2}, {'a':1},
         lambda x: x)
    )
    def test_rejects_junk_span(self, junk_span):

        with pytest.raises(TypeError):
            view_text_snippet(list('abcde'), 0, _span=junk_span)


    @pytest.mark.parametrize('bad_span', (-1, 0, 1, 2))
    def test_rejects_bad_span(self, bad_span):

        with pytest.raises(ValueError):
            view_text_snippet(list('abcde'), 0, _span=bad_span)

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    @pytest.mark.parametrize('all_caps', (True, False))
    @pytest.mark.parametrize('vector_len', (1, 2, 4, 8))
    @pytest.mark.parametrize('idx', (0, 1, 4, 8))
    @pytest.mark.parametrize('span', (3, 5, 9))
    def test_accuracy(self, all_caps, vector_len, idx, span):

        if idx >= vector_len:
            pytest.skip(reason=f'failure condition')

        VECTOR = list('abcdefghijklmnop')[:vector_len]

        if all_caps:
            VECTOR = list(map(str.upper, VECTOR))


        out = view_text_snippet(
            VECTOR,
            _idx = idx,
            _span = span
        )


        assert isinstance(out, str)

        split_out = out.split(sep=' ')


        if vector_len == 1:
            # could only happen if idx == 0
            assert idx == 0
            assert len(split_out) == vector_len
            assert np.array_equal(split_out, ['A'])
        elif vector_len == 2:
            # span is always greater than vector_len for this
            # should only happen for idx in [0, 1]
            assert idx in [0, 1]
            assert len(split_out) == vector_len
            if idx == 0:
                assert np.array_equal(split_out, ['A', 'b'])
            elif idx == 1:
                assert np.array_equal(split_out, ['a', 'B'])
            else:
                raise Exception
        elif vector_len == 4:
            # should only happen for idx in [0, 1]
            assert idx in [0, 1]
            if span == 3:
                assert len(split_out) == span
                if idx == 0:
                    assert np.array_equal(split_out, ['A', 'b', 'c'])
                elif idx == 1:
                    assert np.array_equal(split_out, ['a', 'B', 'c'])
                else:
                    raise Exception
            else:   # 5, 9
                assert len(split_out) == vector_len
                if idx == 0:
                    assert np.array_equal(split_out, ['A', 'b', 'c', 'd'])
                elif idx == 1:
                    assert np.array_equal(split_out, ['a', 'B', 'c', 'd'])
        elif vector_len == 8:
            # should only happen for idx in [0, 1, 4]
            assert idx in [0, 1, 4]
            if span == 3:
                assert len(split_out) == span
                if idx == 0:
                    assert np.array_equal(split_out, ['A', 'b', 'c'])
                elif idx == 1:
                    assert np.array_equal(split_out, ['a', 'B', 'c'])
                elif idx == 4:
                    assert np.array_equal(split_out, ['d', 'E', 'f'])
                else:
                    raise Exception
            elif span == 5:
                assert len(split_out) == span
                if idx == 0:
                    assert np.array_equal(split_out, ['A', 'b', 'c', 'd', 'e'])
                elif idx == 1:
                    assert np.array_equal(split_out, ['a', 'B', 'c', 'd', 'e'])
                elif idx == 4:
                    assert np.array_equal(split_out, ['c', 'd', 'E', 'f', 'g'])
                else:
                    raise Exception
            elif span == 9:
                assert len(split_out) == vector_len
                if idx == 0:
                    assert np.array_equal(split_out, ['A'] + list('bcdefgh'))
                elif idx == 1:
                    assert np.array_equal(split_out, ['a'] + ['B'] + list('cdefgh'))
                elif idx == 4:
                    assert np.array_equal(split_out, list('abcd') + ['E'] + list('fgh'))
                else:
                    raise Exception
            else:
                assert len(split_out) == span
        else:
            raise Exception







