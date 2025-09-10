import re
import pytest
import tm_profiler as tp


class TestTmProfilerSetDecimalPlaces(object):

    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        tp.reset()

    @tp.profile()
    def func(self):
        r = 0
        for _ in range(1000000):
            r = 100 / 10
        return r

    @pytest.mark.forked
    def test_output_last_default(self, capsys):
        """
        Test default last record output with 4 decimal palaces
        """
        self.func()

        tp.print_last()

        captured = capsys.readouterr()

        assert re.fullmatch(
            r"##\sTP\s#\sFunction\s\(test_tp_set_dec_places.py\[func\]:1\)\s-\stook:\s\d+\.\d\d\d\ds\s#\n",
            captured.out,
            re.DOTALL
        )
        assert captured.err == ""

    @pytest.mark.forked
    def test_output_last_six_dec_places(self, capsys):
        """
        Test last record output with 6 decimal palaces
        """
        tp.set_output_dec(6)

        self.func()

        tp.print_last()

        captured = capsys.readouterr()

        assert re.fullmatch(
            r"##\sTP\s#\sFunction\s\(test_tp_set_dec_places.py\[func\]:1\)\s-\stook:\s\d+\.\d\d\d\d\d\ds\s#\n",
            captured.out,
            re.DOTALL
        )
        assert captured.err == ""
