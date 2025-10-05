
"""
Creates a file parser.
"""
import re
import datetime
import time
import vmstat_visualizer.parser.timeseries as ts
import matplotlib.pyplot as plt
from vmstat_visualizer.checks.check import check_vmstat_columns


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
        has_st, has_gu = check_vmstat_columns()
        if has_st and has_gu:
            print("System supports 'st' and 'gu' columns.")
        else:
            print(f"Missing columns: st={not has_st}, gu={not has_gu}")
        with open(self.filename, 'r') as file:
            data = file.readlines()
            for line in data:
                timeseries_entry = ts.Timeseries()
                # Regex to match a timestamp like '2025-07-31 23:52:52'
                time_regex = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')

                parts = line.strip().split()
                if len(parts) < 3:
                    continue 
                data_points = []
                if len(parts) >= 2 and time_regex.match(" ".join(parts[-2:])):
                    time_column = " ".join(parts[-2:])
                    data_points = [item.strip() for item in parts[:-2]] + [time_column]
                else:
                    time_column = " ".join(parts[:2])
                    data_points = [time_column] + [item.strip() for item in parts[2:]]
                timeseries_entry.add_data_point(data_points)
                timeseries_entry.commit_raw_data()
                self.timeseries.append(timeseries_entry)

    def plot(self, output_file_prefix='vmstat', output_format='png'):
        import matplotlib.ticker as ticker
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
        print(inactive_memory_kb, active_memory_kb, free_memory_kb)
        def force_numeric(ax):
            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=False))
            ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
            ax.ticklabel_format(style='plain', axis='y')
            ax.autoscale(enable=True, axis='y', tight=True)
        # 1. System Load
        plt.figure(figsize=(10, 4))
        plt.plot(t, run_queue, label='Running Queue (r)')
        plt.plot(t, blocked_processes, label='Blocked Processes (b)')
        plt.title('System Load')
        plt.xlabel('Seconds')
        plt.ylabel('Processes')
        plt.legend()
        plt.tight_layout()
        ax = plt.gca()
        force_numeric(ax)
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        now_unix = int(time.mktime(now.timetuple()))
        plt.savefig(f'{output_file_prefix}_system_load_{now_unix}.{output_format}')
        plt.close()
        # 2. Memory Usage
        plt.figure(figsize=(10, 4))
        # Convert memory values to integers for plotting
        inactive_memory_kb_int = [int(x) for x in inactive_memory_kb]
        active_memory_kb_int = [int(x) for x in active_memory_kb]
        swapped_memory_kb_int = [int(x) for x in swapped_memory_kb]
        free_memory_kb_int = [int(x) for x in free_memory_kb]

        plt.plot(t, inactive_memory_kb_int, label='Inactive Memory (KB)')
        plt.plot(t, active_memory_kb_int, label='Active Memory (KB)')
        plt.plot(t, swapped_memory_kb_int, label='Swapped Memory (KB)')
        plt.plot(t, free_memory_kb_int, label='Free Memory (KB)')
        plt.title('Memory Usage')
        plt.xlabel('Seconds')
        plt.ylabel('Memory (KB)')
        plt.legend()
        plt.tight_layout()
        ax = plt.gca()
        force_numeric(ax)
        # Set y-axis limit a bit higher than the max value for better display
        all_memory = inactive_memory_kb_int + active_memory_kb_int + swapped_memory_kb_int + free_memory_kb_int
        if all_memory:
            ymax = max(all_memory) * 1.05
            ax.set_ylim(top=ymax)
        plt.savefig(f'{output_file_prefix}_memory_{now_unix}.{output_format}')
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
        ax = plt.gca()
        force_numeric(ax)
        plt.savefig(f'{output_file_prefix}_cpu_{now_unix}.{output_format}')
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
        ax = plt.gca()
        force_numeric(ax)
        plt.savefig(f'{output_file_prefix}_swap_{now_unix}.{output_format}')
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
        ax = plt.gca()
        force_numeric(ax)
        plt.savefig(f'{output_file_prefix}_io.{output_format}')
        plt.close()
