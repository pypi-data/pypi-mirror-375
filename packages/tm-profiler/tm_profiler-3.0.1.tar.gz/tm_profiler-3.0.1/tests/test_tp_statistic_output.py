import re
import pytest
import tm_profiler as tp


class TestTmProfilerSortOutput(object):

    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        tp.reset()

    @tp.profile()
    def func_a(self):
        r = 0
        for _ in range(100000):
            r = 100 / 10
        return r

    @tp.profile()
    def func_b(self):
        r = 0
        for _ in range(10000):
            r = 100 / 10
        return r

    @tp.profile()
    def func_c(self):
        r = 0
        for _ in range(1000000):
            r = 100 / 10
        return r

    @pytest.mark.forked
    def test_sorted_by_name(self, capsys):

        for _ in range(8):
            self.func_b()
        for _ in range(5):
            self.func_c()
        for _ in range(10):
            self.func_a()

        tp.print_stat()

        captured = capsys.readouterr()

        expected = [
            r"-+",
            r"## Time Profiler: #",
            r"-+",
            r"\|\sName\s+\|\sTime total\(s\)\s+\|\sCalls\s+\|\sTime\saverage\(s\)\s+\|",
            r"-+",
            r"\|\stest_tp_statistic_output.py\[func_a\]\s+\|\s+\d+\.\d\d\d\d\s\|\s*10\s\|\s+\d+\.\d\d\d\d\s\|",
            r"\|\stest_tp_statistic_output.py\[func_b\]\s+\|\s+\d+\.\d\d\d\d\s\|\s*8\s\|\s+\d+\.\d\d\d\d\s\|",
            r"\|\stest_tp_statistic_output.py\[func_c\]\s+\|\s+\d+\.\d\d\d\d\s\|\s*5\s\|\s+\d+\.\d\d\d\d\s\|",
            r"-+",
        ]

        for i, line in enumerate(captured.out.splitlines()):
            assert re.fullmatch(
                expected[i],
                line,
                re.DOTALL
            )
        assert captured.err == ""

    @pytest.mark.forked
    def test_sorted_by_calls(self, capsys):

        for _ in range(8):
            self.func_b()
        for _ in range(5):
            self.func_c()
        for _ in range(10):
            self.func_a()

        tp.print_stat(sort_by=tp.TpSort.CALLS)

        captured = capsys.readouterr()

        expected = [
            r"-+",
            r"## Time Profiler: #",
            r"-+",
            r"\|\sName\s+\|\sTime total\(s\)\s+\|\sCalls\s+\|\sTime\saverage\(s\)\s+\|",
            r"-+",
            r"\|\stest_tp_statistic_output.py\[func_c\]\s+\|\s+\d+\.\d\d\d\d\s\|\s*5\s\|\s+\d+\.\d\d\d\d\s\|",
            r"\|\stest_tp_statistic_output.py\[func_b\]\s+\|\s+\d+\.\d\d\d\d\s\|\s*8\s\|\s+\d+\.\d\d\d\d\s\|",
            r"\|\stest_tp_statistic_output.py\[func_a\]\s+\|\s+\d+\.\d\d\d\d\s\|\s*10\s\|\s+\d+\.\d\d\d\d\s\|",
            r"-+",
        ]

        for i, line in enumerate(captured.out.splitlines()):
            assert re.fullmatch(
                expected[i],
                line,
                re.DOTALL
            )
        assert captured.err == ""

    @pytest.mark.forked
    def test_sorted_by_average(self, capsys):

        for _ in range(10):
            self.func_a()
        for _ in range(10):
            self.func_b()
        for _ in range(10):
            self.func_c()

        tp.print_stat(sort_by=tp.TpSort.TOTAL)

        captured = capsys.readouterr()

        expected = [
            r"-+",
            r"## Time Profiler: #",
            r"-+",
            r"\|\sName\s+\|\sTime total\(s\)\s+\|\sCalls\s+\|\sTime\saverage\(s\)\s+\|",
            r"-+",
            r"\|\stest_tp_statistic_output.py\[func_b\]\s+\|\s+\d+\.\d\d\d\d\s\|\s*10\s\|\s+\d+\.\d\d\d\d\s\|",
            r"\|\stest_tp_statistic_output.py\[func_a\]\s+\|\s+\d+\.\d\d\d\d\s\|\s*10\s\|\s+\d+\.\d\d\d\d\s\|",
            r"\|\stest_tp_statistic_output.py\[func_c\]\s+\|\s+\d+\.\d\d\d\d\s\|\s*10\s\|\s+\d+\.\d\d\d\d\s\|",
            r"-+",
        ]

        for i, line in enumerate(captured.out.splitlines()):
            assert re.fullmatch(
                expected[i],
                line,
                re.DOTALL
            )
        assert captured.err == ""

    @pytest.mark.forked
    def test_sorted_by_total(self, capsys):

        for _ in range(10):
            self.func_a()
        for _ in range(10):
            self.func_b()
        for _ in range(10):
            self.func_c()

        tp.print_stat(sort_by=tp.TpSort.AVG)

        captured = capsys.readouterr()

        expected = [
            r"-+",
            r"## Time Profiler: #",
            r"-+",
            r"\|\sName\s+\|\sTime total\(s\)\s+\|\sCalls\s+\|\sTime\saverage\(s\)\s+\|",
            r"-+",
            r"\|\stest_tp_statistic_output.py\[func_b\]\s+\|\s+\d+\.\d\d\d\d\s\|\s*10\s\|\s+\d+\.\d\d\d\d\s\|",
            r"\|\stest_tp_statistic_output.py\[func_a\]\s+\|\s+\d+\.\d\d\d\d\s\|\s*10\s\|\s+\d+\.\d\d\d\d\s\|",
            r"\|\stest_tp_statistic_output.py\[func_c\]\s+\|\s+\d+\.\d\d\d\d\s\|\s*10\s\|\s+\d+\.\d\d\d\d\s\|",
            r"-+",
        ]

        for i, line in enumerate(captured.out.splitlines()):
            assert re.fullmatch(
                expected[i],
                line,
                re.DOTALL
            )
        assert captured.err == ""
