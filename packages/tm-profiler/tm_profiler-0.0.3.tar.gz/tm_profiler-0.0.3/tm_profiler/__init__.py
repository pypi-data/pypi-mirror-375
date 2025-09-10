"""
Time Profiler
=============

The tm_profiler module for time profiling of functions

+---------------+--------------------------------------------+
| GitHub        | https://github.com/NorchaHack/tm_profiler  |
+---------------+--------------------------------------------+
| Pypi          | https://pypi.org/project/tm-profiler       |
+---------------+--------------------------------------------+


Installation
============

Releases of `tm_profiler` can be installed
using pip

    pip install tm-profiler

Time Profiler Basic Usage
=========================

import tm_profiler as tp

@tp.profile()
def func():
    return "Func - return value"

func()

....

tp.print_stat()

Output:
------------------------------------------------------------------
## Time Profiler: #
------------------------------------------------------------------
| Name                 | Time total(s) | Calls | Time average(s) |
------------------------------------------------------------------
| main.py[func]        |        0.0001 |     1 |          0.0001 |
------------------------------------------------------------------

"""

from .tm_profiler import (profile, enable, disable, reset,
                          print_stat, print_last,
                          set_output_dec, set_name_format,
                          TpNameFormat, TpSort)

from .tm_profiler import (profile as tp_profile,
                          enable as tp_enable,
                          disable as tp_disable,
                          reset as tp_reset,
                          print_stat as tp_print_stat,
                          print_last as tp_print_last,
                          set_output_dec as tp_set_output_dec,
                          set_name_format as tp_set_name_format,
                          TpNameFormat,
                          TpSort
                          )

__all__ = [
    "tp_profile",
    "tp_enable",
    "tp_disable",
    "tp_reset",
    "tp_print_stat",
    "tp_print_last",
    "tp_set_output_dec",
    "tp_set_name_format",
    "TpNameFormat",
    "TpSort"
]

__author__ = "Normunds Pureklis <norchahack@gmail.com>"
__status__ = "development"
__version__ = "0.0.3"
__date__ = "07 Sep 2025"
