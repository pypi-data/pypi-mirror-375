# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.feature_extraction.text._TextRemover._validation import _validation



class TestValidation:

    # the brunt of testing validation is handled by the individual validation
    # modules' tests

    # just make sure that it accepts all good parameters, and that the
    # conditionals for passing parameters are enforced.
    # 1) cannot pass 'flags' if 'remove' is not passed
    # 2) cannot pass 'case_sensitive' as a list if 'remove' is not passed


    @pytest.mark.parametrize('dim', (1, 2))
    @pytest.mark.parametrize('X_container', (list, tuple, np.ndarray))
    @pytest.mark.parametrize('remove, remove_container',
        (
            (None, None),
            (' ', None),
            ((' ', '\n', r'\s'), None),
            ('remove_seq_1', list),
            ('remove_seq_1', tuple)
        )
    )
    @pytest.mark.parametrize('case_sensitive, case_sensitive_container',
        (
            (True, None),
            (False, None),
            ('case_sensitive_seq_1', list),
            ('case_sensitive_seq_1', tuple)
        )
    )
    @pytest.mark.parametrize('flags, flags_container',
        (
            (None, None),
            (re.I | re.X, None),
            ('flags_seq_1', list),
            ('flags_seq_1', tuple)
        )
    )
    @pytest.mark.parametrize('remove_empty_rows', (True, False, 'garbage'))
    def test_accuracy(
        self, dim, X_container, remove, case_sensitive, flags, remove_empty_rows,
        remove_container, case_sensitive_container, flags_container
    ):

        _type_error = False
        _value_error = False


        remove_seq_1 = [
            (' ', ',', re.compile(re.escape('.'))),
            '',
            re.compile(re.escape('\n')),
            r'\s',
            None
        ]

        case_sensitive_seq_1 = [False, True, True, True, None]

        flags_seq_1 = [None, re.I, None, re.I | re.X, None]


        # manage dim of X and container -- -- -- -- -- -- -- -- -- -- --
        if dim == 1:
            _text_dim_1 = [
                'Despair thy charm, ',
                'And let the angel whom thou still hast served ',
                'Tell thee Macduff was ',
                "from his mother’s womb",
                "Untimely ripped."
            ]
            if X_container is np.ndarray:
                _X = np.array(_text_dim_1)
            else:
                _X = X_container(_text_dim_1)
            assert isinstance(_X, X_container)
        elif dim == 2:
            _text_dim_2 = [
                ['Despair', 'thy' 'charm, '],
                ['And', 'let', 'the', 'angel', 'whom', 'thou', 'still', 'hast' 'served '],
                ['Tell', 'thee', 'Macduff', 'was '],
                ['from', 'his', "mother’s", 'womb'],
                ['Untimely', 'ripped.']
            ]
            if X_container is np.ndarray:
                _X = np.fromiter(map(lambda x: np.array(x), _text_dim_2), dtype=object)
            else:
                _X = X_container(map(X_container, _text_dim_2))
            assert isinstance(_X, X_container)
            assert all(map(isinstance, _X, (X_container for _ in _X)))
        else:
            raise Exception
        # manage dim of X and container -- -- -- -- -- -- -- -- -- -- --

        # manage param containers, when applicable -- -- -- -- -- -- -- --
        if remove == 'remove_seq_1':
            remove = remove_container(remove_seq_1)
            assert isinstance(remove, remove_container)

        if case_sensitive == 'case_sensitive_seq_1':
            case_sensitive = case_sensitive_container(case_sensitive_seq_1)
            assert isinstance(case_sensitive, case_sensitive_container)

        if flags == 'flags_seq_1':
            flags = flags_container(flags_seq_1)
            assert isinstance(flags, flags_container)
        # END manage param containers, when applicable -- -- -- -- -- --

        # manage exceptions -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        if isinstance(remove, tuple) and len(remove) == 5:
            # need to distinguish between the valid tuple of patterns and
            # the list of patterns wrongfully passed as a tuple
            _type_error = True

        if isinstance(case_sensitive, list) and not remove:
            _value_error = True

        if isinstance(case_sensitive, (set, tuple)):
            _type_error = True

        if dim == 2 and not isinstance(remove_empty_rows, bool):
            _type_error = True

        if isinstance(flags, (set, tuple)):
            _type_error = True

        if flags is not None and not remove:
            _value_error = True
        # END manage exceptions -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _type_error or _value_error:
            with pytest.raises((TypeError, ValueError)):
                _validation(
                    _X,
                    _remove=remove,
                    _case_sensitive=case_sensitive,
                    _remove_empty_rows=remove_empty_rows,
                    _flags=flags
                )
        else:
            out = _validation(
                _X,
                _remove=remove,
                _case_sensitive=case_sensitive,
                _remove_empty_rows=remove_empty_rows,
                _flags=flags
            )

            assert out is None





