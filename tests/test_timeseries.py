import pytest
from vmstat_visualizer.parser.timeseries import Timeseries, COLUMN_TO_ATTR
from vmstat_visualizer.parser.parser import KNOWN_VMSTAT_COLUMNS


class TestColumnToAttrMapping:
    def test_key_count_matches_all_metric_columns_and_time(self):
        assert len(COLUMN_TO_ATTR) == 21

    def test_includes_buff_and_cache(self):
        assert COLUMN_TO_ATTR["buff"] == "buff_memory_kb"
        assert COLUMN_TO_ATTR["cache"] == "cache_memory_kb"

    def test_covers_known_vmstat_column_names_plus_time(self):
        for name in KNOWN_VMSTAT_COLUMNS:
            assert name in COLUMN_TO_ATTR
        assert COLUMN_TO_ATTR.get("time") == "time"

    def test_values_are_unique_attribute_names(self):
        attrs = list(COLUMN_TO_ATTR.values())
        assert len(attrs) == len(set(attrs))


class TestTimeseriesInit:
    """All metric attributes start as None; raw_data starts as empty dict."""

    METRIC_ATTRS = [
        "time",
        "run_queue",
        "blocked_processes",
        "swapped_memory_kb",
        "free_memory_kb",
        "inactive_memory_kb",
        "active_memory_kb",
        "buff_memory_kb",
        "cache_memory_kb",
        "swap_in_kb",
        "swap_out_kb",
        "blocks_in",
        "blocks_out",
        "interrupts",
        "context_switches",
        "user_cpu_percent",
        "system_cpu_percent",
        "idle_cpu_percent",
        "wait_cpu_percent",
        "steal_cpu_percent",
        "guest_cpu_percent",
    ]

    def test_all_metric_attributes_none(self):
        ts = Timeseries()
        for attr in self.METRIC_ATTRS:
            assert getattr(ts, attr) is None, f"{attr} should be None"

    def test_raw_data_starts_empty(self):
        ts = Timeseries()
        assert ts.raw_data == {}


class TestAddDataPoint:
    def test_stores_list(self):
        ts = Timeseries()
        data = [
            "3",
            "0",
            "0",
            "523",
            "128",
            "1059",
            "0",
            "0",
            "4",
            "1",
            "71",
            "111",
            "0",
            "0",
            "99",
            "0",
            "0",
            "0",
            "2025-08-01 10:06:32",
        ]
        ts.add_data_point(data)
        assert ts.raw_data == data

    def test_replaces_previous_data(self):
        ts = Timeseries()
        ts.add_data_point(["a", "b"])
        ts.add_data_point(["c", "d"])
        assert ts.raw_data == ["c", "d"]


class TestCommitRawData:
    """commit_raw_data maps positional values using default vmstat -a order or explicit headers."""

    def _make_ts(self, data, headers=None):
        ts = Timeseries()
        ts.add_data_point(data)
        ts.commit_raw_data(headers=headers)
        return ts

    def test_maps_default_headers_vmstat_guest_order(self):
        data = [
            "3",
            "0",
            "0",
            "523",
            "128",
            "1059",
            "0",
            "0",
            "4",
            "1",
            "71",
            "111",
            "0",
            "0",
            "99",
            "0",
            "0",
            "0",
            "2025-08-01 10:06:32",
        ]
        ts = self._make_ts(data)
        assert ts.run_queue == "3"
        assert ts.blocked_processes == "0"
        assert ts.swapped_memory_kb == "0"
        assert ts.free_memory_kb == "523"
        assert ts.inactive_memory_kb == "128"
        assert ts.active_memory_kb == "1059"
        assert ts.swap_in_kb == "0"
        assert ts.swap_out_kb == "0"
        assert ts.blocks_in == "4"
        assert ts.blocks_out == "1"
        assert ts.interrupts == "71"
        assert ts.context_switches == "111"
        assert ts.user_cpu_percent == "0"
        assert ts.system_cpu_percent == "0"
        assert ts.idle_cpu_percent == "99"
        assert ts.wait_cpu_percent == "0"
        assert ts.steal_cpu_percent == "0"
        assert ts.guest_cpu_percent == "0"
        assert ts.time == "2025-08-01 10:06:32"
        assert ts.buff_memory_kb is None
        assert ts.cache_memory_kb is None

    def test_explicit_standard_headers_map_buff_cache(self):
        headers = [
            "r",
            "b",
            "swpd",
            "free",
            "buff",
            "cache",
            "si",
            "so",
            "bi",
            "bo",
            "in",
            "cs",
            "us",
            "sy",
            "id",
            "wa",
            "st",
            "gu",
            "time",
        ]
        data = [
            "2",
            "0",
            "0",
            "15234",
            "512",
            "8192",
            "0",
            "0",
            "12",
            "8",
            "200",
            "450",
            "5",
            "2",
            "92",
            "1",
            "0",
            "0",
            "2025-09-15 14:00:01",
        ]
        ts = self._make_ts(data, headers=headers)
        assert ts.buff_memory_kb == "512"
        assert ts.cache_memory_kb == "8192"
        assert ts.inactive_memory_kb is None
        assert ts.active_memory_kb is None

    def test_cpu_values_vmstat_guest_order(self):
        data = [
            "1",
            "0",
            "0",
            "500",
            "100",
            "2000",
            "0",
            "0",
            "10",
            "5",
            "200",
            "300",
            "15",
            "2",
            "84",
            "0",
            "0",
            "0",
            "2025-08-01 10:06:58",
        ]
        ts = self._make_ts(data)
        assert ts.user_cpu_percent == "15"
        assert ts.system_cpu_percent == "2"
        assert ts.idle_cpu_percent == "84"


class TestRepr:
    def test_repr_contains_key_fields(self):
        ts = Timeseries()
        r = repr(ts)
        assert "Timeseries(" in r
        assert "run_queue=None" in r
        assert "time=None" in r
        assert "raw_data={}" in r

    def test_repr_after_commit(self):
        ts = Timeseries()
        ts.add_data_point(
            [
                "3",
                "0",
                "0",
                "523",
                "128",
                "1059",
                "0",
                "0",
                "4",
                "1",
                "71",
                "111",
                "0",
                "0",
                "99",
                "0",
                "0",
                "0",
                "2025-08-01 10:06:32",
            ]
        )
        ts.commit_raw_data()
        r = repr(ts)
        assert "run_queue=3" in r
        assert "time=2025-08-01 10:06:32" in r
