"""Tests for the vmstat parser."""

import pytest
from vmstat_visualizer.parser.parser import Parser


class TestParserActiveFormat:
    """Tests for vmstat -a output (inact/active columns) with header lines."""

    def test_parse_entry_count(self, active_log):
        p = Parser(active_log)
        p.parse()
        assert len(p.timeseries) == 5

    def test_first_entry_time(self, active_log):
        p = Parser(active_log)
        p.parse()
        assert p.timeseries[0].time == "2025-08-01 10:06:32"

    def test_first_entry_cpu(self, active_log):
        p = Parser(active_log)
        p.parse()
        entry = p.timeseries[0]
        assert entry.user_cpu_percent == "0"
        assert entry.system_cpu_percent == "0"
        assert entry.idle_cpu_percent == "99"

    def test_first_entry_memory(self, active_log):
        p = Parser(active_log)
        p.parse()
        entry = p.timeseries[0]
        assert entry.free_memory_kb == "523"

    def test_last_entry_time(self, active_log):
        p = Parser(active_log)
        p.parse()
        assert p.timeseries[-1].time == "2025-08-01 10:06:36"


class TestParserNoHeader:
    """Tests for log files without header lines (legacy format)."""

    def test_parse_entry_count(self, no_header_log):
        p = Parser(no_header_log)
        p.parse()
        assert len(p.timeseries) == 3

    def test_first_entry_values(self, no_header_log):
        p = Parser(no_header_log)
        p.parse()
        entry = p.timeseries[0]
        assert entry.time == "2025-08-01 10:06:32"
        assert entry.run_queue == "3"
        assert entry.free_memory_kb == "523"

    def test_empty_lines_skipped(self, tmp_path):
        log = tmp_path / "empty.log"
        log.write_text("\n\n\n")
        p = Parser(str(log))
        p.parse()
        assert len(p.timeseries) == 0

    def test_header_only_file(self, tmp_path):
        log = tmp_path / "header_only.log"
        log.write_text(
            "procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----\n"
            " r  b   swpd   free  inact active   si   so    bi    bo   in   cs us sy id wa st\n"
        )
        p = Parser(str(log))
        p.parse()
        assert len(p.timeseries) == 0


class TestPlotMetrics:
    """Tests for the PlotMetrics inner class."""

    def test_time_format(self, active_log):
        p = Parser(active_log)
        p.parse()
        pm = p.PlotMetrics(p.timeseries)
        assert len(pm.t) == 5
        assert pm.t[0] == "06:32"

    def test_relative_time(self, active_log):
        p = Parser(active_log)
        p.parse()
        pm = p.PlotMetrics(p.timeseries, relative_time=True)
        assert pm.t == [0, 1, 2, 3, 4]

    def test_cpu_extraction(self, active_log):
        p = Parser(active_log)
        p.parse()
        pm = p.PlotMetrics(p.timeseries)
        assert pm.user_cpu_percent[0] == "0"
        assert pm.idle_cpu_percent[0] == "99"
        assert len(pm.user_cpu_percent) == 5

    def test_memory_extraction(self, active_log):
        p = Parser(active_log)
        p.parse()
        pm = p.PlotMetrics(p.timeseries)
        assert pm.free_memory_kb[0] == "523"
        assert len(pm.free_memory_kb) == 5

    def test_io_extraction(self, active_log):
        p = Parser(active_log)
        p.parse()
        pm = p.PlotMetrics(p.timeseries)
        assert pm.blocks_in[0] == "4"
        assert pm.blocks_out[0] == "1"
