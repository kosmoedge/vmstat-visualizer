"""Tests for the Timeseries data model."""

from vmstat_visualizer.parser.timeseries import Timeseries


class TestTimeseriesCommit:
    """Test commit_raw_data with the default (vmstat -a) header list."""

    def test_commit_default_headers(self):
        ts = Timeseries()
        data = ["1", "0", "0", "256", "128", "2048",
                "0", "0", "0", "0", "50", "100",
                "10", "2", "88", "0", "0", "0", "2025-01-01 12:00:01"]
        ts.add_data_point(data)
        ts.commit_raw_data()

        assert ts.run_queue == "1"
        assert ts.free_memory_kb == "256"
        assert ts.inactive_memory_kb == "128"
        assert ts.active_memory_kb == "2048"
        assert ts.user_cpu_percent == "10"
        assert ts.idle_cpu_percent == "88"
        assert ts.time == "2025-01-01 12:00:01"

    def test_add_data_point_stores_raw(self):
        ts = Timeseries()
        data = ["a", "b", "c"]
        ts.add_data_point(data)
        assert ts.raw_data == data

    def test_repr_contains_key_fields(self):
        ts = Timeseries()
        ts.time = "2025-01-01 12:00:00"
        ts.run_queue = "3"
        r = repr(ts)
        assert "time=2025-01-01 12:00:00" in r
        assert "run_queue=3" in r

    def test_initial_values_are_none(self):
        ts = Timeseries()
        assert ts.time is None
        assert ts.run_queue is None
        assert ts.user_cpu_percent is None
        assert ts.free_memory_kb is None
