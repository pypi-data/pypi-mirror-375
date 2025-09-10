import os
import time
import types
from enum import Enum
from functools import wraps

# NOTE: __version__ needs to be in sync with __init__.py
__version__ = '0.0.3'


class TpNameFormat(Enum):
    """
    Enum class for function name-format strings
    """
    NAME = "name"
    ABS = "abs"
    REL = "rel"


class TpSort(Enum):
    """
    Enum class for output sorting
    """
    NAME = "name"
    CALLS = "calls"
    TOTAL = "total"
    AVG = "avg"


class TimeProfiler:
    _instance = None

    function_name_format = TpNameFormat.NAME
    dec_places = 4

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.init()
        return cls._instance

    def init(self):
        self.__profiler_enabled = True
        self.__time_counters: dict[str, float] = {}
        self.__call_counters: dict[str, int] = {}
        self.__last_name: str = "none"
        self.__last_time: float = .0
        self.__last_call: int = 0

    @classmethod
    def reset_profiler(cls) -> None:
        """
        Resets the profiler
        :return: None
        """
        cls._instance = None

    def is_enabled(self) -> bool:
        """
        Returns True if the profiler is enabled.
        :return: is profiling enabled or not
        :rtype: bool
        """
        return self.__profiler_enabled

    def set_profiler_enable_status(self, enabled=True) -> None:
        """
        Sets the profiler enabled status
        :param enabled:
        :type enabled: bool
        :return: None
        """
        self.__profiler_enabled = enabled

    def gen_print_line(self, name: str, call: int, took: float) -> str:
        """
        Format string for one Time Profiler record output.
        :param name: Function name
        :type name: str
        :param call: Number of function calls
        :type call: int
        :param took: Function time taken
        :type took: float
        :return: Formated string
        :rtype: str
        """
        return f"## TP # Function ({name}:{call}) - took: {took:.{self.dec_places}f}s #"

    def count(self, sec: float, func, print_inline: bool = False) -> None:
        if isinstance(func, types.FunctionType):
            func_name = func.__name__
            if self.function_name_format == TpNameFormat.ABS:
                func_name = f"{os.path.abspath(func.__code__.co_filename)}[{func_name}]"
            elif self.function_name_format == TpNameFormat.REL:
                func_name = f"{os.path.relpath(func.__code__.co_filename)}[{func_name}]"
            elif self.function_name_format == TpNameFormat.NAME:
                func_name = f"{os.path.basename(func.__code__.co_filename)}[{func_name}]"

        elif isinstance(func, str):
            func_name = func
        else:
            func_name = "__none__"

        if func_name not in self.__time_counters:
            self.__time_counters[func_name] = 0
            self.__call_counters[func_name] = 0
        self.__time_counters[func_name] += sec
        self.__call_counters[func_name] += 1
        self.__last_name = func_name
        self.__last_time = sec
        self.__last_call = self.__call_counters[func_name]

        if print_inline:
            print(self.gen_print_line(func_name, self.__last_call, sec))

    def get_last(self) -> str:
        """
        Get Time Profiler last recorded entry.
        :return: Time Profiler last recorded entry
        :rtype: str
        """
        return self.gen_print_line(self.__last_name, self.__last_call, self.__last_time)

    def _get_sorted_stat(self, sort_by: TpSort = TpSort.NAME) -> list[tuple[str, int, float, float]]:
        """
        Get Time Profiler sorted statistic data.
        :param sort_by: parameter for sorting statistics [name, calls, total, avg]
        :type sort_by: TpSort
        :return: list of tuples with sorted statistic data
        :rtype: list[tuple[str, int, float, float]]
        """
        stat = [(k, self.__call_counters[k], v, v / self.__call_counters[k]) for k, v in self.__time_counters.items()]

        if sort_by == TpSort.NAME:
            return sorted(stat, key=lambda item: item[0])

        if sort_by == TpSort.CALLS:
            return sorted(stat, key=lambda item: item[1])

        if sort_by == TpSort.TOTAL:
            return sorted(stat, key=lambda item: item[2])

        if sort_by == TpSort.AVG:
            return sorted(stat, key=lambda item: item[3])

        return sorted(stat, key=lambda item: item[0])

    def gen_statistic_table(self, sort_by: TpSort = TpSort.NAME) -> str:
        """
        Function generate time profiler statistic table formated to print in commandline.

        :param sort_by: parameter for sorting statistics [name, calls, total, avg]
        :type sort_by: TpSort
        :return: Time profiler statistic table
        :rtype: str
        """
        headers = [("Name", "Time total(s)", "Calls", "Time average(s)")]
        calls_list = headers + [(n, f"{t:.{self.dec_places}f}", str(c), f"{a:.{self.dec_places}f}") for n, c, t, a in self._get_sorted_stat(sort_by)]

        c_lens = [0, 0, 0, 0]
        for x in calls_list:
            for i, y in enumerate(x):
                c_lens[i] = max(len(y), c_lens[i])

        ret = []
        sp = ""
        for i, c in enumerate(calls_list):
            if i == 0:
                h_str = f"| {c[0]:<{c_lens[0]}} | {c[1]:<{c_lens[1]}} | {c[2]:<{c_lens[2]}} | {c[3]:<{c_lens[3]}} |"
                sp = "-" * len(h_str)
                ret.append(sp)
                ret.append("## Time Profiler: #")
                ret.append(sp)
                ret.append(h_str)
                ret.append(sp)
                continue
            ret.append(f"| {c[0]:<{c_lens[0]}} | {c[1]:>{c_lens[1]}} | {c[2]:>{c_lens[2]}} | {c[3]:>{c_lens[3]}} |")
        ret.append(sp)

        return "\n".join(ret)

    def __repr__(self):
        return self.gen_statistic_table()


def enable() -> None:
    """
    Enable Time Profiler
    :return: None
    """
    TimeProfiler().set_profiler_enable_status(True)


def disable() -> None:
    """
    Disable Time Profiler
    :return: None
    """
    TimeProfiler().set_profiler_enable_status(False)


def reset() -> None:
    """
    Reset Time Profiler
    :return: None
    """
    TimeProfiler.reset_profiler()


def set_output_dec(dec: int) -> None:
    """
    Set time profiler output decimal places.
    :param dec: decimal places
    :type dec: int
    :return: none
    """
    TimeProfiler().dec_places = dec


def set_name_format(name_format: TpNameFormat) -> None:
    """
    Set time profiler - function name format.
    :param name_format: function name format
    :type name_format: TpNameFormat
    :return: None
    """
    TimeProfiler().function_name_format = name_format


def print_stat(sort_by: TpSort = TpSort.NAME) -> None:
    """
    Print time profiler statistic table.
    :param sort_by: Sort output column
    :type sort_by: TpSort
    :return: None
    """
    if TimeProfiler().is_enabled():
        print(TimeProfiler().gen_statistic_table(sort_by))


def print_last() -> None:
    """
    Print Time Profiler last recorded entry.
    :return: None
    """
    if TimeProfiler().is_enabled():
        print(TimeProfiler().get_last())


# Decorators
def profile(print_inline=False):
    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            if TimeProfiler().is_enabled():
                s_time = time.time()

                # Call wrapped function
                res = func(*args, **kwargs)

                e_time = time.time()
                TimeProfiler().count(e_time - s_time, func, print_inline)
                return res
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator
