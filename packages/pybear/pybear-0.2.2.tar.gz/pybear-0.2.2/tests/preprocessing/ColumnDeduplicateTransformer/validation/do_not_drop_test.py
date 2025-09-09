# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.preprocessing._ColumnDeduplicator._validation. \
    _do_not_drop import _val_do_not_drop



class TestDoNotDrop:


    # pl always has str column names, even if not passed at construction
    @pytest.mark.parametrize('_columns_is_passed', (True, False))
    @pytest.mark.parametrize('junk_dnd',
        (-1, 0, 1, 3.14, True, 'trash', {'a':1}, max, lambda x: x)
    )
    def test_rejects_not_list_like_or_none(
        self, _shape, _columns, _columns_is_passed, junk_dnd
    ):

        with pytest.raises(TypeError):
            _val_do_not_drop(
                junk_dnd,
                _shape[1],
                _columns if _columns_is_passed else None
            )


    @pytest.mark.parametrize('_columns_is_passed', (True, False), scope='module')
    @pytest.mark.parametrize('bad_dnd',
        (
            [True, min, 3.14],
            [min, max, float],
            [2.718, 3.141, 8.834],
            []
        )
    )
    def test_rejects_bad_list(
        self, _shape, _columns, _columns_is_passed, bad_dnd
    ):

        with pytest.raises(TypeError):
            _val_do_not_drop(
                bad_dnd,
                _shape[1],
                _columns if _columns_is_passed else None
            )


    def test_str_handing(self, _shape, _columns):

        # rejects str when columns is none
        with pytest.raises(TypeError):
            _val_do_not_drop(
                [v for i,v in enumerate(_columns) if i%2==0],
                _shape[1],
                _columns=None
            )

        # accepts good str when columns not none
        _val_do_not_drop(
            [v for i, v in enumerate(_columns) if i % 2 == 0],
            _shape[1],
            _columns
        )

        # rejects bad str when columns not none
        with pytest.raises(TypeError):
            _val_do_not_drop(
                ['a', 'b'],
                _shape[1],
                None
            )


    @pytest.mark.parametrize('_columns_is_passed', (True, False), scope='module')
    def test_int_and_none_handling(self, _columns_is_passed, _columns, _shape):

        # accepts good int always
        _val_do_not_drop(
            [0, 1],
            _shape[1],
            _columns if _columns_is_passed else None
        )

        # rejects bad int always - 1
        with pytest.raises(ValueError):
            _val_do_not_drop(
                [-1, 1],
                _shape[1],
                _columns if _columns_is_passed else None
            )

        # rejects bad int always - 2
        with pytest.raises(ValueError):
            _val_do_not_drop(
                [0, _shape[1]],
                _shape[1],
                _columns if _columns_is_passed else None
            )

        # accepts None always
        _val_do_not_drop(
            None,
            _shape[1],
            _columns if _columns_is_passed else None
        )



