# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numpy as np

import pytest

from pybear.feature_extraction.text._TextStatistics._partial_fit. \
    _build_string_frequency import _build_string_frequency



class TestBuildStringFrequency:


    @pytest.mark.parametrize('junk_STRINGS',
        (-2.7, -1, 0, 1, 2.7, True, False, None, 'trash', [0,1], (1,),
         {'a': 1}, lambda x: x)
    )
    def test_junk_strings(self, junk_STRINGS):

        with pytest.raises(TypeError):
            _build_string_frequency(
                junk_STRINGS,
                case_sensitive=False
            )


    @pytest.mark.parametrize('junk_case_sensitive',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [0,1], (1,), {'a': 1}, lambda x: x)
    )
    def test_junk_case_sensitive(self, junk_case_sensitive):

        with pytest.raises(TypeError):
            _build_string_frequency(
                ['A', 'BE', 'TWO', 'FOUR', 'SEVEN', 'ELEVEN', 'FIFTEEN'],
                case_sensitive=junk_case_sensitive
            )


    @pytest.mark.parametrize('case_sensitive', (True, False))
    def test_accuracy(self, case_sensitive):

        STRINGS = ['A', 'BE', 'TWO', 'FOUR', 'SEVEN', 'ELEVEN', 'FIFTEEN']

        out = _build_string_frequency(
            STRINGS,
            case_sensitive=case_sensitive
        )

        assert isinstance(out, dict)
        for k, v in out.items():
            assert isinstance(k, str)
            assert not isinstance(k, np.str_)
            assert isinstance(v, int)
            assert not isinstance(v, np.int32)

        assert np.array_equal(
            sorted(list(out.keys())),
            sorted(STRINGS)
        )

        assert all(map(lambda x: x==1, out.values()))

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        STRINGS = ['a', 'be', 'two', 'for', 'seven', 'eleven', 'fifteen']

        out = _build_string_frequency(
            STRINGS,
            case_sensitive=case_sensitive
        )

        assert isinstance(out, dict)
        for k, v in out.items():
            assert isinstance(k, str)
            assert not isinstance(k, np.str_)
            assert isinstance(v, int)
            assert not isinstance(v, np.int32)

        if case_sensitive:
            assert np.array_equal(
                sorted(list(out.keys())),
                sorted(STRINGS)
            )
        elif not case_sensitive:
            assert np.array_equal(
                sorted(list(out.keys())),
                sorted(map(str.upper, STRINGS))
            )

        assert all(map(lambda x: x==1, out.values()))


        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        STRINGS = ['one', 'ONE', 'two', 'TWO', 'two', 'TWO', 'THREE']

        out = _build_string_frequency(
            STRINGS,
            case_sensitive=case_sensitive
        )

        assert isinstance(out, dict)
        for k, v in out.items():
            assert isinstance(k, str)
            assert not isinstance(k, np.str_)
            assert isinstance(v, int)
            assert not isinstance(v, np.int32)

        if case_sensitive:
            assert np.array_equal(
                sorted(list(out.keys())),
                sorted(['one', 'ONE', 'two', 'TWO', 'THREE'])
            )
            assert out['one'] == 1
            assert out['ONE'] == 1
            assert out['two'] == 2
            assert out['TWO'] == 2
            assert out['THREE'] == 1

        elif not case_sensitive:
            assert np.array_equal(
                list(out.keys()),
                sorted(['ONE', 'TWO', 'THREE'])
            )

            assert out['ONE'] == 2
            assert out['TWO'] == 4
            assert out['THREE'] == 1





