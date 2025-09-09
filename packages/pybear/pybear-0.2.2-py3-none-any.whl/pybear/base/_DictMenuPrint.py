# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import numbers

from ._validate_user_input import validate_user_str_cs



class DictMenuPrint:
    """Manage the display and operation of an interactive user menu.

    Display the allowed sub-menu options from a full menu to the screen.

    The :meth:`choose` method displays the allowed menu options and
    offers a validated prompt to select one of the options.

    Parameters
    ----------
    MENU_DICT : dict[str, str]
        Required. A Dictionary of unit-length alpha characters as keys
        and the descriptions of their associated actions as values. Keys
        are case-sensitive.
    disp_width : int, default=80
        The maximum number of characters to display per line.
    fixed_col_width : int | None, default=None
        Set a fixed width for each column of menu items in the display.
        DMP will determine a number of columns that causes the overall
        width of the display to be less than or equal to `disp_width`.
    allowed : str | None, default=None
        Can only enter this if `disallowed` is not entered, cannot enter
        both. The action keys that are allowed to be selected from the
        full selection available in `MENU_DICT`. case-sensitive. Enter
        as a contiguous sequence of characters.
    disallowed : str | None, default=None
        Can only enter this if `allowed` is not entered, cannot enter
        both. The action keys that are not allowed to be selected from
        `MENU_DICT`. `allowed` becomes the space of action keys that are
        not disallowed. Case-sensitive. Enter as a contiguous sequence
        of characters.

    Attributes
    ----------
    allowed : str
        The positive space out of `MENU_DICT` that the user is allowed
        to select from. This attribute is always the set of allowed
        options determined at instantiation. The instance attribute IS
        NOT overwritten by any `allowed` or `disallowed` passed to the
        methods. The `allowed` passed to or determined by the methods
        is used only temporarily in place of the permanent `allowed`
        attribute. The menu associated with the stored `allowed`
        attribute is always available as the default menu.
    all_allowed_str : str
        The full set of possible options taken from the keys of
        `MENU_DICT`.
    disp_width : int
        The maximum character display width passed at instantiation or
        the default if not passed.
    fixed_col_width : int
        The fixed column width within the full display width passed at
        instantiation or the default if not passed.
    MENU_DICT : dict[str, str]
        The `MENU_DICT` passed at instantiation.

    Examples
    --------
    >>> MENU_DICT = {
    ...    'a': 'Apply Option 1', 'b': 'Apply Option 2',
    ...    'c': 'Apply Option 3', 'd': 'Apply Option 4'
    ... }
    >>> DMP = DictMenuPrint(
    ...    MENU_DICT,
    ...    disp_width = 80,
    ...    fixed_col_width = None,
    ...    allowed = 'abcd',
    ...    disallowed = None
    ... )
    >>> DMP.choose(allowed='ab', prompt='pick one')   # doctest:+SKIP
    a) Apply Option 1     b) Apply Option 2
    pick one >

    """


    def __init__(
        self,
        MENU_DICT:dict[str, str],
        *,
        disp_width:int = 80,
        fixed_col_width:int | None = None,
        allowed:str | None = None,
        disallowed:str | None = None
    ) -> None:
        """Initialize the DictMenuPrint instance."""

        # validation v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # MENU_DICT -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        if not isinstance(MENU_DICT, dict):
            raise TypeError(f"'MENU_DICT' must be a dictionary")

        if len(MENU_DICT) == 0:
            raise ValueError(f"'MENU_DICT' cannot be empty")

        if not all(map(isinstance, MENU_DICT, (str for _ in MENU_DICT))):
            raise TypeError(f"MENU_DICT keys must be str.")

        if not all(map(
            isinstance, MENU_DICT.values(), (str for _ in MENU_DICT)
        )):
            raise TypeError(f"MENU_DICT values must be str.")

        if max(map(len, MENU_DICT.keys())) != 1:
            raise ValueError(f"Illegal key in MENU_DICT, len must be 1.")

        self.MENU_DICT = MENU_DICT
        # END MENU_DICT -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # MENU_DICT cant have duplicate keys, its a dictionary
        self.all_allowed_str = ''.join(MENU_DICT.keys())

        # disp_width -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        if not isinstance(disp_width, numbers.Integral):
            raise TypeError(f"'disp_width' must be a non-boolean integer")
        if isinstance(disp_width, bool):
            raise TypeError(f"'disp_width' must be a non-boolean integer")
        if disp_width < 10:
            raise ValueError(f"'disp_width' must be >=10")

        self.disp_width = disp_width
        # END disp_width -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # fixed_column_width -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        if not isinstance(fixed_col_width, (numbers.Integral, type(None))):
            raise TypeError(f"'fixed_col_width' must be an integer or None")
        if isinstance(fixed_col_width, bool):
            raise TypeError(f"'fixed_col_width' must be a non-boolean integer")
        if fixed_col_width is not None and fixed_col_width < 10:
            raise ValueError(f"'disp_width' must be >=10")
        if fixed_col_width and fixed_col_width > disp_width:
            raise ValueError(f"'fixed_col_width' must be <= 'disp_width'")

        self.fixed_col_width = fixed_col_width
        # END fixed_column_width -- -- -- -- -- -- -- -- -- -- -- -- -- --

        self.allowed = self._val_allowed_disallowed_and_get_allowed(
            allowed,
            disallowed
        )

        # END allowed / disallowed -- -- -- -- -- -- -- -- -- -- -- --

        # END validation v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v


    def _val_allowed_disallowed_and_get_allowed(
        self,
        _allowed:str | None = None,
        _disallowed:str | None = None
    ) -> str:
        """Validate `allowed` & `disallowed`, determine allowed, and
        return it.

        Parameters
        ----------
        _allowed : str | None, default = None
            Options in the full menu that the user is allowed to choose.
        _disallowed : str | None, default = None
            Options in the full menu that the user is not allowed to
            choose.

        Returns
        -------
        __ : str
            The allowed subset from `all_allowed_str`, arrived at by
            applying the characters in `allowed` and `disallowed` against
            the characters in `all_allowed_str`.

        """

        # allowed / disallowed -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if not isinstance(_allowed, (str, type(None))):
            raise TypeError(f"'allowed' must be a str or None")

        if not isinstance(_disallowed, (str, type(None))):
            raise TypeError(f"'disallowed' must be a str or None")

        _allowed = None if _allowed == '' else _allowed
        _disallowed = None if _disallowed == '' else _disallowed

        if _allowed is not None and _disallowed is not None:
            raise ValueError(
                f"cannot enter both 'allowed' and 'disallowed', must be "
                f"one or the other or neither."
            )
        elif _allowed is None and _disallowed is None:
            _allowed = self.all_allowed_str

        elif _allowed is not None:   #  _disallowed is None

            # CLEAR OUT ANY DUPLICATES THAT MAY BE IN ALLOWED
            _allowed = ''.join(list(set(_allowed)))

            if not all(map(lambda x: x in self.all_allowed_str, _allowed)):
                raise ValueError(
                    f"Invalid key in 'allowed' ({_allowed}), must be in "
                    f"{self.all_allowed_str}."
                )

        elif _disallowed is not None:   # _allowed is None

            # CLEAR OUT ANY DUPLICATES THAT MAY BE IN disallowed
            _disallowed = ''.join(list(set(_disallowed)))

            if not all(map(lambda x: x in self.all_allowed_str, _disallowed)):
                raise ValueError(
                    f"Invalid key in 'disallowed' ({_disallowed}), must "
                    f"be in {self.all_allowed_str}."
                )

            _allowed = ''.join(set(self.all_allowed_str) - set(_disallowed))

        if len(_allowed) == 0:
            raise ValueError(
                f"the given values for 'allowed' or 'disallowed' have left "
                f"no allowed menu choices."
            )

        return _allowed


    def _generate_subdict_and_print(self, _allowed: str):
        """Print the allowed menu options to screen.

        Parameters
        ----------
        allowed : str
            The subset of the fullset of menu options that are to be
            printed to screen.

        Returns
        -------
        None

        """

        SUB_DICT = {
            k: v for k, v in self.MENU_DICT.items() if k in _allowed
        }

        if self.fixed_col_width is not None:
            num_cols = self.disp_width // int(self.fixed_col_width)
            ljust = int(self.fixed_col_width)
        else:  # fixed_col_width is None
            # +3 FOR '(' + <the menu option> + ')' +2 FOR BUFFER
            _max_desc_len = max(map(len, SUB_DICT.values())) + 3 + 2
            num_cols = max(1, self.disp_width // _max_desc_len)
            ljust = self.disp_width // num_cols
            del _max_desc_len

        # attrs are MENU_DICT, SUB_DICT, all_allowed_str, fixed_column_width,
        # allowed, num_cols, ljust

        for itr, (k, v) in enumerate(SUB_DICT.items()):
            print_line = f'{v[:ljust-5]}({k})'.ljust(ljust)
            if itr % num_cols < num_cols - 1:
                print(print_line, end='')
            else:
                print(print_line)

        del print_line


    def choose(
        self,
        prompt:str,
        *,
        allowed:str | None = None,
        disallowed:str | None = None
    ) -> str:
        """Displays the allowed menu options to the screen.

        Prompts the user for a case-sensitive selection. Returns the
        single-character action command selected by the user. The default
        menu associated with the `allowed` action keys that were passed
        at instantiation is available by passing no kwargs, or pass
        custom `allowed` or `disallowed` to generate a different menu
        for the one time. The custom `allowed` or `disallowed` that are
        passed here DO NOT overwrite the `allowed` attribute of the
        instance, that will always be available as the default menu.

        Parameters
        ----------
        allowed : str | None, default=None
            Can only enter this if `disallowed` is not entered,
            cannot enter both. The action keys that are allowed to be
            selected from the full section available in `MENU_DICT`.
            Case-sensitive. Enter as a contiguous sequence of characters.
        disallowed : str | None, default=None
            Can only enter this if `allowed` is not entered, cannot
            enter both. The action keys that are not allowed to be
            selected from `MENU_DICT`. `allowed` becomes the space of
            action keys that are not disallowed. Case-sensitive. Enter
            as a contiguous sequence of characters.

        Returns
        -------
        char : str
            The value of the menu item selected by the user.

        """

        if not isinstance(prompt, str):
            raise TypeError(f"'prompt' must be a string")

        if allowed is None and disallowed is None:
            _allowed = self.allowed
        else:
            _allowed = \
                self._val_allowed_disallowed_and_get_allowed(
                    allowed,
                    disallowed
                )

        self._generate_subdict_and_print(_allowed)


        return validate_user_str_cs(f'\n{prompt} > ', _allowed)





