
"""
Creates a file parser.
"""
import re
import datetime
import time
import vmstat_visualizer.parser.timeseries as ts
import matplotlib.pyplot as plt
from vmstat_visualizer.checks.check import check_vmstat_columns
from matplotlib.dates import DateFormatter


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
        self.figure_size = (10, 4)

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
                if ("procs" in line or "memory" in line or "cpu" in line) or ("free" in line or "inact" in line or "active" in line):
                    continue
                if not line.strip():
                    continue 
                parts = line.strip().split()
                if len(parts) < 3:
                    continue
                # Skip lines where any part is not a digit
                # if any(not part.isdigit() for part in parts):
                #     continue
                # isDataLine = True
                # for part in parts:
                #     if not part.replace('.', '', 1).replace('-', '', 1).isdigit():
                #         isDataLine = False
                #         break
                # if not isDataLine:
                #     continue
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
        tstart = self.timeseries[0].time if self.timeseries else 'N/A'
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
            t_dt = datetime.datetime.strptime(ts_entry.time, '%Y-%m-%d %H:%M:%S')
            t.append(t_dt.strftime('%M:%S'))
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
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        now_unix = int(time.mktime(now.timetuple()))

        # 1. System Load
        self.plot_metric('system_load', run_queue=run_queue,
                         blocked_processes=blocked_processes,
                         t=t, tstart=tstart,
                         output_file_prefix=output_file_prefix,
                         output_format=output_format,
                         now_unix=now_unix)
        # 2. Memory Usage
        self.plot_metric('memory', inactive_memory_kb=inactive_memory_kb,
                         active_memory_kb=active_memory_kb,
                         swapped_memory_kb=swapped_memory_kb,
                         free_memory_kb=free_memory_kb, t=t,
                         tstart=tstart, output_file_prefix=output_file_prefix,
                         output_format=output_format, now_unix=now_unix)
        # 3. CPU Usage
        self.plot_metric('cpu', user_cpu_percent=user_cpu_percent,
                         system_cpu_percent=system_cpu_percent,
                         idle_cpu_percent=idle_cpu_percent,
                         wait_cpu_percent=wait_cpu_percent,
                         steal_cpu_percent=steal_cpu_percent,
                         t=t, tstart=tstart,
                         output_file_prefix=output_file_prefix,
                         output_format=output_format, now_unix=now_unix)
        # 4. Swap
        self.plot_metric('swap', swapped_memory_kb=swapped_memory_kb,
                         swap_in_kb=swap_in_kb, swap_out_kb=swap_out_kb,
                         t=t, tstart=tstart, output_file_prefix=output_file_prefix,
                         output_format=output_format, now_unix=now_unix)
        # 5. IO
        self.plot_metric('io', blocks_in=blocks_in,
                         blocks_out=blocks_out, t=t,
                         tstart=tstart, output_file_prefix=output_file_prefix,
                         output_format=output_format, now_unix=now_unix)

    def plot_comparison(
        self, compare_parser,
        output_file_prefix='vmstat',
        output_format='png',
        metric='cpu'
    ):
        # Placeholder for comparison plotting logic
        pass

    def force_numeric(self,ax):
        import matplotlib.ticker as ticker
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=False))
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
        ax.ticklabel_format(style='plain', axis='y')
        ax.autoscale(enable=True, axis='y', tight=True)

    def plot_metric(self, metric, **kwargs):
        if metric == 'cpu':
            self._plot_cpu(
                kwargs.get('user_cpu_percent'), kwargs.get('system_cpu_percent'),
                kwargs.get('idle_cpu_percent'), kwargs.get('wait_cpu_percent'),
                kwargs.get('steal_cpu_percent'), kwargs.get('t'), kwargs.get('tstart'),
                kwargs.get('output_file_prefix'), kwargs.get('output_format'), kwargs.get('now_unix')
            )
        elif metric == 'memory':
            self._plot_memory(
                kwargs.get('inactive_memory_kb'), kwargs.get('active_memory_kb'),
                kwargs.get('swapped_memory_kb'), kwargs.get('free_memory_kb'), kwargs.get('t'),
                kwargs.get('tstart'), kwargs.get('output_file_prefix'), kwargs.get('output_format'), kwargs.get('now_unix')
            )
        elif metric == 'system_load':
            self._plot_system_load(
                kwargs.get('run_queue'), kwargs.get('blocked_processes'), kwargs.get('t'), kwargs.get('tstart'),
                kwargs.get('output_file_prefix'), kwargs.get('output_format'), kwargs.get('now_unix')
            )
        elif metric == 'swap':
            self._plot_swap(
                kwargs.get('swapped_memory_kb'), kwargs.get('swap_in_kb'), kwargs.get('swap_out_kb'), kwargs.get('t'), kwargs.get('tstart'),
                kwargs.get('output_file_prefix'), kwargs.get('output_format'), kwargs.get('now_unix')
            )
        elif metric == 'io':
            self._plot_io(
                kwargs.get('blocks_in'), kwargs.get('blocks_out'), kwargs.get('t'), kwargs.get('tstart'),
                kwargs.get('output_file_prefix'), kwargs.get('output_format'), kwargs.get('now_unix')
            )
        else:
            raise ValueError(f"Unknown metric: {metric}")

    def _plot_system_load(self, run_queue, blocked_processes, t, tstart, output_file_prefix, output_format, now_unix):
        import matplotlib.pyplot as plt
        plt.figure(figsize=self.figure_size)
        # Convert run_queue and blocked_processes to integers for plotting
        run_queue_int = [int(x) for x in run_queue]
        blocked_processes_int = [int(x) for x in blocked_processes]
        plt.plot(t, run_queue_int, label='Running Queue (r)')
        plt.plot(t, blocked_processes_int, label='Blocked Processes (b)')
        plt.title('System Load')
        plt.xlabel('Seconds')
        plt.ylabel('Processes')
        plt.legend()
        plt.tight_layout()
        ax = plt.gca()
        self.force_numeric(ax)
        plt.xticks(rotation=45)
        if t:
            plt = self._set_figtext(plt, tstart)
        # Set y-axis lower limit to 0 for better fit
        ax.set_ylim(bottom=0)
        plt.savefig(f'{output_file_prefix}_system_load_{now_unix}.{output_format}', bbox_inches='tight')
        plt.close()

    def _plot_memory(self, inactive_memory_kb,
                    active_memory_kb, swapped_memory_kb, free_memory_kb,
                    t, tstart, output_file_prefix, output_format, now_unix):
        import matplotlib.pyplot as plt
        plt.figure(figsize=self.figure_size)
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
        self.force_numeric(ax)
        plt.xticks(rotation=45)
        if t:
            plt = self._set_figtext(plt, tstart)
        # Set y-axis limit a bit higher than the max value for better display
        all_memory = inactive_memory_kb_int + active_memory_kb_int + swapped_memory_kb_int + free_memory_kb_int
        if all_memory:
            ymax = max(all_memory) * 1.05
            ax.set_ylim(top=ymax)
        ax.set_ylim(bottom=0)
        plt.savefig(f'{output_file_prefix}_memory_{now_unix}.{output_format}', bbox_inches='tight')
        plt.close()

    def _plot_cpu(self, user_cpu_percent, system_cpu_percent,
                 idle_cpu_percent, wait_cpu_percent,
                 steal_cpu_percent, t, tstart,
                 output_file_prefix, output_format, now_unix):
        import matplotlib.pyplot as plt
        plt.figure(figsize=self.figure_size)
        plt.plot(t, [int(x) for x in user_cpu_percent], label='User CPU (%)')
        plt.plot(t, [int(x) for x in system_cpu_percent], label='System CPU (%)')
        plt.plot(t, [int(x) for x in idle_cpu_percent], label='Idle CPU (%)')
        plt.plot(t, [int(x) for x in wait_cpu_percent], label='Wait CPU (%)')
        plt.plot(t, [int(x) for x in steal_cpu_percent], label='Steal CPU (%)')
        plt.title('CPU Usage (%)')
        plt.xlabel('Seconds')
        plt.ylabel('Percent')
        plt.legend()
        plt.tight_layout()
        ax = plt.gca()
        self.force_numeric(ax)
        plt.xticks(rotation=45)
        if t:
            plt = self._set_figtext(plt, tstart)
        ax.set_ylim(bottom=0)
        plt.savefig(f'{output_file_prefix}_cpu_{now_unix}.{output_format}', bbox_inches='tight')
        plt.close()

    def _plot_swap(self, swapped_memory_kb, swap_in_kb,
                  swap_out_kb, t, tstart,
                  output_file_prefix, output_format, now_unix):
        import matplotlib.pyplot as plt
        plt.figure(figsize=self.figure_size)
        plt.plot(t, [int(x) for x in swapped_memory_kb], label='Swapped Memory (KB)')
        plt.plot(t, [int(x) for x in swap_in_kb], label='Swap In (KB)')
        plt.plot(t, [int(x) for x in swap_out_kb], label='Swap Out (KB)')
        plt.title('Swap Usage')
        plt.xlabel('Seconds')
        plt.ylabel('Swap (KB)')
        plt.legend()
        plt.tight_layout()
        ax = plt.gca()
        self.force_numeric(ax)
        plt.xticks(rotation=45)
        if t:
            plt = self._set_figtext(plt, tstart)
        ax.set_ylim(bottom=0)
        plt.savefig(f'{output_file_prefix}_swap_{now_unix}.{output_format}', bbox_inches='tight')
        plt.close()

    def _plot_io(self, blocks_in, blocks_out, t, tstart, output_file_prefix, output_format, now_unix):
        import matplotlib.pyplot as plt
        plt.figure(figsize=self.figure_size)
        plt.plot(t, [int(x) for x in blocks_in], label='Blocks In')
        plt.plot(t, [int(x) for x in blocks_out], label='Blocks Out')
        plt.title('IO')
        plt.xlabel('Seconds')
        plt.ylabel('Blocks')
        plt.legend()
        plt.tight_layout()
        ax = plt.gca()
        self.force_numeric(ax)
        plt.xticks(rotation=45)
        if t:
            plt = self._set_figtext(plt, tstart)
        ax.set_ylim(bottom=0)
        plt.savefig(f'{output_file_prefix}_io_{now_unix}.{output_format}', bbox_inches='tight')
        plt.close()

    def _set_figtext(self, plt, tstart):
        plt.figtext(0.99, 0.01, f"Start time: {tstart}", horizontalalignment='right', fontsize=8, color='gray')
        plt.figtext(0.99, 0.99, f"File: {self.filename}", horizontalalignment='right', fontsize=8, color='gray')
        return plt
