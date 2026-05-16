from unittest.mock import patch, MagicMock
import subprocess
import pytest
from vmstat_visualizer.checks.check import check_vmstat_columns


class TestCheckVmstatColumns:
    VMSTAT_HEADER_WITH_ST_GU = (
        "procs -----------memory---------- ---swap-- -----io---- -system-- -------cpu-------\n"
        " r  b   swpd   free  inact active   si   so    bi    bo   in   cs us sy id wa st gu\n"
        " 1  0      0  15234    128   1059    0    0     4     1   71  111  0  0 99  0  0  0\n"
    )
    VMSTAT_HEADER_WITHOUT_GU = (
        "procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----\n"
        " r  b   swpd   free  inact active   si   so    bi    bo   in   cs us sy id wa st\n"
        " 1  0      0  15234    128   1059    0    0     4     1   71  111  0  0 99  0  0\n"
    )

    @patch("vmstat_visualizer.checks.check.subprocess.run")
    def test_returns_true_true_when_st_and_gu_present(self, mock_run):
        mock_run.return_value = MagicMock(stdout=self.VMSTAT_HEADER_WITH_ST_GU)
        has_st, has_gu = check_vmstat_columns()
        assert has_st is True
        assert has_gu is True

    @patch("vmstat_visualizer.checks.check.subprocess.run")
    def test_returns_true_false_when_gu_absent(self, mock_run):
        mock_run.return_value = MagicMock(stdout=self.VMSTAT_HEADER_WITHOUT_GU)
        has_st, has_gu = check_vmstat_columns()
        assert has_st is True
        assert has_gu is False

    @patch("vmstat_visualizer.checks.check.subprocess.run")
    def test_returns_false_false_on_short_output(self, mock_run):
        mock_run.return_value = MagicMock(stdout="only one line")
        has_st, has_gu = check_vmstat_columns()
        assert has_st is False
        assert has_gu is False

    @patch("vmstat_visualizer.checks.check.subprocess.run", side_effect=FileNotFoundError)
    def test_returns_false_false_on_missing_vmstat(self, mock_run):
        has_st, has_gu = check_vmstat_columns()
        assert has_st is False
        assert has_gu is False

    @patch("vmstat_visualizer.checks.check.subprocess.run",
           side_effect=subprocess.CalledProcessError(1, "vmstat", stderr="fail"))
    def test_returns_false_false_on_process_error(self, mock_run):
        has_st, has_gu = check_vmstat_columns()
        assert has_st is False
        assert has_gu is False
