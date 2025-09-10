import os
import re
import pytest
import tm_profiler as tp


class TestTmProfilerSetFunctionNameFormat(object):

    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        tp.reset()
        os.chdir("..")

    @tp.profile()
    def func(self):
        r = 0
        for _ in range(1000000):
            r = 100 / 10
        return r

    @pytest.mark.forked
    def test_set_abs_path(self, capsys):

        tp.set_name_format(tp.TpNameFormat.ABS)

        for _ in range(10):
            self.func()

        tp.print_stat()

        captured = capsys.readouterr()

        assert ("/tests/test_tp_set_function_name_format.py[func]") in captured.out
        assert re.fullmatch(
            r"-+\n## Time Profiler: #\n-+\n\|\sName\s+\|\sTime total\(s\)\s+\|\sCalls\s+\|\sTime\saverage\(s\)\s+\|\n-+\n\|\s[^|]+/tests/test_tp_set_function_name_format.py\[func\]\s+\|\s+\d+\.\d\d\d\d\s\|\s*10\s\|\s+\d+\.\d\d\d\d\s\|\n-+\n",
            captured.out,
            re.DOTALL
        )
        assert captured.err == ""

        tp.print_last()

        captured = capsys.readouterr()

        assert "/tests/test_tp_set_function_name_format.py[func]:10)" in captured.out
        assert re.fullmatch(
            r"##\sTP\s#\sFunction\s\([^|]+/tests/test_tp_set_function_name_format.py\[func\]:10\)\s-\stook:\s\d+\.\d\d\d\ds\s#\n",
            captured.out,
            re.DOTALL
        )
        assert captured.err == ""

    @pytest.mark.forked
    def test_set_relative_path(self, capsys):

        tp.set_name_format(tp.TpNameFormat.REL)

        for _ in range(10):
            self.func()

        tp.print_stat()

        captured = capsys.readouterr()

        assert "| tests/test_tp_set_function_name_format.py[func]" in captured.out
        assert re.fullmatch(
            r"-+\n## Time Profiler: #\n-+\n\|\sName\s+\|\sTime total\(s\)\s+\|\sCalls\s+\|\sTime\saverage\(s\)\s+\|\n-+\n\|\stests/test_tp_set_function_name_format.py\[func\]\s+\|\s+\d+\.\d\d\d\d\s\|\s*10\s\|\s+\d+\.\d\d\d\d\s\|\n-+\n",
            captured.out,
            re.DOTALL
        )
        assert captured.err == ""

        tp.print_last()

        captured = capsys.readouterr()

        assert "## TP # Function (tests/test_tp_set_function_name_format.py[func]:10)" in captured.out
        assert re.fullmatch(
            r"##\sTP\s#\sFunction\s\(tests/test_tp_set_function_name_format.py\[func\]:10\)\s-\stook:\s\d+\.\d\d\d\ds\s#\n",
            captured.out,
            re.DOTALL
        )
        assert captured.err == ""
