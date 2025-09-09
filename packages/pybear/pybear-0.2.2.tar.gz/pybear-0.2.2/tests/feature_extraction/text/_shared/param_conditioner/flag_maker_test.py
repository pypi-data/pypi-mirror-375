# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

from pybear.feature_extraction.text.__shared._param_conditioner. \
    _flag_maker import _flag_maker



class TestFlagMaker:


    # def _flag_maker(
    #     _remove: list[list[None] | list[re.Pattern]],
    #     _case_sensitive: CaseSensitiveType,
    #     _flags: FlagsType
    # ) -> list[list[None] | list[re.Pattern]]:


    # _remove must be list[list[None] | list[re.Pattern]]
    # _case_sensitive can be bool | list[None | bool]
    # _flags can be None | int | list[None | int]

    # minimal validation


    # _case_sensitive can be bool | list[None | bool]
    # _flags can be None | int | list[None | int]
    @pytest.mark.parametrize('_cs', (True, False, [True, None, False, None]))
    @pytest.mark.parametrize('_flags', (None, re.I, [None, re.M, None, None]))
    def test_accuracy(self, _cs, _flags):

        _remove = [
            [None],
            # user passed compile
            [re.compile('abc', re.I)],
            # user passed literal strings
            [re.compile(re.escape('def')), re.compile(re.escape('ghi'))],
            [None]
        ]

        out = _flag_maker(_remove, _cs, _flags)

        # convert whatever was passed to _cs & _flags to list for
        # easier checks, and convert to re.flag equivalent
        _ref_cs = []
        _ref_flags = []
        for idx in range(len(_remove)):
            if isinstance(_cs, bool):
                if _cs is True:
                    _ref_cs.append(0)
                elif _cs is False:
                    _ref_cs.append(re.I)
                else:
                    raise Exception
            elif isinstance(_cs, list):
                if _cs[idx] is None or _cs[idx] is True:
                    _ref_cs.append(0)
                elif _cs[idx] is False:
                    _ref_cs.append(re.I)
                else:
                    raise Exception
            else:
                raise Exception

            if isinstance(_flags, (type(None), type(re.X))):
                _ref_flags.append(0)
            elif isinstance(_flags, list):
                if _flags[idx] is None:
                    _ref_flags.append(0)
                elif isinstance(_flags[idx], int):
                    _ref_flags.append(_flags[idx])
                else:
                    raise Exception
            else:
                raise Exception

        assert len(_ref_cs) == len(_remove)
        assert len(_ref_flags) == len(_remove)
        # END MAKE cs & flags REF OBJECTS -- -- -- -- -- -- -- -- -- --

        # merge the flags from _ref_cs and _ref_flags
        _ref_flags = [_ref_cs[i] | _ref_flags[i] for i in range(len(_ref_flags))]

        # case_sensitive doesnt matter anymore, just look at pattern and flags
        assert isinstance(out, list)
        for idx, row in enumerate(out):
            assert isinstance(row, list)
            assert len(row) == len(_remove[idx])
            for idx2, re_compile in enumerate(row):

                if _remove[idx][idx2] is None:
                    assert re_compile is None
                    continue

                _og_pattern = _remove[idx][idx2].pattern
                _og_flags = _remove[idx][idx2].flags
                _new_flags = _og_flags | _ref_flags[idx]
                assert re_compile.pattern == _og_pattern
                assert re_compile.flags == _new_flags







