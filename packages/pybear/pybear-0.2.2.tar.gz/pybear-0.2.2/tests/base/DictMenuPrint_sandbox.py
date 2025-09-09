# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



if __name__ == '__main__':


    from pybear.base._DictMenuPrint import DictMenuPrint as DMP


    test_start = lambda name: print(f'\nSTARTING {name}...')
    test_pass = lambda name: print(f'\033[92m*** {name} PASSED ***\033[0m')
    test_fail = lambda name, reason: print(
        f'\033[91m*** {name} FAILED. REASON = {reason} ***\033[0m'
    )

    def measuring_stick(_len: int) -> None:
        offset = len("MEASURING STICK")
        out = 'MEASURING STICK' + (_len-offset-1)*'-' + '|'
        assert len(out) == _len
        print(out)


    # TEST DISPLAY OF MANY SMALL OPTIONS ##########################################
    name = 'DISPLAY OF MANY SMALL OPTIONS, disp_width=50'
    test_start(name)

    VALUES = [f'Test{_}' for _ in range(0, 27)]
    DICT = dict((zip(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), VALUES)))
    measuring_stick(50)
    DMP(DICT, disp_width=50).choose('Pick one already')
    # END TEST DISPLAY OF MANY SMALL OPTIONS ######################################

    # TEST DISPLAY OF MANY SMALL OPTIONS ##########################################
    name = 'DISPLAY OF MANY SMALL OPTIONS, disp_width=120'
    test_start(name)

    VALUES = [f'Test{_}' for _ in range(0, 27)]
    DICT = dict((zip(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), VALUES)))
    measuring_stick(120)
    DMP(DICT, disp_width=120).choose('Pick one already')
    # END TEST DISPLAY OF MANY SMALL OPTIONS ######################################

    # TEST DISPLAY OF MANY MEDIUM OPTIONS #########################################
    name = 'DISPLAY OF MANY MEDIUM OPTIONS, disp_width=120'
    test_start(name)

    VALUES = [f'Test of many medium-sized options{_}' for _ in range(0, 27)]
    DICT = dict((zip(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), VALUES)))
    measuring_stick(120)
    DMP(DICT, disp_width=120).choose('Pick one already')
    # END TEST DISPLAY OF MANY MEDIUM OPTIONS #####################################

    # TEST DISPLAY OF LONG OPTIONS ################################################
    name = 'DISPLAY OF EXTREMELY LONG OPTIONS, disp_width=90'
    test_start(name)

    VALUES = [(f'Test of extremely long options, so long they go past the disp_width, '
               f'so they should be truncated{_}') for _ in range(0, 27)]
    DICT = dict((zip(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), VALUES)))
    measuring_stick(90)
    DMP(DICT, disp_width=90).choose('Pick one already')
    # END TEST DISPLAY OF LONG OPTIONS ############################################


    # TEST fixed_col_width DISPLAYS CORRECTLY #####################################
    name = 'TEST fixed_col_width DISPLAYS CORRECTLY, disp_width=default, fixed_col_width=40'
    test_start(name)
    SHORT_DICT = {'a': 'Test 1', 'b': 'Test 2', 'c': 'Test 3'}
    MEDIUM_DICT = {
        'a': 'Medium len text Test 1',
        'b': 'Medium len text Test 2',
        'c': 'Medium len text Test 3'
    }
    LONG_DICT = {
        'a': 'Print long display of text Test 1',
        'b': 'Print long display of text Test 2',
        'c': 'Print long display of text Test 3'
    }
    for name, SAMPLE_DICT in zip(
            ('SHORT_DICT', 'MEDIUM_DICT', 'LONG_DICT'),
            (SHORT_DICT, MEDIUM_DICT, LONG_DICT)
    ):
        print(f'{name}:')
        measuring_stick(40)
        DMP(SAMPLE_DICT, fixed_col_width=40).choose('Pick one already')
        print()

    print(f'ALL PRINTOUTS SHOULD HAVE SAME MARGINS')
    # END TEST fixed_col_width DISPLAYS CORRECTLY #################################


    # TEST allowed DISPLAYS CORRECTLY #############################################
    name = 'TEST allowed DISPLAYS CORRECTLY, disp_width=default, fixed_col_width=default'
    test_start(name)
    print(f'Only a AND c SHOULD BE SHOWN')
    DICT = {'a': 'Test 1', 'b': 'Test 2', 'c': 'Test 3'}
    DMP(DICT, allowed='ac').choose('Pick one already')
    # END TEST allowed DISPLAYS CORRECTLY #########################################


    # TEST disallowed DISPLAYS CORRECTLY ##########################################
    name = 'TEST disallowed DISPLAYS CORRECTLY, disp_width=default, fixed_col_width=default'
    test_start(name)
    print(f'Only a AND b SHOULD BE SHOWN')
    DICT = {'a': 'Test 1', 'b': 'Test 2', 'c': 'Test 3'}
    DMP(DICT, disallowed='c').choose('Pick one already')
    # END TEST allowed DISPLAYS CORRECTLY #########################################


    # TEST choose RETURNS CORRECTLY ###############################################
    name = 'TEST choose RETURNS CORRECTLY, disp_width=default, fixed_col_width=default'
    test_start(name)
    DICT = {'a': 'Test 1', 'b': 'Test 2', 'c': 'Test 3'}
    TestClass = DMP(DICT)
    _ = TestClass.choose('Pick one already')
    print(f'TestClass.choose RETURNED "{_}"')
    # END TEST choose RETURNS CORRECTLY ###########################################





