# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
import numpy as np

from pybear.utilities._remove_characters import remove_characters


# def remove_characters(
#     X: list[str] | list[list[str]] | npt.NDArray[str],
#     allowed_chars: str | None,
#     disallowed_chars: str | None
# ) -> list[str] | list[list[str]] | npt.NDArray[str]:



class TestRemoveCharactersValidation:


    @pytest.mark.parametrize('junk_X',
        (-2.7, -1, 0, 1, 2.7, True, None, 'trash', [0,1], (1,), {'A':1},
         lambda x: x, [[1,2,3], [4,5,6]])
    )
    def test_rejects_junk_X(self, junk_X):

        with pytest.raises(TypeError):

            remove_characters(junk_X, disallowed_chars='!@#$%^&*()')



    @pytest.mark.parametrize('junk_ac',
        (-2.7, -1, 0, 1, 2.7, True, False, [0, 1], (1,), {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_allowed_chars(self, junk_ac):

        with pytest.raises(TypeError):
            remove_characters(list('abcde'), allowed_chars=junk_ac)


    @pytest.mark.parametrize('junk_dc',
        (-2.7, -1, 0, 1, 2.7, True, False, [0, 1], (1,), {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_disallowed_chars(self, junk_dc):

        with pytest.raises(TypeError):
            remove_characters(list('abcd'), disallowed_chars=junk_dc)


    def test_rejects_empty_strings(self):

        with pytest.raises(ValueError):
            remove_characters(list('abcde'), allowed_chars='')

        with pytest.raises(ValueError):
            remove_characters(list('abcd'), disallowed_chars='')


    @pytest.mark.parametrize('_ac', ('!@#$%^&*(', None))
    @pytest.mark.parametrize('_dc', ('qwerty', None))
    def test_mix_and_match_strs_and_None(self, _ac, _dc):

        if (_ac is None and _dc is None) or (_ac is not None and _dc is not None):
            with pytest.raises(ValueError):
                remove_characters(
                    list('!@#'),
                    allowed_chars=_ac,
                    disallowed_chars=_dc
                )
        else:
            out = remove_characters(
                list('!@#'),
                allowed_chars=_ac,
                disallowed_chars=_dc
            )

            assert np.array_equal(out, list('!@#'))



class TestRemoveCharacters:

    # 1D -- -- -- -- -- -- -- -- -- --

    def test_1D_list_accuracy(self):


        out = remove_characters([' Sam ', ' I ', ' am '], disallowed_chars='!@#')
        assert isinstance(out, list)
        assert np.array_equal(out, [' Sam ', ' I ', ' am '])

        out = remove_characters(['!S!a!m!', '@I@', '#a#m#'], disallowed_chars='!@#')
        assert isinstance(out, list)
        assert np.array_equal(out, ['Sam', 'I', 'am'])

        out = remove_characters(['Sam ', ' I ', ' am '], allowed_chars='SamI ')
        assert isinstance(out, list)
        assert np.array_equal(out, ['Sam ', ' I ', ' am '])

        out = remove_characters(
            [' !Sam! ', '@ I @', ' #am #'], allowed_chars='SamI '
        )
        assert isinstance(out, list)
        assert np.array_equal(out, [' Sam ', ' I ', ' am '])


        # removes empties
        out = remove_characters(
            [' !Sam! ', '@ I @', ' #am #'], disallowed_chars=' #am'
        )
        assert isinstance(out, list)
        assert np.array_equal(out, ['!S!', '@I@'])


    def test_1D_np_accuracy(self):

        out = remove_characters(
            np.array([' Sam ', ' I ', ' am ']), disallowed_chars='!@#'
        )
        assert isinstance(out, np.ndarray)
        assert np.array_equal(out, [' Sam ', ' I ', ' am '])

        out = remove_characters(
            np.array(['!S!a!m!', '@I@', '#a#m#']), disallowed_chars='!@#'
        )
        assert isinstance(out, np.ndarray)
        assert np.array_equal(out, ['Sam', 'I', 'am'])

        out = remove_characters(
            np.array(['Sam ', ' I ', ' am ']), allowed_chars='SamI '
        )
        assert isinstance(out, np.ndarray)
        assert np.array_equal(out, ['Sam ', ' I ', ' am '])

        out = remove_characters(
            np.array([' !Sam! ', '@ I @', ' #am #']), allowed_chars='SamI '
        )
        assert isinstance(out, np.ndarray)
        assert np.array_equal(out, [' Sam ', ' I ', ' am '])

        # removes empties
        out = remove_characters(
            np.array([' !Sam! ', '@ I @', ' #am #']), disallowed_chars=' #am'
        )
        assert isinstance(out, np.ndarray)
        assert np.array_equal(out, ['!S!', '@I@'])


    # END 1D -- -- -- -- -- -- -- -- -- --

    # 2D -- -- -- -- -- -- -- -- -- --

    def test_2D_list_accuracy(self):

        out = remove_characters(
            [['Sam', 'I', 'am'], ['I', 'am', 'Sam']],
            disallowed_chars='!@#'
        )
        assert isinstance(out, list)
        assert all(map(
            np.array_equal,
            out,
            [['Sam', 'I', 'am'], ['I', 'am', 'Sam']]
        ))

        # -- -- -- -- -- -- -- -- -- -- -- -- -- --

        out = remove_characters(
            [[' !Sam! ', 'I@  ', ' #am'], [' !I@ ', ' @am#', '@Sam']],
            disallowed_chars='!@#'
        )
        assert isinstance(out, list)
        assert all(map(
            np.array_equal,
            out,
            [[' Sam ', 'I  ', ' am'], [' I ', ' am', 'Sam']]
        ))

        # -- -- -- -- -- -- -- -- -- -- -- -- -- --

        out = remove_characters(
            [['I   am   Sam,  Sam ,  I , am   ']],
            allowed_chars='IamS '
        )
        assert isinstance(out, list)
        assert np.array_equal(out, [['I   am   Sam  Sam   I  am   ']])

        # -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # removes empties
        out = remove_characters(
            [[' !Sam! ', 'I@  ', ' #am'], [' !I@ ', ' @am#', '@Sam']],
            disallowed_chars='@Sam'
        )
        assert isinstance(out, list)
        assert all(map(
            np.array_equal,
            out,
            [[' !! ', 'I  ', ' #'], [' !I ', ' #']]
        ))


    def test_2D_np_accuracy(self):

        out = remove_characters(
            np.array([['Sam', 'I', 'am'], ['I', 'am', 'Sam']]),
            disallowed_chars='!@#'
        )
        assert isinstance(out, np.ndarray)
        assert all(map(
            np.array_equal,
            out,
            [['Sam', 'I', 'am'], ['I', 'am', 'Sam']]
        ))

        # -- -- -- -- -- -- -- -- -- -- -- -- -- --

        out = remove_characters(
            np.array([['!S!a!m!', '@I@', '#a#m#'], ['!I ', ' @am ', ' Sam#']]),
            disallowed_chars='!@#'
        )
        assert isinstance(out, np.ndarray)
        assert all(map(
            np.array_equal,
            out,
            [['Sam', 'I', 'am'], ['I ', ' am ', ' Sam']]
        ))

        # -- -- -- -- -- -- -- -- -- -- -- -- -- --

        out = remove_characters(
            np.array([['I   am   Sam,  Sam ,  I , am   ']]),
            allowed_chars='IamS '
        )
        assert isinstance(out, np.ndarray)
        assert np.array_equal(out, [['I   am   Sam  Sam   I  am   ']])


        # removes empties
        out = remove_characters(
            np.array(
                (np.array([' !Sam! ', 'I@  ']),
                np.array([' !I@ ', ' @am#', '@Sam'])),
                dtype=object
            ),
            disallowed_chars='@Sam'
        )
        assert isinstance(out, np.ndarray)
        assert all(map(
            np.array_equal,
            out,
            [[' !! ', 'I  '], [' !I ', ' #']]
        ))

        # this is actually a full array so will skip removing the empties
        # because of casting error
        out = remove_characters(
            np.array([[' !Sam! ', 'I@  ', ' #am'], [' !I@ ', ' @am#', '@Sam']]),
            disallowed_chars='@Sam'
        )
        assert isinstance(out, np.ndarray)
        assert all(map(
            np.array_equal,
            out,
            [[' !! ', 'I  ', ' #'], [' !I ', ' #', '']]
        ))

    # END 2D -- -- -- -- -- -- -- -- -- --











