# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#


import os


def _read_green_eggs_and_ham():

    module_dir = os.path.dirname(os.path.abspath(__file__))
    file = '_green_eggs_and_ham'

    STRINGS = []
    with open(os.path.join(module_dir, file)) as f:
        for line in f:
            if line == '\n':
                continue
            STRINGS.append(line.replace('\n', ''))


    return STRINGS








