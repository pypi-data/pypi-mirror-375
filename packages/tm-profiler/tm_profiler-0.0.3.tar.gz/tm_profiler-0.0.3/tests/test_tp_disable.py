import pytest
import tm_profiler as tp


class TestTmProfilerDisable(object):
    """
    Test Time Profiler disable/enable
    """

    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        tp.reset()

    @tp.profile()
    def func1(self):
        r = 0
        for _ in range(1000000):
            r = 100 / 10
        return r

    @tp.profile()
    def func2(self):
        r = 0
        for _ in range(1000000):
            r = 100 / 10
        return r

    def test_disable_enable(self, capsys):
        # Disable time profiler
        tp.disable()

        self.func1()

        tp.print_stat()

        captured = capsys.readouterr()
        assert "func" not in captured.out
        assert captured.err == ""

        # Enable Time Profiler
        tp.enable()
        self.func1()

        tp.print_stat()

        captured = capsys.readouterr()
        assert "test_tp_disable.py[func1]" in captured.out
        assert captured.err == ""

        # Disable time profiler
        tp.disable()

        self.func2()

        tp.print_stat()

        # Capture output
        captured = capsys.readouterr()
        assert "func2" not in captured.out
        assert captured.err == ""

        # reset time profiler data
        tp.reset()

        tp.print_stat()

        captured = capsys.readouterr()
        assert "func" not in captured.out
        assert captured.err == ""
