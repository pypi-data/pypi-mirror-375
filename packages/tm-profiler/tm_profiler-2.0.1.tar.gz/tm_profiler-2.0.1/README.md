# tm_profiler
### Python - time profiler

> Package version 2.x.x is to support Python 2 (2.7 and newer versions).<br>For Python >= 3.8, please use package version >= 3.0.1.

    Developed by Normunds Pureklis (c) 2025

### Installation

Install via pip::

    $ pip install tm-profiler

## Available functions
> Imported like: `import tm_profiler` or `import tm_profiler as tp`

| Function                                   | Usage                                    |
|--------------------------------------------|------------------------------------------|
| profile(print_inline=False)                | Decorator for function time profilig     |
| print_stat(sort_by: TpSort = TpSort.NAME)  | Print all collected statistic            |
| print_last()                               | Print statistic last collected record    |
| disable()                                  | Disable profiler                         |    
| enable()                                   | Enable profiler                          |  
| reset()                                    | Reset profiler                           |
| set_output_dec(int)                        | Set profiler output decimal places       |
| set_name_format(name_format: TpNameFormat) | Set profiler output function name format |

---
> Imported like: `from tm_profiler import *`

| Function                                      | Usage                                    |
|-----------------------------------------------|------------------------------------------|
| tp_profile(print_inline=False)                | Decorator for function time profilig     |
| tp_print_stat(sort_by: TpSort = TpSort.NAME)  | Print all collected statistic            |
| tp_print_last()                               | Print statistic last collected record    |
| tp_disable()                                  | Disable profiler                         |    
| tp_enable()                                   | Enable profiler                          |  
| tp_reset()                                    | Reset profiler                           |
| tp_set_output_dec(int)                        | Set profiler output decimal places       |
| tp_set_name_format(name_format: TpNameFormat) | Set profiler output function name format |

## Usage

#### Add decorator to functions which needs to profile.<br>Run `print_stat()` function to print time statistic.

```python
import tm_profiler as tp

@tp.profile()
def func_a():
    res = 0
    for _ in range(1000000):
        res = 100 / 10
    return res

@tp.profile()
def func_b():
    res = 0
    for _ in range(1000000):
        res = 100 / 10
    return res

func_a()

for _ in range(3):
    func_b()

tp.print_stat()
```
Output:

    -------------------------------------------------------------
    ## Time Profiler: #
    -------------------------------------------------------------
    | Name            | Time total(s) | Calls | Time average(s) |
    -------------------------------------------------------------
    | main.py[func_a] |        0.0117 |     1 |          0.0117 |
    | main.py[func_b] |        0.0317 |     3 |          0.0106 |
    -------------------------------------------------------------

---
#### To print inline time statistic, use decorator function argument `print_inline=True`.

```python
import tm_profiler as tp

@tp.profile(print_inline=True)
def func_a():
    res = 0
    for _ in range(1000000):
        res = 100 / 10
    return res

func_a()
```
Output:
> NOTE: Profiler information will be printed before function result is returned!

    ## TP # Function (main.py[func_a]:1) - took: 0.0105s #
    Function result: 10.0

---
#### To print time statistic for last function run, use profiler function `print_last()`.

```python
import tm_profiler as tp

@tp.profile()
def func_a():
    res = 0
    for _ in range(1000000):
        res = 100 / 10
    return res

print(f"Function result: {func_a()}")

tp.print_last()
```
Output:

    Function result: 10.0
    ## TP # Function (main.py[func_a]:1) - took: 0.0146s #

---
#### To disable profiler, use profiler function `disable()`.<br>Statistic will not be collected and printed.<br>To enable back use function `enable()`.

```python
import tm_profiler as tp

@tp.profile()
def func_a():
    res = 0
    for _ in range(1000000):
        res = 100 / 10
    return res

tp.disable()
print(f"Function result1: {func_a()}")
tp.print_last()

tp.enable()
print(f"Function result2: {func_a()}")
tp.print_last()
```
Output:

    Function result1: 10.0
    Function result2: 10.0
    ## TP # Function (main.py[func_a]:1) - took: 0.0123s #

---
#### Use `reset()` function to reset profiler collected data.

```python
import tm_profiler as tp

@tp.profile()
def func_a():
    res = 0
    for _ in range(1000000):
        res = 100 / 10
    return res

@tp.profile()
def func_b():
    res = 0
    for _ in range(1000000):
        res = 100 / 10
    return res

func_a()

for _ in range(3):
    func_b()

tp.print_stat()

tp.reset()
tp.print_stat()

func_a()
tp.print_stat()
```
Output:

    -------------------------------------------------------------
    ## Time Profiler: #
    -------------------------------------------------------------
    | Name            | Time total(s) | Calls | Time average(s) |
    -------------------------------------------------------------
    | main.py[func_a] |        0.0117 |     1 |          0.0117 |
    | main.py[func_b] |        0.0317 |     3 |          0.0106 |
    -------------------------------------------------------------
    --------------------------------------------------
    ## Time Profiler: #
    --------------------------------------------------
    | Name | Time total(s) | Calls | Time average(s) |
    --------------------------------------------------
    --------------------------------------------------
    -------------------------------------------------------------
    ## Time Profiler: #
    -------------------------------------------------------------
    | Name            | Time total(s) | Calls | Time average(s) |
    -------------------------------------------------------------
    | main.py[func_a] |        0.0108 |     1 |          0.0108 |
    -------------------------------------------------------------

---
#### Use `set_output_dec(int)` to configure output number decimal places (affects only print output).

```python
import tm_profiler as tp

@tp.profile()
def func_a():
    return 10

func_a()

tp.set_output_dec(6)
tp.print_last()
```
Output:

    ## TP # Function (main.py[func_a]:1) - took: 0.014630s #

---
#### Use `set_name_format(name_format: TpNameFormat)` to configure how is stored decorated function name<br>(Imortant to set before any decorated function is used, as it affects how function name is stored).

```python
import tm_profiler as tp

tp.set_name_format(name_format=tp.TpNameFormat.REL)
# Available options:
#  TpNameFormat.NAME - function name (default)
#  TpNameFormat.REL - function name with relative path
#  TpNameFormat.ABS - function name with absolute path

@tp.profile()
def func_a():
    return 10

func_a()

tp.set_output_dec(6)
tp.print_last()
```

---
#### Sort profiler output data.<br>Use `sort_by` parameter for function `print_stat()` to sort output.

```python
import tm_profiler as tp

@tp.profile()
def func_a():
    return 10

func_a()

tp.print_stat(sort_by=tp.TpSort.CALLS)
# Available options:
#  TpSort.NAME  - sort by name (default)
#  TpSort.CALLS - sort by count of calls
#  TpSort.TOTAL - sort by total time
#  TpSort.AVG   - sort by average time
```
