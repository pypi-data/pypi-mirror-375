# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from copy import deepcopy

from pybear.preprocessing._ColumnDeduplicator._partial_fit. \
    _identify_idxs_to_delete import _identify_idxs_to_delete

from pybear.preprocessing._ColumnDeduplicator._partial_fit. \
    _lock_in_random_idxs import _lock_in_random_idxs



# def _identify_idxs_to_delete(
#     _duplicates: list[list[int]],
#     _keep: Literal['first', 'last', 'random'],
#     _do_not_drop: Sequence[int] | Sequence[str] | None,
#     _columns: Sequence[str] | None,
#     _conflict: Literal['raise', 'ignore'],
#     _rand_idxs: tuple[int]
# ) -> dict[int, int]:



@pytest.fixture(scope='module')
def _iitd_args(_columns):
    return {
        '_duplicates': [[0,1], [2,3]],
        '_keep': 'first',
        '_do_not_drop': [0, 1],
        '_columns': _columns,
        '_conflict': 'ignore',
        '_rand_idxs': (1, 3) # len and numbers must match _duplicates
    }



class TestIITDValidation:

    # test validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # ------------------------------
    @pytest.mark.parametrize('junk_duplicates',
        (-1,0,1,3.14,None,True,False,[0,1],(0,1),(0,),{'a':1}, min, lambda x: x)
    )
    def test_rejects_junk_duplicates(self, junk_duplicates, _iitd_args):

        _new_args = deepcopy(_iitd_args)
        _new_args['_duplicates'] = junk_duplicates

        with pytest.raises(AssertionError):
            _identify_idxs_to_delete(**_new_args)


    @pytest.mark.parametrize('bad_duplicates',
        ([['a','b'], ['c','d']], [[2,2],[2,2]])
    )
    def test_rejects_bad_duplicates(self, bad_duplicates, _iitd_args):

        _new_args = deepcopy(_iitd_args)
        _new_args['_duplicates'] = bad_duplicates

        with pytest.raises(AssertionError):
            _identify_idxs_to_delete(**_new_args)

    # ------------------------------

    # ------------------------------
    @pytest.mark.parametrize('junk_keep',
        (-1,0,1,3.14,None,True,False,[0,1],(0,),{'a':1}, min, lambda x: x)
    )
    def test_rejects_junk_keep(self, junk_keep, _iitd_args):

        _new_args = deepcopy(_iitd_args)
        _new_args['_keep'] = junk_keep

        with pytest.raises(AssertionError):
            _identify_idxs_to_delete(**_new_args)


    @pytest.mark.parametrize('bad_keep', ('trash', 'junk', 'garbage'))
    def test_rejects_bad_keep(self, bad_keep, _iitd_args):

        _new_args = deepcopy(_iitd_args)
        _new_args['_keep'] = bad_keep

        with pytest.raises(AssertionError):
            _identify_idxs_to_delete(**_new_args)

    # ------------------------------

    # ------------------------------
    @pytest.mark.parametrize('junk_do_not_drop',
        (-1,0,1,3.14,True,False,{'a':1}, min, lambda x: x)
    )
    def test_rejects_junk_do_not_drop(self, junk_do_not_drop, _iitd_args):

        _new_args = deepcopy(_iitd_args)
        _new_args['_do_not_drop'] = junk_do_not_drop

        with pytest.raises(AssertionError):
            _identify_idxs_to_delete(**_new_args)


    @pytest.mark.parametrize('bad_do_not_drop',
        ([min, max], [True, False], [[], []])
)
    def test_rejects_bad_do_not_drop(self, bad_do_not_drop, _iitd_args):

        _new_args = deepcopy(_iitd_args)
        _new_args['_do_not_drop'] = bad_do_not_drop

        with pytest.raises(AssertionError):
            _identify_idxs_to_delete(**_new_args)


    def test_reject_str_do_not_drop_if_no_columns(self, _iitd_args, _columns):

        _new_args = deepcopy(_iitd_args)
        _new_args['_do_not_drop'] = [_columns[0], _columns[-1]]
        _new_args['_columns'] = None

        with pytest.raises(AssertionError):
            _identify_idxs_to_delete(**_new_args)

    # ------------------------------

    # ------------------------------
    @pytest.mark.parametrize('junk_columns',
        (-1,0,1,3.14,True,False,[0,1],(0,1),(0,),{'a':1}, min, lambda x: x)
    )
    def test_rejects_junk_columns(self, junk_columns, _iitd_args):

        _new_args = deepcopy(_iitd_args)
        _new_args['_columns'] = junk_columns

        with pytest.raises(AssertionError):
            _identify_idxs_to_delete(**_new_args)


    @pytest.mark.parametrize('bad_columns', ([0,1,2,3,4], [True, False]))
    def test_rejects_bad_columns(self, bad_columns, _iitd_args):

        _new_args = deepcopy(_iitd_args)
        _new_args['_columns'] = bad_columns

        with pytest.raises(AssertionError):
            _identify_idxs_to_delete(**_new_args)

    # ------------------------------


    # ------------------------------
    @pytest.mark.parametrize('junk_conflict',
        (-1,0,1,3.14,None,True,False,[0,1],(0,),{'a':1}, min, lambda x: x)
    )
    def test_rejects_junk_conflict(self, junk_conflict, _iitd_args):

        _new_args = deepcopy(_iitd_args)
        _new_args['_conflict'] = junk_conflict

        with pytest.raises(AssertionError):
            _identify_idxs_to_delete(**_new_args)


    @pytest.mark.parametrize('bad_conflict', ('junk', 'trash', 'garbage'))
    def test_rejects_bad_conflict(self, bad_conflict, _iitd_args):

        _new_args = deepcopy(_iitd_args)
        _new_args['_conflict'] = bad_conflict

        with pytest.raises(AssertionError):
            _identify_idxs_to_delete(**_new_args)

    # ------------------------------


    # ------------------------------
    @pytest.mark.parametrize('junk_rand_idxs',
        (-1,0,1,3.14,None,True,False,[0,1],(0,),{'a':1}, min, lambda x: x)
    )
    def test_rejects_junk_rand_idxs(self, junk_rand_idxs, _iitd_args):

        _new_args = deepcopy(_iitd_args)
        _new_args['_rand_idxs'] = junk_rand_idxs

        with pytest.raises(AssertionError):
            _identify_idxs_to_delete(**_new_args)


    @pytest.mark.parametrize('bad_rand_idxs', ((-2, -1), (0,2,4), (0, 1000)))
    def test_rejects_bad_rand_idxs(self, bad_rand_idxs, _iitd_args):

        # length does not match duplicates or idxs are out of range

        _new_args = deepcopy(_iitd_args)
        _new_args['_rand_idxs'] = bad_rand_idxs

        with pytest.raises(AssertionError):
            _identify_idxs_to_delete(**_new_args)


    @pytest.mark.parametrize('_duplicates', ([[0,2],[1,3]], [], [[0,1,2,3]]))
    @pytest.mark.parametrize('_rand_idxs',  ((0,2), (1,3), tuple(), (0,1)))
    def test_rejects_rand_idxs_does_not_match_duplicates(
        self, _duplicates, _rand_idxs, _iitd_args
    ):

        _new_args = deepcopy(_iitd_args)
        _new_args['_duplicates'] = _duplicates
        _new_args['_rand_idxs'] = _rand_idxs
        _new_args['_do_not_drop'] = None

        do_not_match = False
        if len(_duplicates) != len(_rand_idxs):
            do_not_match += 1
        else:
            for _idx in range(len(_duplicates)):
                if _rand_idxs[_idx] not in _duplicates[_idx]:
                    do_not_match += 1

        if do_not_match:
            with pytest.raises(AssertionError):
                _identify_idxs_to_delete(**_new_args)
        else:
            _identify_idxs_to_delete(**_new_args)


    @pytest.mark.parametrize('_rand_idxs', ((0,2), (1,3)))
    @pytest.mark.parametrize('_conflict', ('raise', 'ignore'))
    @pytest.mark.parametrize('_do_not_drop', ([0, 1, 2], 'str', None))
    @pytest.mark.parametrize('_keep', ('first', 'last', 'random'))
    def test_accepts_all_good(
        self, _iitd_args, _keep, _do_not_drop, _conflict, _rand_idxs
    ):

        _new_args = deepcopy(_iitd_args)
        _new_args['_keep'] = _keep
        _new_args['_do_not_drop'] = _do_not_drop
        _new_args['_conflict'] = _conflict
        _new_args['_rand_idxs'] = _rand_idxs


        _identify_idxs_to_delete(**_iitd_args)

    # END test validation ** * ** * ** * ** * ** * ** * ** * ** * ** * **


class TestIITDConflict:

    @pytest.mark.parametrize('_columns_is_passed', (True, False))
    def test_conflict(self, _columns, _columns_is_passed, _iitd_args):

        _new_args = deepcopy(_iitd_args)
        _new_args['_keep'] = 'first'
        _new_args['_columns'] = _columns if _columns_is_passed else None

        # do not drop idxs are both from the same set of duplicates -----------
        for _dnd in ([0,1], [2,3]):
            _new_args['_do_not_drop'] = _dnd
            for _conflict in ('raise', 'ignore'):
                _new_args['_conflict'] = _conflict
                if _conflict == 'raise':
                    with pytest.raises(ValueError):
                        # two do_not_drop idxs in the same set of duplicates
                        _identify_idxs_to_delete(**_new_args)
                elif _conflict == 'ignore':
                    # two do_not_drop idxs in the same set of duplicates, but
                    # does not raise because of 'ignore'
                    # _new_args['_do_not_drop'] = [2, 3]
                    removed_columns_out = _identify_idxs_to_delete(**_new_args)

                    assert isinstance(removed_columns_out, dict)

                    if _dnd == [0, 1]:
                        assert removed_columns_out == {1: 0, 3: 2}
                    elif _dnd == [2, 3]:
                        assert removed_columns_out == {1: 0, 3: 2}
                    else:
                        raise Exception
        # END do not drop idxs are both from the same set of duplicates -------

        _new_args = deepcopy(_iitd_args)
        _new_args['_keep'] = 'first'
        _new_args['_columns'] = _columns if _columns_is_passed else None
        _new_args['_do_not_drop'] = [1]

        # ** ** ** ** **
        for _conflict in ('raise', 'ignore'):
            _new_args['_conflict'] = _conflict
            if _conflict == 'raise':
                with pytest.raises(ValueError):
                    # wants so keep 0 because of 'first' but _do_not_drop [1]
                    _identify_idxs_to_delete(**_new_args)
            else:
                # do_not_drop == [1] but 'first' wants to keep [0]
                # this doesnt raise because of 'ignore'
                removed_columns_out = _identify_idxs_to_delete(**_new_args)

                assert isinstance(removed_columns_out, dict)
                assert removed_columns_out == {0:1, 3:2}

        # ** ** ** ** **


class TestIITDAccuracy:

    # accuracy ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @pytest.mark.parametrize('_columns_is_passed', (True, False))
    @pytest.mark.parametrize('_keep', ('first', 'last', 'random'))
    @pytest.mark.parametrize('_do_not_drop', (None, [0], [0,1], [0,2]))
    @pytest.mark.parametrize('_conflict', ('raise', 'ignore'))
    def test_no_duplicates(
        self, _columns, _keep, _do_not_drop, _conflict, _columns_is_passed,
        _iitd_args
    ):

        # no duplicates, so removed_columns should be empty
        # _rand_idxs should come in empty
        _new_args = deepcopy(_iitd_args)
        _new_args['_duplicates'] = []
        _new_args['_keep'] = _keep
        _new_args['_do_not_drop'] = _do_not_drop
        _new_args['_columns'] = _columns if _columns_is_passed else None
        _new_args['_conflict'] = _conflict
        _new_args['_rand_idxs'] = tuple()

        removed_columns_out = _identify_idxs_to_delete(**_new_args)

        assert isinstance(removed_columns_out, dict)
        assert len(removed_columns_out) == 0


    @pytest.mark.parametrize('_columns_is_passed', (True, False))
    @pytest.mark.parametrize('_keep', ('first', 'last', 'random'))
    def test_do_not_drop_is_none(
        self, _columns_is_passed, _columns, _iitd_args, _keep
    ):

        # do_not_drop is None, so no conflicts with keep, should always
        # return without exception, and should not muddy the water for
        # keep==random

        _new_args = deepcopy(_iitd_args)
        _new_args['_keep'] = _keep
        _new_args['_do_not_drop'] = None
        _new_args['_columns'] = _columns if _columns_is_passed else None
        _new_args['_conflict'] = 'raise'

        removed_columns_out = _identify_idxs_to_delete(**_new_args)

        assert isinstance(removed_columns_out, dict)

        for k, v in removed_columns_out.items():
            assert isinstance(k, int)
            assert isinstance(v, int)


        if _keep == 'first':
            assert removed_columns_out == {1:0, 3:2}

        elif _keep == 'last':
            assert removed_columns_out == {0:1, 2:3}

        elif _keep == 'random':
            assert len(removed_columns_out) == 2
            for k, v in removed_columns_out.items():

                assert v != k

                if k == 0:
                    assert v == 1
                elif k == 1:
                    assert v == 0
                elif k == 2:
                    assert v == 3
                elif k == 3:
                    assert v == 2


    @pytest.mark.parametrize('_columns_is_passed', (True, False))
    @pytest.mark.parametrize('_do_not_drop', ([1], [1, 3], [0, 1]))
    @pytest.mark.parametrize('_keep', ('first', 'last', 'random'))
    def test_with_do_not_drop(
        self, _keep, _do_not_drop, _columns, _columns_is_passed, _iitd_args
    ):

        _new_args = deepcopy(_iitd_args)
        _new_args['_keep'] = _keep
        _new_args['_do_not_drop'] = _do_not_drop
        _new_args['_columns'] = _columns if _columns_is_passed else None
        _new_args['_conflict'] = 'ignore'
        _new_args['_rand_idxs'] = \
            _lock_in_random_idxs(
                _duplicates=_new_args['_duplicates'],
                _do_not_drop=_new_args['_do_not_drop'],
                _columns=_new_args['_columns']
            )

        removed_columns_out = _identify_idxs_to_delete(**_new_args)

        assert isinstance(removed_columns_out, dict)

        for k, v in removed_columns_out.items():
            assert isinstance(k, int)
            assert isinstance(v, int)


        if _keep == 'first':
            if _do_not_drop in ([0], [0, 2]):
                assert removed_columns_out == {1:0, 3:2}
            elif _do_not_drop == [0, 1]:
                assert removed_columns_out == {1:0, 3:2}

        elif _keep == 'last':
            if _do_not_drop == [0]:
                assert removed_columns_out == {1:0, 2:3}
            elif _do_not_drop == [0, 2]:
                assert removed_columns_out == {1: 0, 3: 2}
            elif _do_not_drop == [0, 1]:
                assert removed_columns_out == {0:1, 2:3}


        elif _keep == 'random':

            assert isinstance(removed_columns_out, dict)
            assert len(removed_columns_out) == 2

            if _do_not_drop == [0]:
                for k, v in removed_columns_out.items():
                    if k==1:
                        assert v == 0
                    elif k==2:
                        assert v == 3
                    elif k==3:
                        assert v == 2

            elif _do_not_drop == [0, 2]:
                assert removed_columns_out[1] == 0
                assert removed_columns_out[3] == 2

            elif _do_not_drop == [0, 1]:
                for k, v in removed_columns_out.items():
                    if k == 0:
                        assert v == 1
                    elif k == 1:
                        assert v == 0
                    elif k == 2:
                        assert v == 3
                    elif k == 3:
                        assert v == 2






