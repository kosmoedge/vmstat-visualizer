"""
Creates a file parser.
"""

import vmstat_visualizer.parser.timeseries as ts
import matplotlib.pyplot as plt


class Parser:
    """
    Parser class for reading and processing data from a specified file.

    Attributes:
        filename (str): The path to the file to be parsed.

    Methods:
        __init__(filename):
            Initializes the Parser with the given filename.

        parse():
            Reads the file specified by filename, processes its contents
            line by line, and prints each line. Intended to be extended
            with actual parsing logic.
    """
    def __init__(self, filename):
        self.filename = filename
        self.timeseries = []

    def parse(self):
        with open(self.filename, 'r') as file:
            data = file.readlines()
            for line in data:
                timeseries_entry = ts.TimeSeries()
                timeseries_entry.add_data_point(line.strip())
                timeseries_entry.commit_raw_data()
                self.timeseries.append(timeseries_entry)

def plot(self, output_file_prefix='vmstat', output_format='png'):
    t = []
    run_queue = []
    blocked_processes = []
    free_memory_kb = []
    inactive_memory_kb = []
    active_memory_kb = []
    swapped_memory_kb = []
    user_cpu_percent = []
    system_cpu_percent = []
    idle_cpu_percent = []
    wait_cpu_percent = []
    steal_cpu_percent = []
    guest_cpu_percent = []
    swap_in_kb = []
    swap_out_kb = []
    blocks_in = []
    blocks_out = []

    for ts_entry in self.timeseries:
        t.append(ts_entry.time)
        run_queue.append(ts_entry.run_queue)
        blocked_processes.append(ts_entry.blocked_processes)
        free_memory_kb.append(ts_entry.free_memory_kb)
        inactive_memory_kb.append(ts_entry.inactive_memory_kb)
        active_memory_kb.append(ts_entry.active_memory_kb)
        swapped_memory_kb.append(ts_entry.swapped_memory_kb)
        user_cpu_percent.append(ts_entry.user_cpu_percent)
        system_cpu_percent.append(ts_entry.system_cpu_percent)
        idle_cpu_percent.append(ts_entry.idle_cpu_percent)
        wait_cpu_percent.append(ts_entry.wait_cpu_percent)
        steal_cpu_percent.append(ts_entry.steal_cpu_percent)
        guest_cpu_percent.append(ts_entry.guest_cpu_percent)
        swap_in_kb.append(ts_entry.swap_in_kb)
        swap_out_kb.append(ts_entry.swap_out_kb)
        blocks_in.append(ts_entry.blocks_in)
        blocks_out.append(ts_entry.blocks_out)

    # 1. System Load
    plt.figure(figsize=(10, 4))
    plt.plot(t, run_queue, label='Running Queue (r)')
    plt.plot(t, blocked_processes, label='Blocked Processes (b)')
    plt.title('System Load')
    plt.xlabel('Seconds')
    plt.ylabel('Processes')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_file_prefix}_system_load.{output_format}')
    plt.close()

    # 2. Memory Usage
    plt.figure(figsize=(10, 4))
    plt.plot(t, free_memory_kb, label='Free Memory (KB)')
    plt.plot(t, inactive_memory_kb, label='Inactive Memory (KB)')
    plt.plot(t, active_memory_kb, label='Active Memory (KB)')
    plt.plot(t, swapped_memory_kb, label='Swapped Memory (KB)')
    plt.title('Memory Usage')
    plt.xlabel('Seconds')
    plt.ylabel('Memory (KB)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_file_prefix}_memory.{output_format}')
    plt.close()

    # 3. CPU Usage
    plt.figure(figsize=(10, 4))
    plt.plot(t, user_cpu_percent, label='User CPU (%)')
    plt.plot(t, system_cpu_percent, label='System CPU (%)')
    plt.plot(t, idle_cpu_percent, label='Idle CPU (%)')
    plt.plot(t, wait_cpu_percent, label='Wait CPU (%)')
    plt.plot(t, steal_cpu_percent, label='Steal CPU (%)')
    plt.title('CPU Usage (%)')
    plt.xlabel('Seconds')
    plt.ylabel('Percent')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_file_prefix}_cpu.{output_format}')
    plt.close()

    # 4. Swap
    plt.figure(figsize=(10, 4))
    plt.plot(t, swapped_memory_kb, label='Swapped Memory (KB)')
    plt.plot(t, swap_in_kb, label='Swap In (KB)')
    plt.plot(t, swap_out_kb, label='Swap Out (KB)')
    plt.title('Swap Usage')
    plt.xlabel('Seconds')
    plt.ylabel('Swap (KB)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_file_prefix}_swap.{output_format}')
    plt.close()

    # 5. IO
    plt.figure(figsize=(10, 4))
    plt.plot(t, blocks_in, label='Blocks In')
    plt.plot(t, blocks_out, label='Blocks Out')
    plt.title('IO')
    plt.xlabel('Seconds')
    plt.ylabel('Blocks')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_file_prefix}_io.{output_format}')
    plt.close()

