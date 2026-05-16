import pytest
from vmstat_visualizer.parser.parser import Parser


class TestParserInit:
    def test_initial_state(self):
        p = Parser("dummy.log")
        assert p.filename == "dummy.log"
        assert p.timeseries == []
        assert p.enabled_columns == []
        assert p.detected_headers is None
        assert p.vmstat_format is None


class TestDetectHeaders:
    """_detect_headers: header lines yield column tokens; prose/data lines yield None."""

    def test_returns_active_header_tokens(self):
        line = (
            " r  b   swpd   free  inact active   si   so    bi    bo   "
            "in   cs us sy id wa st gu\n"
        )
        got = Parser._detect_headers(line)
        assert got is not None
        assert "inact" in got
        assert "active" in got
        assert "buff" not in got
        assert "cache" not in got

    def test_returns_standard_header_tokens_with_buff_cache(self):
        line = (
            " r  b   swpd   free   buff  cache   si   so    bi    bo   "
            "in   cs us sy id wa st gu\n"
        )
        got = Parser._detect_headers(line)
        assert got is not None
        assert "buff" in got
        assert "cache" in got

    def test_rejects_procs_banner_line(self):
        line = "procs -----------memory---------- ---swap-- -----io---- -system-- -------cpu-------\n"
        assert Parser._detect_headers(line) is None

    def test_rejects_data_line(self):
        line = " 3  0      0    523    128   1059    0    0     4     1   71  111  0  0 99  0  0  0 2025-08-01 10:06:32\n"
        assert Parser._detect_headers(line) is None

    def test_rejects_line_with_below_threshold_known_tokens(self):
        line = "r b swpd free\n"
        assert Parser._detect_headers(line) is None


class TestParseExampleLog:
    """Parse the shipped example.log (no header banner; defaults to vmstat -a mapping)."""

    def test_entry_count(self, example_log):
        p = Parser(example_log)
        p.parse()
        assert len(p.timeseries) == 30

    def test_first_entry_values(self, example_log):
        p = Parser(example_log)
        p.parse()
        first = p.timeseries[0]
        assert first.run_queue == "3"
        assert first.blocked_processes == "0"
        assert first.swapped_memory_kb == "0"
        assert first.free_memory_kb == "523"
        assert first.inactive_memory_kb == "128"
        assert first.active_memory_kb == "1059"
        assert first.swap_in_kb == "0"
        assert first.swap_out_kb == "0"
        assert first.blocks_in == "4"
        assert first.blocks_out == "1"
        assert first.user_cpu_percent == "0"
        assert first.system_cpu_percent == "0"
        assert first.idle_cpu_percent == "99"
        assert first.wait_cpu_percent == "0"
        assert first.steal_cpu_percent == "0"
        assert first.guest_cpu_percent == "0"
        assert first.time == "2025-08-01 10:06:32"
        assert first.buff_memory_kb is None
        assert first.cache_memory_kb is None

    def test_last_entry_time(self, example_log):
        p = Parser(example_log)
        p.parse()
        assert p.timeseries[-1].time == "2025-08-01 10:07:01"

    def test_timestamps_sequential(self, example_log):
        p = Parser(example_log)
        p.parse()
        times = [e.time for e in p.timeseries]
        assert times == sorted(times)

    def test_headerless_defaults_no_detected_banner(self, example_log):
        p = Parser(example_log)
        p.parse()
        assert p.detected_headers is None
        assert p.vmstat_format is None


class TestParseActiveFixture:
    """vmstat -a style file with banner + header row."""

    def test_detected_headers_and_format(self, active_log):
        p = Parser(active_log)
        p.parse()
        assert p.vmstat_format == "active"
        assert p.detected_headers is not None
        assert "inact" in p.detected_headers
        assert "active" in p.detected_headers

    def test_entry_count(self, active_log):
        p = Parser(active_log)
        p.parse()
        assert len(p.timeseries) == 5

    def test_skips_header_and_procs_lines(self, active_log):
        p = Parser(active_log)
        p.parse()
        for ts_entry in p.timeseries:
            assert ts_entry.time is not None
            assert ts_entry.run_queue is not None

    def test_active_memory_columns_populated_buff_cache_none(self, active_log):
        p = Parser(active_log)
        p.parse()
        first = p.timeseries[0]
        assert first.inactive_memory_kb == "128"
        assert first.active_memory_kb == "1059"
        assert first.buff_memory_kb is None
        assert first.cache_memory_kb is None


class TestParseStandardFixture:
    """Standard vmstat columns (buff/cache instead of inactive/active)."""

    def test_detected_headers_and_format(self, standard_log):
        p = Parser(standard_log)
        p.parse()
        assert p.vmstat_format == "standard"
        assert p.detected_headers is not None
        assert "buff" in p.detected_headers
        assert "cache" in p.detected_headers

    def test_entry_count(self, standard_log):
        p = Parser(standard_log)
        p.parse()
        assert len(p.timeseries) == 5

    def test_buff_cache_populated_inact_active_none(self, standard_log):
        p = Parser(standard_log)
        p.parse()
        first = p.timeseries[0]
        assert first.buff_memory_kb == "512"
        assert first.cache_memory_kb == "8192"
        assert first.inactive_memory_kb is None
        assert first.active_memory_kb is None


class TestParseNoHeaderFixture:
    """File with raw data rows only."""

    def test_entry_count(self, no_header_log):
        p = Parser(no_header_log)
        p.parse()
        assert len(p.timeseries) == 3

    def test_first_entry(self, no_header_log):
        p = Parser(no_header_log)
        p.parse()
        first = p.timeseries[0]
        assert first.run_queue == "3"
        assert first.time == "2025-08-01 10:06:32"


class TestParseEdgeCases:
    def test_empty_file(self, empty_log):
        p = Parser(empty_log)
        p.parse()
        assert len(p.timeseries) == 0

    def test_header_only_file(self, header_only_log):
        p = Parser(header_only_log)
        p.parse()
        assert len(p.timeseries) == 0


class TestPlotMetrics:
    """PlotMetrics aggregates and exposes memory-format hints."""

    def test_absolute_time(self, active_log):
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

    def test_metric_lists_length(self, active_log):
        p = Parser(active_log)
        p.parse()
        pm = p.PlotMetrics(p.timeseries)
        assert len(pm.run_queue) == 5
        assert len(pm.user_cpu_percent) == 5
        assert len(pm.blocks_in) == 5
        assert len(pm.swap_in_kb) == 5
        assert len(pm.inactive_memory_kb) == 5
        assert len(pm.buff_memory_kb) == 5
        assert len(pm.cache_memory_kb) == 5

    def test_metric_values(self, example_log):
        p = Parser(example_log)
        p.parse()
        pm = p.PlotMetrics(p.timeseries)
        assert pm.run_queue[0] == "3"
        assert pm.idle_cpu_percent[0] == "99"

    def test_has_active_memory_true_for_vmstat_active_fixture(self, active_log):
        p = Parser(active_log)
        p.parse()
        pm = p.PlotMetrics(p.timeseries)
        assert pm.has_active_memory is True
        assert pm.has_standard_memory is False

    def test_has_standard_memory_true_for_standard_fixture(self, standard_log):
        p = Parser(standard_log)
        p.parse()
        pm = p.PlotMetrics(p.timeseries)
        assert pm.has_standard_memory is True
        assert pm.has_active_memory is False

    def test_headerless_guest_log_uses_active_style_memory_columns(self, example_log):
        p = Parser(example_log)
        p.parse()
        pm = p.PlotMetrics(p.timeseries)
        assert pm.has_active_memory is True
        assert pm.has_standard_memory is False


class TestParseExampleStandardLog:
    """examples/example_standard.log: banner + buff/cache headers."""

    def test_standard_format_and_buff_cache(self, example_standard_log):
        p = Parser(example_standard_log)
        p.parse()
        assert p.vmstat_format == "standard"
        first = p.timeseries[0]
        assert first.buff_memory_kb == "64"
        assert first.cache_memory_kb == "995"
        assert first.inactive_memory_kb is None
        assert first.active_memory_kb is None

