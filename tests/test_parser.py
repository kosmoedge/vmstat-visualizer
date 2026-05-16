import pytest
from unittest.mock import patch
from vmstat_visualizer.parser.parser import Parser


def _mock_check_vmstat_columns():
    """Mock check_vmstat_columns to avoid running vmstat subprocess."""
    return True, True


class TestParserInit:
    def test_initial_state(self):
        p = Parser("dummy.log")
        assert p.filename == "dummy.log"
        assert p.timeseries == []
        assert p.enabled_columns == []


class TestParseExampleLog:
    """Parse the shipped example.log fixture (headerless, vmstat -a with gu)."""

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_entry_count(self, mock_check, example_log):
        p = Parser(example_log)
        p.parse()
        assert len(p.timeseries) == 30

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_first_entry_values(self, mock_check, example_log):
        p = Parser(example_log)
        p.parse()
        first = p.timeseries[0]
        assert first.run_queue == '3'
        assert first.blocked_processes == '0'
        assert first.swapped_memory_kb == '0'
        assert first.free_memory_kb == '523'
        assert first.inactive_memory_kb == '128'
        assert first.active_memory_kb == '1059'
        assert first.swap_in_kb == '0'
        assert first.swap_out_kb == '0'
        assert first.blocks_in == '4'
        assert first.blocks_out == '1'
        assert first.user_cpu_percent == '0'
        assert first.system_cpu_percent == '0'
        assert first.idle_cpu_percent == '99'
        assert first.wait_cpu_percent == '0'
        assert first.steal_cpu_percent == '0'
        assert first.guest_cpu_percent == '0'
        assert first.time == '2025-08-01 10:06:32'

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_last_entry_time(self, mock_check, example_log):
        p = Parser(example_log)
        p.parse()
        assert p.timeseries[-1].time == '2025-08-01 10:07:01'

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_timestamps_sequential(self, mock_check, example_log):
        p = Parser(example_log)
        p.parse()
        times = [e.time for e in p.timeseries]
        assert times == sorted(times)


class TestParseActiveFixture:
    """Parse the vmstat -a fixture file that has header rows."""

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_entry_count(self, mock_check, active_log):
        p = Parser(active_log)
        p.parse()
        assert len(p.timeseries) == 5

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_skips_header_and_procs_lines(self, mock_check, active_log):
        p = Parser(active_log)
        p.parse()
        for ts_entry in p.timeseries:
            assert ts_entry.time is not None
            assert ts_entry.run_queue is not None


class TestParseNoHeaderFixture:
    """Parse a file with no header row (raw data only)."""

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_entry_count(self, mock_check, no_header_log):
        p = Parser(no_header_log)
        p.parse()
        assert len(p.timeseries) == 3

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_first_entry(self, mock_check, no_header_log):
        p = Parser(no_header_log)
        p.parse()
        first = p.timeseries[0]
        assert first.run_queue == '3'
        assert first.time == '2025-08-01 10:06:32'


class TestParseEdgeCases:
    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_empty_file(self, mock_check, empty_log):
        p = Parser(empty_log)
        p.parse()
        assert len(p.timeseries) == 0

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_header_only_file(self, mock_check, header_only_log):
        p = Parser(header_only_log)
        p.parse()
        assert len(p.timeseries) == 0


class TestPlotMetrics:
    """Validate PlotMetrics correctly aggregates timeseries data."""

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_absolute_time(self, mock_check, active_log):
        p = Parser(active_log)
        p.parse()
        pm = p.PlotMetrics(p.timeseries)
        assert len(pm.t) == 5
        assert pm.t[0] == '06:32'

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_relative_time(self, mock_check, active_log):
        p = Parser(active_log)
        p.parse()
        pm = p.PlotMetrics(p.timeseries, relative_time=True)
        assert pm.t == [0, 1, 2, 3, 4]

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_metric_lists_length(self, mock_check, active_log):
        p = Parser(active_log)
        p.parse()
        pm = p.PlotMetrics(p.timeseries)
        assert len(pm.run_queue) == 5
        assert len(pm.user_cpu_percent) == 5
        assert len(pm.blocks_in) == 5
        assert len(pm.swap_in_kb) == 5
        assert len(pm.inactive_memory_kb) == 5

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_metric_values(self, mock_check, example_log):
        p = Parser(example_log)
        p.parse()
        pm = p.PlotMetrics(p.timeseries)
        assert pm.run_queue[0] == '3'
        assert pm.idle_cpu_percent[0] == '99'
