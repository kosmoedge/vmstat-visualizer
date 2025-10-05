"""
Timeseries module implements the timeseries class.
A timeseries is a sequence of data points, typically consisting of
successive measurements made over a time interval.
"""

class Timeseries:
    """
    Timeseries class for handling time series data.

    Attributes:
        data (list): A list to store the time series data points.
    Methods:
        __init__():
            Initializes the Timeseries with an empty data list.
        add_data_point(point):
            Adds a data point to the time series.
        get_data():
            Returns the list of data points in the time series.
    """
    def __init__(self):
        self.time = None
        self.run_queue = None
        self.blocked_processes = None
        self.swapped_memory_kb = None
        self.free_memory_kb = None
        self.inactive_memory_kb = None
        self.active_memory_kb = None
        self.swap_in_kb = None
        self.swap_out_kb = None
        self.blocks_in = None
        self.blocks_out = None
        self.user_cpu_percent = None
        self.system_cpu_percent = None
        self.idle_cpu_percent = None
        self.wait_cpu_percent = None
        self.steal_cpu_percent = None
        self.guest_cpu_percent = None
        self.raw_data = {}

    def __repr__(self):
        return f"Timeseries(data_points={len(self.raw_data)})"

    def add_data_point(self, point):
        """Adds a data point to the time series."""
        self.raw_data.append(point)

    def get_data(self):
        """Returns the list of data points in the time series."""
        return self.data

    def commit_raw_data(self):
        """
        Commits the raw_data points to the actual attributes of
        the Timeseries instance. Maps raw_data keys to attribute
        names and appends values to corresponding lists.
        Assumes raw_data is a list of dicts, each representing a data point.
        """
        # Mapping from raw_data keys to attribute names
        key_map = {
            'time': 'time',
            'r': 'run_queue',
            'b': 'blocked_processes',
            'swpd': 'swapped_memory_kb',
            'free': 'free_memory_kb',
            'inact': 'inactive_memory_kb',
            'active': 'active_memory_kb',
            'si': 'swap_in_kb',
            'so': 'swap_out_kb',
            'bi': 'blocks_in',
            'bo': 'blocks_out',
            'us': 'user_cpu_percent',
            'sy': 'system_cpu_percent',
            'id': 'idle_cpu_percent',
            'wa': 'wait_cpu_percent',
            'st': 'steal_cpu_percent',
            'gu': 'guest_cpu_percent'
        }
        # Initialize lists for each attribute if not already done
        for attr in key_map.values():
            if getattr(self, attr) is None:
                setattr(self, attr, [])
        # Commit raw data to attributes
        for point in self.raw_data:
            for raw_key, attr in key_map.items():
                if raw_key in point:
                    getattr(self, attr).append(point[raw_key])

    