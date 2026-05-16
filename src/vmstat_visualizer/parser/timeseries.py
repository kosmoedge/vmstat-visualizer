"""
Timeseries module implements the timeseries class.
A timeseries is a sequence of data points, typically consisting of
successive measurements made over a time interval.
"""


COLUMN_TO_ATTR = {
    'r': 'run_queue',
    'b': 'blocked_processes',
    'swpd': 'swapped_memory_kb',
    'free': 'free_memory_kb',
    'inact': 'inactive_memory_kb',
    'active': 'active_memory_kb',
    'buff': 'buff_memory_kb',
    'cache': 'cache_memory_kb',
    'si': 'swap_in_kb',
    'so': 'swap_out_kb',
    'bi': 'blocks_in',
    'bo': 'blocks_out',
    'in': 'interrupts',
    'cs': 'context_switches',
    'us': 'user_cpu_percent',
    'sy': 'system_cpu_percent',
    'id': 'idle_cpu_percent',
    'wa': 'wait_cpu_percent',
    'st': 'steal_cpu_percent',
    'gu': 'guest_cpu_percent',
    'time': 'time',
}


class Timeseries:
    """Single vmstat sample with named attributes for each metric column."""

    def __init__(self):
        self.time = None
        self.run_queue = None
        self.blocked_processes = None
        self.swapped_memory_kb = None
        self.free_memory_kb = None
        self.inactive_memory_kb = None
        self.active_memory_kb = None
        self.buff_memory_kb = None
        self.cache_memory_kb = None
        self.swap_in_kb = None
        self.swap_out_kb = None
        self.blocks_in = None
        self.blocks_out = None
        self.interrupts = None
        self.context_switches = None
        self.user_cpu_percent = None
        self.system_cpu_percent = None
        self.idle_cpu_percent = None
        self.wait_cpu_percent = None
        self.steal_cpu_percent = None
        self.guest_cpu_percent = None
        self.raw_data = {}

    def __repr__(self):
        return (
            f"Timeseries("
            f"time={self.time}, "
            f"run_queue={self.run_queue}, "
            f"blocked_processes={self.blocked_processes}, "
            f"swapped_memory_kb={self.swapped_memory_kb}, "
            f"free_memory_kb={self.free_memory_kb}, "
            f"inactive_memory_kb={self.inactive_memory_kb}, "
            f"active_memory_kb={self.active_memory_kb}, "
            f"buff_memory_kb={self.buff_memory_kb}, "
            f"cache_memory_kb={self.cache_memory_kb}, "
            f"swap_in_kb={self.swap_in_kb}, "
            f"swap_out_kb={self.swap_out_kb}, "
            f"blocks_in={self.blocks_in}, "
            f"blocks_out={self.blocks_out}, "
            f"user_cpu_percent={self.user_cpu_percent}, "
            f"system_cpu_percent={self.system_cpu_percent}, "
            f"idle_cpu_percent={self.idle_cpu_percent}, "
            f"wait_cpu_percent={self.wait_cpu_percent}, "
            f"steal_cpu_percent={self.steal_cpu_percent}, "
            f"guest_cpu_percent={self.guest_cpu_percent}, "
            f"raw_data={self.raw_data}"
            f")"
        )

    def add_data_point(self, point):
        """Adds a data point to the time series."""
        self.raw_data = point

    def get_data(self):
        """Returns the list of data points in the time series."""
        return self.raw_data

    def commit_raw_data(self, headers=None):
        """Map raw_data values to named attributes using the provided header list."""
        if headers is None:
            headers = [
                'r', 'b', 'swpd', 'free', 'inact', 'active', 'si', 'so',
                'bi', 'bo', 'in', 'cs', 'us', 'sy', 'id', 'wa', 'st', 'gu', 'time',
            ]
        for idx, value in enumerate(self.raw_data):
            if idx >= len(headers):
                break
            col = headers[idx]
            attr = COLUMN_TO_ATTR.get(col)
            if attr:
                setattr(self, attr, value)
