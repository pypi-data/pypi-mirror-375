import tm_profiler as tp


class TestTmProfilerReset(object):
    """
    Test Time profiler reset.
    """

    @tp.profile()
    def func(self):
        r = 0
        for _ in range(1000000):
            r = 100 / 10
        return r

    def test_reset(self, capsys):

        # 1. run
        self.func()
        tp.print_last()

        captured = capsys.readouterr()
        assert "## TP # Function (test_tp_reset.py[func]:1) - took:" in captured.out
        assert captured.err == ""

        # clean captured output
        capsys.readouterr()
        # 2. run
        self.func()
        # tp.reset()

        tp.print_last()

        captured = capsys.readouterr()
        assert "## TP # Function (test_tp_reset.py[func]:1) - took:" not in captured.out
        assert "## TP # Function (test_tp_reset.py[func]:2) - took:" in captured.out
        assert captured.err == ""

        # clean captured output
        capsys.readouterr()

        # reset time profiler data
        tp.reset()
        # 3. run
        self.func()

        tp.print_last()

        captured = capsys.readouterr()
        assert "## TP # Function (test_tp_reset.py[func]:2) - took:" not in captured.out
        assert "## TP # Function (test_tp_reset.py[func]:1) - took:" in captured.out
        assert captured.err == ""
