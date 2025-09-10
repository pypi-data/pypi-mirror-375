import re
import pytest
import tm_profiler as tp


class TestTmProfilerOutputInline(object):

    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        tp.reset()

    @tp.profile(print_inline=True)
    def func(self):
        r = 0
        for _ in range(1000000):
            r = 100 / 10
        return "returned value"

    @pytest.mark.forked
    def test_inline_output(self, capsys):

        print(self.func())

        captured = capsys.readouterr()

        assert re.fullmatch(
            r"##\sTP\s#\sFunction\s\(test_tp_output_inline.py\[func\]:1\)\s-\stook:\s\d+\.\d\d\d\ds\s#\nreturned value\n",
            captured.out,
            re.DOTALL
        )
        assert captured.err == ""
