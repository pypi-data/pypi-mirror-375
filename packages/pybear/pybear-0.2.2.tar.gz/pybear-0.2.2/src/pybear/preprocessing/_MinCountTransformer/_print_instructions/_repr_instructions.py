# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    InstructionsType,
    TotalCountsByColumnType,
    CountThresholdType,
    FeatureNamesInType
)

import numbers

import numpy as np

from .._make_instructions._validation._delete_instr import _val_delete_instr
from .._make_instructions._validation._total_counts_by_column import \
    _val_total_counts_by_column

from .._validation._count_threshold import _val_count_threshold
from .._validation._feature_names_in import _val_feature_names_in

from .._make_instructions._threshold_listifier import _threshold_listifier



def _repr_instructions(
    _delete_instr: InstructionsType,
    _total_counts_by_column: TotalCountsByColumnType,
    _thresholds: CountThresholdType,
    _n_features_in: int,
    _feature_names_in: FeatureNamesInType | None,
    _clean_printout: bool,
    _max_char: int = 99
) -> list[str]:
    """Display instructions generated for the current fitted state,
    subject to the current settings of the parameters.

    The printout will indicate what values and columns will be deleted,
    and if all columns or all rows will be deleted. Use `set_params`
    after finishing fits to change MCTs parameters and see the impact
    on the transformation.

    If the instance has multiple recursions (i.e., `max_recursions` > 1),
    parameters cannot be changed via method `set_params`, but the net
    effect of all recursions is displayed (remember that multiple
    recursions can only be accessed through `fit_transform`). The
    results are displayed as a single set of instructions, as if to
    perform the cumulative effect of the recursions in a single step.

    This print utility can only report the instructions and outcomes that
    can be directly inferred from the information learned about uniques
    and counts during fitting. It cannot predict any interaction effects
    that occur during transform of a dataset that may ultimately cause
    all rows to be deleted. It also cannot capture the effects of
    previously unseen values that may be passed during transform.

    Parameters
    ----------
    _delete_instr : InstructionsType
        The instructions for deleting values and columns as generated
        by :func:`_make_instructions` from the uniques / counts in
        `_total_counts_by_column` and the parameter settings.
    _total_counts_by_column : TotalCountsByColumnType
        The uniques and their counts for each column in the data.
    _thresholds : CountThresholdsType
        The threshold value(s) that determine whether a unique value is
        removed from a dataset.
    _n_features_in : int
        The number of features in the data.
    _feature_names_in : FeatureNamesInType | None
        The features names of the data if the data was passed in a
        container that had features names, like a pandas or polars
        dataframe. Otherwise, None.
    _clean_printout : bool
        Truncate printout to fit on screen.
    _max_char : int, default=99
        The maximum number of characters to display per line if
        `clean_printout` is set to True. Ignored if `clean_printout` is
        False. Must be an integer in range [72, 120].

    Return
    ------
    OUTPUT_HOLDER_FOR_TEST : list[str]
        The printed summary captured in a list. This is only for test
        purposes.

    """


    _tcnw = 35 # the number of chars for idx/name/thresh/_pad
    _pad = 2  # number of spaces between name/thresh info & delete info


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # _n_features_in is validated by _val_delete_instr

    _val_feature_names_in(_feature_names_in)

    _val_delete_instr(_delete_instr, _n_features_in)

    _val_total_counts_by_column(_total_counts_by_column)
    assert len(_total_counts_by_column) == _n_features_in

    _val_count_threshold(_thresholds, ['int', 'Sequence[int]'], _n_features_in)

    if not isinstance(_clean_printout, bool):
        raise TypeError(f"'clean_printout' must be boolean")

    _err_msg = f"'max_char' must be an integer >= 72 and <= 120"
    if not isinstance(_max_char, numbers.Integral):
        raise TypeError(_err_msg)
    if _max_char < 72 or _max_char > 120:
        raise ValueError(_err_msg)
    del _err_msg
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    _thresholds = _threshold_listifier(_n_features_in, _thresholds)

    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
    # build the idx/feature name/threshold/pad part of the display

    # the maximum width for idx/name/thresh/pad is fixed to a maximum
    # but could be shorter. do all these gymnastics to find out:
    # 1) if shorter, and what is the final total len
    # 2) if longer, that will determine that names need to be chopped

    # get max idx len -- -- -- -- -- -- -- -- -- -- --
    _max_idx_len = len(f"{_n_features_in-1}) ")
    # END get max idx len -- -- -- -- -- -- -- -- -- --

    # get the max name len -- -- -- -- -- -- -- --
    if _feature_names_in is not None:
        _columns = list(map(str, _feature_names_in))
    else:
        _columns = [f"Column {i+1}" for i in range(_n_features_in)]

    _max_name_len = max(map(len, _columns))
    # END get the max name len -- -- -- -- -- -- -- --

    # get the max thresh len -- -- -- -- -- -- -- --
    _max_thresh_len = len(f" ({max(_thresholds)})")
    # END get the max thresh len -- -- -- -- -- -- --

    # set the final width for the description part -- -- --
    _final_tcnw: int = min(
        _tcnw,
        _max_idx_len + _max_name_len + _max_thresh_len + _pad
    )
    # END set the final width for the description part -- -- --

    del _max_idx_len, _max_name_len, _max_thresh_len,

    # build the description part for all the columns -- -- --
    DESCRIPTION_PART = []
    for c_idx in range(_n_features_in):

        _allotment_for_name = _final_tcnw
        _allotment_for_name -= len(f"{c_idx}) ")
        _allotment_for_name -= len(f" ({_thresholds[c_idx]})")
        _allotment_for_name -= _pad

        _description = f""
        _description += f"{c_idx}) "

        if len(_columns[c_idx]) <= _allotment_for_name:
            _description += f"{_columns[c_idx]}"
        else:
            _chop_point = (_allotment_for_name - len(f"..."))
            _description += f"{_columns[c_idx][:_chop_point]}"
            _description += f"..."
            del _chop_point

        _description += f" ({_thresholds[c_idx]})"

        _description = _description.ljust(_final_tcnw)

        DESCRIPTION_PART.append(_description)

    del c_idx, _allotment_for_name, _description, _columns
    # END build the description part for all the columns -- -- --

    # END build the idx/feature name/threshold/pad part of the display
    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    # MAKE A VECTOR TO HOLD THE OUTPUTS FOR TESTING
    OUTPUT_HOLDER_FOR_TEST = [f"" for _ in range(_n_features_in)]

    _delete_column = False
    _all_rows_deleted = False
    _all_columns_deleted = True  # if any column is not deleted, toggles to False
    _ardm = f"All rows will be deleted. "  # all_rows_deleted_msg
    _cdm = f"Delete column."   # column_delete_msg
    for col_idx, _instr in _delete_instr.items():

        # notice the end="". tack on the instructions part below.
        print(DESCRIPTION_PART[col_idx], end="")
        OUTPUT_HOLDER_FOR_TEST[col_idx] += DESCRIPTION_PART[col_idx]

        # print the instructions part -- -- -- -- -- -- -- -- -- -- --
        if 'DELETE COLUMN' in _instr:
            # IF IS BIN-INT & NOT DELETE ROWS, ONLY ENTRY WOULD BE "DELETE COLUMN"
            _delete_column = True
            _instr.remove('DELETE COLUMN')
            if len(_instr) == 0:  # then 'DELETE COLUMN' was the only entry
                print(_cdm)
                OUTPUT_HOLDER_FOR_TEST[col_idx] += _cdm
                continue
        else:
            _all_columns_deleted = False

        # must be after _all_columns_deleted logic
        if len(_instr) == 0:
            print("No operations.")
            OUTPUT_HOLDER_FOR_TEST[col_idx] += f"No operations."
            continue

        if _instr[0] == 'INACTIVE':
            print("Ignored.")
            OUTPUT_HOLDER_FOR_TEST[col_idx] += f"Ignored."
            continue

        if 'DELETE ALL' in _instr:
            _all_rows_deleted = True
            _instr.remove('DELETE ALL')
        elif len(_instr) == len(_total_counts_by_column[col_idx]):
            _all_rows_deleted = True
            _instr = []

        if _all_rows_deleted:
            # notice the 'end'!
            print(_ardm, end='')
            OUTPUT_HOLDER_FOR_TEST[col_idx] += _ardm
            if _all_columns_deleted:
                print(_cdm)
                OUTPUT_HOLDER_FOR_TEST[col_idx] += _cdm
            else:
                print('')

            continue

        # sanity check
        if len(_instr) == 0:
            raise Exception(f"_instr is empty and should not be")

        # if get to here, _instr must have single values, not empty
        # all_rows_deleted cannot be triggered, would have caught above

        # condition the values in _instr for easier viewing
        for _idx, _value in enumerate(_instr):
            try:
                _value = np.float64(str(_value)[:7])
                _instr[_idx] = f"{_value}"
            except:
                _instr[_idx] = str(_value)
        del _idx, _value
        # END condition the values in _instr for easier viewing

        _instr: list[str]

        _delete_rows_msg = "Delete rows containing "
        _mpl: int = (_max_char - _final_tcnw)  # subtract chars for description
        _mpl -= len(_delete_rows_msg)   # subtract the row del prefix jargon
        _mpl -= len(_cdm) if _delete_column else 0 # subtract col del jargon
        # what is left in _mpl is the num spaces we have to put row values

        _trunc_msg = lambda _idx: f"... + {len(_instr[_idx+1:])} other(s). "

        if not _clean_printout or len(', '.join(_instr) + ". ") <= _mpl:
            _delete_rows_msg += (', '.join(_instr) + ". ")
            # if the total length of the entries is less than _mpl, just
            # join and get on with it
        elif len(f"{_instr[0]}, {_trunc_msg(0)}") > _mpl:
            # if a single deleted value + trunc_msg is over the length
            _num_deleted = len(_instr)
            _num_uniques = len(_total_counts_by_column[col_idx])
            _delete_rows_msg = \
                f"Delete {_num_deleted} of {_num_uniques} uniques. "
            del _num_deleted, _num_uniques
        else:
            _shown_values = ""
            for idx, word in enumerate(_instr):
                # cant reach the last word here... we know from above that
                # if we could fit all the words we joined all in one shot
                # and bypassed this.

                _shown_values += f"{word}, "

                # if the next word and addon are too long, stay at the
                # current word, attach the addon, and break.
                if len(
                    _shown_values
                    + _instr[idx + 1] + f", "
                    + _trunc_msg(idx + 1)
                ) > _mpl:
                    _delete_rows_msg += (_shown_values + _trunc_msg(idx))
                    break

            del _shown_values, idx, word

        del _mpl, _trunc_msg

        _delete_rows_msg += _cdm if _delete_column else ""

        if _clean_printout:
            try:
                assert len(_delete_rows_msg) <= (_max_char - _final_tcnw)
            except AssertionError:
                raise ValueError(
                    f"MCT does not have an instruction display layout for "
                    f"column index {col_idx} that fits within the maximum "
                    f"\ncharacter window that you have provided. Please "
                    f"use a larger value for :param: 'max_char'."
                )


        print(_delete_rows_msg)
        OUTPUT_HOLDER_FOR_TEST[col_idx] += _delete_rows_msg
        # end individual column printing ** ** ** ** ** ** ** ** ** **

    if _all_columns_deleted:
        print(f'\nAll columns will be deleted.')
        OUTPUT_HOLDER_FOR_TEST.append(f'All columns will be deleted.')
    if _all_rows_deleted:
        print(f'\nAll rows are guaranteed to be deleted.')
        OUTPUT_HOLDER_FOR_TEST.append(f'All rows are guaranteed to be deleted.')

    del DESCRIPTION_PART, _ardm, _cdm, col_idx, _instr
    del _all_columns_deleted, _all_rows_deleted, _delete_column

    try:
        _delete_rows_msg
    except:
        pass

    print(f"\n*** NOTE *** ")
    NOTE = (
        f"This print utility can only report the instructions and "
        f"outcomes that can be directly inferred from the information "
        f"learned about uniques and counts during fitting. It cannot "
        f"predict any interaction effects that occur during transform of "
        f"a dataset that may ultimately cause all rows to be deleted. "
        f"It also cannot capture the effects of previously unseen "
        f"values that may be passed during transform."
    )

    if _clean_printout:
        split_NOTE = NOTE.split(' ')
        out = f""
        for idx, word in enumerate(split_NOTE):
            last_word = (idx == len(split_NOTE) - 1)
            out += f" {word}"
            if not last_word:
                next_word = f" {split_NOTE[idx + 1]}"
            if last_word or (len(out[1:]) + len(next_word)) > _max_char:
                print(out.strip())
                out = f""
        del split_NOTE, out, idx, word, last_word
    else:
        print(NOTE)

    del NOTE


    return OUTPUT_HOLDER_FOR_TEST




