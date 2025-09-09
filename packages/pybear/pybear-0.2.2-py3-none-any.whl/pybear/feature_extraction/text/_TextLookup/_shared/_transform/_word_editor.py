# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from ......base._validate_user_input import validate_user_str


def _word_editor(
    _word: str,
    _prompt: str
) -> str:
    """Validation function for single words entered by user.

    Parameter
    ---------
    _word : str
        The word prompting a new entry by the user.
    _prompt : str
        A special prompt.

    Returns
    -------
    _word : str
        The new word entered by the user.

    """


    if not isinstance(_word, str):
        raise TypeError(f"'word' must be a string")

    if not isinstance(_prompt, str):
        raise TypeError(f"'prompt' must be a string")

    while True:

        _word = input(f'{_prompt} > ')

        if validate_user_str(
            f'User entered *{_word}* -- accept? (y/n) > ', 'YN'
        ) == 'Y':
            break


    return _word


