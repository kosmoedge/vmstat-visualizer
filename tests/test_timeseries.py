import pytest
from vmstat_visualizer.parser.timeseries import Timeseries


class TestTimeseriesInit:
    """All metric attributes start as None; raw_data starts as empty dict."""

    METRIC_ATTRS = [
        'time', 'run_queue', 'blocked_processes',
        'swapped_memory_kb', 'free_memory_kb',
        'inactive_memory_kb', 'active_memory_kb',
        'swap_in_kb', 'swap_out_kb',
        'blocks_in', 'blocks_out',
        'interrupts', 'context_switches',
        'user_cpu_percent', 'system_cpu_percent',
        'idle_cpu_percent', 'wait_cpu_percent',
        'steal_cpu_percent', 'guest_cpu_percent',
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
        data = ['3', '0', '0', '523', '128', '1059', '0', '0',
                '4', '1', '71', '111', '0', '0', '99', '0', '0', '0',
                '2025-08-01 10:06:32']
        ts.add_data_point(data)
        assert ts.raw_data == data

    def test_replaces_previous_data(self):
        ts = Timeseries()
        ts.add_data_point(['a', 'b'])
        ts.add_data_point(['c', 'd'])
        assert ts.raw_data == ['c', 'd']


class TestCommitRawData:
    """commit_raw_data maps positional values from raw_data to named attributes
    using the hardcoded vmstat -a header order:
    r b swpd free inact active si so bi bo in cs us sy id wa st gu time
    """

    def _make_ts(self, data):
        ts = Timeseries()
        ts.add_data_point(data)
        ts.commit_raw_data()
        return ts

    def test_maps_all_19_columns(self):
        data = ['3', '0', '0', '523', '128', '1059', '0', '0',
                '4', '1', '71', '111', '0', '0', '99', '0', '0', '0',
                '2025-08-01 10:06:32']
        ts = self._make_ts(data)
        assert ts.run_queue == '3'
        assert ts.blocked_processes == '0'
        assert ts.swapped_memory_kb == '0'
        assert ts.free_memory_kb == '523'
        assert ts.inactive_memory_kb == '128'
        assert ts.active_memory_kb == '1059'
        assert ts.swap_in_kb == '0'
        assert ts.swap_out_kb == '0'
        assert ts.blocks_in == '4'
        assert ts.blocks_out == '1'
        assert ts.interrupts == '71'
        assert ts.context_switches == '111'
        assert ts.user_cpu_percent == '0'
        assert ts.system_cpu_percent == '0'
        assert ts.idle_cpu_percent == '99'
        assert ts.wait_cpu_percent == '0'
        assert ts.steal_cpu_percent == '0'
        assert ts.guest_cpu_percent == '0'
        assert ts.time == '2025-08-01 10:06:32'

    def test_cpu_values(self):
        data = ['1', '0', '0', '500', '100', '2000', '0', '0',
                '10', '5', '200', '300', '15', '2', '84', '0', '0', '0',
                '2025-08-01 10:06:58']
        ts = self._make_ts(data)
        assert ts.user_cpu_percent == '15'
        assert ts.system_cpu_percent == '2'
        assert ts.idle_cpu_percent == '84'


class TestRepr:
    def test_repr_contains_key_fields(self):
        ts = Timeseries()
        r = repr(ts)
        assert 'Timeseries(' in r
        assert 'run_queue=None' in r
        assert 'time=None' in r
        assert 'raw_data={}' in r

    def test_repr_after_commit(self):
        ts = Timeseries()
        ts.add_data_point(['3', '0', '0', '523', '128', '1059', '0', '0',
                           '4', '1', '71', '111', '0', '0', '99', '0', '0', '0',
                           '2025-08-01 10:06:32'])
        ts.commit_raw_data()
        r = repr(ts)
        assert "run_queue=3" in r
        assert "time=2025-08-01 10:06:32" in r
