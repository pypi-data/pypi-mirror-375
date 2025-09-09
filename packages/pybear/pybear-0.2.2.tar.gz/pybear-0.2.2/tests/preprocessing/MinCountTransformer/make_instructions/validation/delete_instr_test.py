# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.preprocessing._MinCountTransformer._make_instructions._validation. \
    _delete_instr import _val_delete_instr

import pytest



class TestValDeleteInstr:

    # def _val_delete_instr(
    #     _delete_instr: InstructionsType,
    #     _n_features_in: int
    # ) -> None:

     # _n_features_in handled by _val_n_features_in


    @pytest.mark.parametrize(f'junk_instr',
        (-2.7, -1, 0, 1, 2.7, True, None, [0,1], (1,), {0,1}, lambda x: x)
    )
    def test_rejects_junk_delete_instr(self, junk_instr):

        with pytest.raises(TypeError):
            _val_delete_instr(
                junk_instr,
                _n_features_in=5
            )


    @pytest.mark.parametrize(f'bad_instr',
        (-2.7, -1, 0, 1, 2.7, True, None, [0, 1], (1,), {0, 1}, lambda x: x)
    )
    def test_rejects_bad_delete_instr(self, bad_instr):

        n_features_in=5

        # too short
        with pytest.raises(ValueError):
            _val_delete_instr(
                {i:['INACTIVE'] for i in range(n_features_in-1)},
                _n_features_in=n_features_in
            )

        # too long
        with pytest.raises(ValueError):
            _val_delete_instr(
                {i:['INACTIVE'] for i in range(n_features_in+1)},
                _n_features_in=n_features_in
            )

        # values not lists
        with pytest.raises(AssertionError):
            _val_delete_instr(
                {i:1 for i in range(n_features_in)},
                _n_features_in=n_features_in
            )


    def test_miscellaneous(self):

        # INACTIVE -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # 'INACTIVE' is not the only entry for a column
        with pytest.raises(ValueError):
            _val_delete_instr(
                {i:['INACTIVE', 0, 1, 2] for i in range(3)},
                _n_features_in=3
            )

        _val_delete_instr(
            {i: ['INACTIVE'] for i in range(3)},
            _n_features_in=3
        )
        # END INACTIVE -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


        # DELETE ALL -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # 'DELETE ALL' MUST ALWAYS BE IN THE SECOND TO LAST POSITION!
        with pytest.raises(ValueError):
            _val_delete_instr(
                {i:['DELETE ALL', 0, 1, 2] for i in range(3)},
                _n_features_in=3
            )

        _val_delete_instr(
            {i:[0, 1, 'DELETE ALL', 'DELETE COLUMN'] for i in range(3)},
            _n_features_in=3
        )

        # multiple 'DELETE ALL' for a column
        with pytest.raises(ValueError):
            _val_delete_instr(
                {i:['DELETE ALL', 'DELETE ALL'] for i in range(5)},
                _n_features_in=5
            )

        _val_delete_instr(
            {i:['DELETE ALL', 'DELETE COLUMN'] for i in range(5)},
            _n_features_in=5
        )

        # DELETE ALL but no DELETE COLUMN
        with pytest.raises(ValueError):
            _val_delete_instr(
                {i:[0, 1, 'DELETE ALL'] for i in range(3)},
                _n_features_in=3
            )


        # END DELETE ALL -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # DELETE COLUMN -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # 'DELETE COLUMN' MUST ALWAYS BE IN THE LAST POSITION!
        with pytest.raises(ValueError):
            _val_delete_instr(
                {i:['DELETE COLUMN', 0, 1, 2] for i in range(3)},
                _n_features_in=3
            )

        _val_delete_instr(
            {i:[0, 1, 2, 'DELETE COLUMN'] for i in range(3)},
            _n_features_in=3
        )

        # multiple 'DELETE COLUMN' for a column
        with pytest.raises(ValueError):
            _val_delete_instr(
                {i:['DELETE COLUMN', 'DELETE COLUMN'] for i in range(5)},
                _n_features_in=5
            )

        _val_delete_instr(
            {i:['DELETE COLUMN'] for i in range(5)},
            _n_features_in=5
        )

        # END DELETE COLUMN -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --







