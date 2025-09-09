# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



from ._array_sparsity import array_sparsity
from ._benchmarking import (
    time_memory_benchmark,
    timer
)
from ._check_pipeline import check_pipeline
from ._feature_name_mapper import feature_name_mapper
from ._get_methods_out_of_class import get_methods_out_of_class
from ._get_module_name import get_module_name
from ._logger import logger
from ._inf_masking import inf_mask
from ._nan_masking import (
    nan_mask_numerical,
    nan_mask_string,
    nan_mask
)
from ._permuter import permuter
from ._print_inspect_stack import print_inspect_stack
from ._remove_characters import remove_characters
from ._serial_index_mapper import serial_index_mapper
from ._union_find import union_find



# from https://docs.python.org/3/reference/simple_stmts.html:
# The public names defined by a module are determined by checking the
# module’s namespace for a variable named __all__;  if defined, it must
# be a sequence of strings which are names defined or imported by that
# module. The names given in __all__ are all considered public and are
# required to exist. If __all__ is not defined, the set of public names
# includes all names found in the module’s namespace which do not begin
# with an underscore character ('_'). __all__ should contain the entire
# public API. It is intended to avoid accidentally exporting items that
# are not part of the API (such as library modules which were imported
# and used within the module).




__all__ = [
    "array_sparsity",
    "check_pipeline",
    "feature_name_mapper",
    "get_methods_out_of_class",
    "get_module_name",
    "inf_mask",
    "logger",
    "nan_mask",
    "nan_mask_numerical",
    "nan_mask_string",
    "permuter",
    "print_inspect_stack",
    "remove_characters",
    "serial_index_mapper",
    "time_memory_benchmark",
    "timer",
    "union_find"
]




