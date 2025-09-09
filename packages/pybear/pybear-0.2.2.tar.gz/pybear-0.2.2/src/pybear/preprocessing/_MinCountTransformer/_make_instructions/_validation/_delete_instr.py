# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ..._type_aliases import InstructionsType

from ....__shared._validation._any_integer import _val_any_integer



def _val_delete_instr(
    _delete_instr: InstructionsType,
    _n_features_in: int
) -> None:
    """Validate that `_delete_instr` is a dictionary with an entry for
    each feature in the data.

    The keys must be the integer column indices of the features and
    the values must be lists that hold the values to be removed from
    that column. the lists may also contain any of 'DELETE ALL',
    'DELETE COLUMN' or 'INACTIVE'. The individual lists may be empty.

    Parameters
    ----------
    _delete_instr : InstructionsType
        The recipe for deleting values and columns derived from the
        `unqs_ct_dict`, which holds the unique values and their
        frequencies in data passed to the MCT instance.
    _n_features_in : int
        The number of features in the data.

    Return
    ------
    None

    """


    _err_msg = (
        f"'_delete_instr' must be a dictionary with an entry for each "
        f"feature in the data. \nthe keys must be the integer column "
        f"indices of the features and the values must be lists that hold "
        f"the values to be removed from the data for that column. "
    )


    _val_any_integer(_n_features_in, 'n_features_in', _min=1)

    if not isinstance(_delete_instr, dict):
        raise TypeError(_err_msg + f"got outer container {type(_delete_instr)}. ")

    if len(_delete_instr) != _n_features_in:
        raise ValueError(_err_msg + f"got {len(_delete_instr)} entries.")

    for col_idx, _instr in _delete_instr.items():

        assert isinstance(_instr, list), \
            _err_msg + f"got col idx {col_idx} value is {type(_instr)}."

        if 'INACTIVE' in _instr and len(_instr) > 1:
            raise ValueError(f"'INACTIVE' IN len(_delete_instr[{col_idx}]) > 1")

        # 'DELETE ALL' MUST ALWAYS BE SECOND TO LAST AND 'DELETE COLUMN'
        # MUST ALSO BE IN!
        if 'DELETE ALL' in _instr:

            if _instr[-2] != 'DELETE ALL':
                raise ValueError(
                    f"'DELETE ALL' is not in the -2 position of "
                    f"_delete_instr[{col_idx}]"
                )

            if len([i for i in _instr if i == 'DELETE ALL']) > 1:
                raise ValueError(
                    f"'DELETE ALL' is in _delete_instr[{col_idx}] more "
                    f"than once"
                )

            if 'DELETE COLUMN' not in _instr:
                raise ValueError(
                    f"'DELETE ALL' is in _delete_instr[{col_idx}] but "
                    f"'DELETE COLUMN' is not"
                )

        # 'DELETE COLUMN' MUST ALWAYS BE IN THE LAST POSITION!
        if 'DELETE COLUMN' in _instr:

            if _instr[-1] != 'DELETE COLUMN':
                raise ValueError(
                    f"'DELETE COLUMN' is not in the -1 position of "
                    f"_delete_instr[{col_idx}]"
                )

            if len([i for i in _instr if i == 'DELETE COLUMN']) > 1:
                raise ValueError(
                    f"'DELETE COLUMN' is in _delete_instr[{col_idx}] more "
                    f"than once"
                )





