
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
        plot_metrics = self.PlotMetrics(self.timeseries)
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        now_unix = int(time.mktime(now.timetuple()))

        # 1. System Load
        self.plot_metric('system_load', run_queue=plot_metrics.run_queue,
                         blocked_processes=plot_metrics.blocked_processes,
                         t=plot_metrics.t, tstart=tstart,
                         output_file_prefix=output_file_prefix,
                         output_format=output_format,
                         now_unix=now_unix)
        # 2. Memory Usage
        self.plot_metric('memory', inactive_memory_kb=plot_metrics.inactive_memory_kb,
                         active_memory_kb=plot_metrics.active_memory_kb,
                         swapped_memory_kb=plot_metrics.swapped_memory_kb,
                         free_memory_kb=plot_metrics.free_memory_kb, t=plot_metrics.t,
                         tstart=tstart, output_file_prefix=output_file_prefix,
                         output_format=output_format, now_unix=now_unix)
        # 3. CPU Usage
        self.plot_metric('cpu', user_cpu_percent=plot_metrics.user_cpu_percent,
                         system_cpu_percent=plot_metrics.system_cpu_percent,
                         idle_cpu_percent=plot_metrics.idle_cpu_percent,
                         wait_cpu_percent=plot_metrics.wait_cpu_percent,
                         steal_cpu_percent=plot_metrics.steal_cpu_percent,
                         t=plot_metrics.t, tstart=tstart,
                         output_file_prefix=output_file_prefix,
                         output_format=output_format, now_unix=now_unix)
        # 4. Swap
        self.plot_metric('swap', swapped_memory_kb=plot_metrics.swapped_memory_kb,
                         swap_in_kb=plot_metrics.swap_in_kb, swap_out_kb=plot_metrics.swap_out_kb,
                         t=plot_metrics.t, tstart=tstart, output_file_prefix=output_file_prefix,
                         output_format=output_format, now_unix=now_unix)
        # 5. IO
        self.plot_metric('io', blocks_in=plot_metrics.blocks_in,
                         blocks_out=plot_metrics.blocks_out, t=plot_metrics.t,
                         tstart=tstart, output_file_prefix=output_file_prefix,
                         output_format=output_format, now_unix=now_unix)

    def plot_comparison(
        self, compare_parser,
        output_file_prefix='vmstat',
        output_format='png',
        metric='cpu',
        column=[]
    ):
        import datetime
        import time
        import os
        plot_metrics = self.PlotMetrics(self.timeseries, relative_time=True)
        compare_plot_metrics = self.PlotMetrics(compare_parser.timeseries, relative_time=True)
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        now_unix = int(time.mktime(now.timetuple()))
        tstart1 = self.timeseries[0].time if self.timeseries else 'N/A'
        tstart2 = compare_parser.timeseries[0].time if compare_parser.timeseries else 'N/A'
        # Get filenames without parent directories
        file1_name = os.path.basename(self.filename)
        file2_name = os.path.basename(compare_parser.filename)
        # Align time axes - use the longer time series
        max_len = max(len(plot_metrics.t), len(compare_plot_metrics.t))
        t_aligned = list(range(max_len))
        if metric == 'cpu':
            self._plot_cpu(
                [plot_metrics.user_cpu_percent,
                    compare_plot_metrics.user_cpu_percent]
                if "us" in column or column is None else [],
                [plot_metrics.system_cpu_percent,
                    compare_plot_metrics.system_cpu_percent]
                if "sy" in column or len(column) == 0 else [],
                [plot_metrics.idle_cpu_percent,
                    compare_plot_metrics.idle_cpu_percent]
                if "id" in column or len(column) == 0 else [],
                [plot_metrics.wait_cpu_percent,
                    compare_plot_metrics.wait_cpu_percent]
                if "wa" in column or len(column) == 0 else [],
                [plot_metrics.steal_cpu_percent,
                    compare_plot_metrics.steal_cpu_percent]
                if "st" in column or len(column) == 0 else [],
                t_aligned, [tstart1, tstart2],
                output_file_prefix, output_format, now_unix,
                comparison=True, filenames=[file1_name, file2_name]
            )
        elif metric == 'memory':
            self._plot_memory(
                [plot_metrics.inactive_memory_kb,
                    compare_plot_metrics.inactive_memory_kb]
                if "inact" in column or len(column) == 0 else [],
                [plot_metrics.active_memory_kb,
                    compare_plot_metrics.active_memory_kb]
                if "active" in column or len(column) == 0 else [],
                [plot_metrics.swapped_memory_kb,
                    compare_plot_metrics.swapped_memory_kb]
                if "swpd" in column or len(column) == 0 else [],
                [plot_metrics.free_memory_kb,
                    compare_plot_metrics.free_memory_kb]
                if "free" in column or len(column) == 0 else [],
                t_aligned, [tstart1, tstart2],
                output_file_prefix, output_format, now_unix,
                comparison=True, filenames=[file1_name, file2_name]
            )
        elif metric == 'system_load':
            self._plot_system_load(
                [plot_metrics.run_queue, compare_plot_metrics.run_queue],
                [plot_metrics.blocked_processes, compare_plot_metrics.blocked_processes],
                t_aligned, [tstart1, tstart2], output_file_prefix, output_format, now_unix, 
                comparison=True, filenames=[file1_name, file2_name]
            )
        elif metric == 'swap':
            self._plot_swap(
                [plot_metrics.swapped_memory_kb, compare_plot_metrics.swapped_memory_kb],
                [plot_metrics.swap_in_kb, compare_plot_metrics.swap_in_kb],
                [plot_metrics.swap_out_kb, compare_plot_metrics.swap_out_kb],
                t_aligned, [tstart1, tstart2], output_file_prefix, output_format, now_unix, 
                comparison=True, filenames=[file1_name, file2_name]
            )
        elif metric == 'io':
            self._plot_io(
                [plot_metrics.blocks_in, compare_plot_metrics.blocks_in],
                [plot_metrics.blocks_out, compare_plot_metrics.blocks_out],
                t_aligned, [tstart1, tstart2], output_file_prefix, output_format, now_unix, 
                comparison=True, filenames=[file1_name, file2_name]
            )
        elif metric == 'all':
            # Plot all metrics for comparison
            for m in ['system_load', 'memory', 'cpu', 'swap', 'io']:
                self.plot_comparison(compare_parser, output_file_prefix, output_format, metric=m)
        else:
            raise ValueError(f"Unknown metric: {metric}. Choose from: cpu, memory, system_load, swap, io, all")

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

    def _plot_system_load(self, run_queue, blocked_processes, t, tstart, output_file_prefix, output_format, now_unix, comparison=False, filenames=None):
        import matplotlib.pyplot as plt
        plt.figure(figsize=self.figure_size)
        # Convert run_queue and blocked_processes to integers for plotting
        if not comparison:
            run_queue_int = [int(x) for x in run_queue]
            blocked_processes_int = [int(x) for x in blocked_processes]
            plt.plot(t, run_queue_int, label='Running Queue (r)')
            plt.plot(t, blocked_processes_int, label='Blocked Processes (b)')
            plt.title('System Load')
            plt.xlabel('Seconds')
        else:
            run_queue_int0 = [int(x) for x in run_queue[0]]
            blocked_processes_int0 = [int(x) for x in blocked_processes[0]]
            run_queue_int1 = [int(x) for x in run_queue[1]]
            blocked_processes_int1 = [int(x) for x in blocked_processes[1]]
            # Get filenames for labels
            file1_label = filenames[0] if filenames else 'File 1'
            file2_label = filenames[1] if filenames else 'File 2'
            if len(run_queue) > 1:
                plt.plot(t[:len(run_queue[0])], [int(x) for x in run_queue[0]], 
                        label=f'Running Queue (r) - {file1_label}', color='#8e44ad', linewidth=2)
            if len(blocked_processes) > 1:
                plt.plot(t[:len(blocked_processes[0])], [int(x) for x in blocked_processes[0]], 
                        label=f'Blocked Processes (b) - {file1_label}', color='#d2b4de', linewidth=2)
            if len(run_queue) > 2:
                plt.plot(t[:len(run_queue[1])], [int(x) for x in run_queue[1]], 
                        label=f'Running Queue (r) - {file2_label}', color='#2980b9', linestyle='--', linewidth=2)
            if len(blocked_processes) > 2:
                plt.plot(t[:len(blocked_processes[1])], [int(x) for x in blocked_processes[1]], 
                        label=f'Blocked Processes (b) - {file2_label}', color='#aed6f1', linestyle='--', linewidth=2)
            plt.title('System Load - Comparison')
            plt.xlabel('Relative Time (seconds)')

        plt.ylabel('Processes')
        plt.legend(loc='best', fontsize=8)
        plt.tight_layout()
        ax = plt.gca()
        self.force_numeric(ax)
        plt.xticks(rotation=45)
        
        if comparison:
            plt = self._set_figtext_comparison(plt, tstart)
        else:
            if t:
                plt = self._set_figtext(plt, tstart)
        # Set y-axis lower limit to 0 for better fit
        ax.set_ylim(bottom=0)
        # Use different filename for comparison mode
        suffix = 'comparison' if comparison else 'system_load'
        if comparison:
            plt.savefig(f'{output_file_prefix}_system_load_comparison_{now_unix}.{output_format}', bbox_inches='tight')
        else:
            plt.savefig(f'{output_file_prefix}_system_load_{now_unix}.{output_format}', bbox_inches='tight')
        plt.close()

    def _plot_memory(self, inactive_memory_kb, active_memory_kb, swapped_memory_kb, free_memory_kb,
                    t, tstart, output_file_prefix, output_format, now_unix, comparison=False, filenames=None):
        import matplotlib.pyplot as plt
        plt.figure(figsize=self.figure_size)

        if not comparison:
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
            all_memory = inactive_memory_kb_int + active_memory_kb_int + swapped_memory_kb_int + free_memory_kb_int
        else:
            # Get filenames for labels
            file1_label = filenames[0] if filenames else 'File 1'
            file2_label = filenames[1] if filenames else 'File 2'
            all_memory = []
            if len(inactive_memory_kb) > 0:
                plt.plot(t[:len(inactive_memory_kb[0])], [int(x) for x in inactive_memory_kb[0]], 
                        label=f'Inactive Memory (KB) - {file1_label}', color='#e74c3c', linewidth=2)
            if len(active_memory_kb) > 0:
                plt.plot(t[:len(active_memory_kb[0])], [int(x) for x in active_memory_kb[0]], 
                         label=f'Active Memory (KB) - {file1_label}', color='#3498db', linewidth=2)
            if len(swapped_memory_kb) > 0:
                plt.plot(t[:len(swapped_memory_kb[0])], [int(x) for x in swapped_memory_kb[0]], 
                         label=f'Swapped Memory (KB) - {file1_label}', color='#f39c12', linewidth=2)
            if len(free_memory_kb) > 0:
                plt.plot(t[:len(free_memory_kb[0])], [int(x) for x in free_memory_kb[0]], 
                     label=f'Free Memory (KB) - {file1_label}', color='#2ecc71', linewidth=2)
            # File 2: lighter colors with dashed lines
            if len(inactive_memory_kb) > 1:
                plt.plot(t[:len(inactive_memory_kb[1])], [int(x) for x in inactive_memory_kb[1]], 
                         label=f'Inactive Memory (KB) - {file2_label}', color='#ec7063', linestyle='--', linewidth=2)
                all_memory += [int(x) for x in inactive_memory_kb[0]] + [int(x) for x in inactive_memory_kb[1]]
            if len(active_memory_kb) > 1:
                plt.plot(t[:len(active_memory_kb[1])], [int(x) for x in active_memory_kb[1]], 
                         label=f'Active Memory (KB) - {file2_label}', color='#5dade2', linestyle='--', linewidth=2)
                all_memory += [int(x) for x in active_memory_kb[0]] + [int(x) for x in active_memory_kb[1]]
            if len(swapped_memory_kb) > 1:
                plt.plot(t[:len(swapped_memory_kb[1])], [int(x) for x in swapped_memory_kb[1]], 
                         label=f'Swapped Memory (KB) - {file2_label}', color='#f8c471', linestyle='--', linewidth=2)
                all_memory += [int(x) for x in swapped_memory_kb[0]] + [int(x) for x in swapped_memory_kb[1]]
            if len(free_memory_kb) > 1:
                plt.plot(t[:len(free_memory_kb[1])], [int(x) for x in free_memory_kb[1]], 
                         label=f'Free Memory (KB) - {file2_label}', color='#58d68d', linestyle='--', linewidth=2)
                all_memory += [int(x) for x in free_memory_kb[0]] + [int(x) for x in free_memory_kb[1]]
            plt.title('Memory Usage - Comparison')
            plt.xlabel('Relative Time (seconds)')
        plt.ylabel('Memory (KB)')
        plt.legend(loc='best', fontsize=8 if comparison else 10)
        plt.tight_layout()
        ax = plt.gca()
        self.force_numeric(ax)
        plt.xticks(rotation=45)

        if comparison:
            plt = self._set_figtext_comparison(plt, tstart)
        else:
            if t:
                plt = self._set_figtext(plt, tstart)

        # Set y-axis limit a bit higher than the max value for better display
        if all_memory:
            ymax = max(all_memory) * 1.05
            ax.set_ylim(top=ymax)
        ax.set_ylim(bottom=0)

        if comparison:
            plt.savefig(f'{output_file_prefix}_memory_comparison_{now_unix}.{output_format}', bbox_inches='tight')
        else:
            plt.savefig(f'{output_file_prefix}_memory_{now_unix}.{output_format}', bbox_inches='tight')
        plt.close()

    def _plot_cpu(self, user_cpu_percent, system_cpu_percent,
                 idle_cpu_percent, wait_cpu_percent,
                 steal_cpu_percent, t, tstart,
                 output_file_prefix, output_format, now_unix, comparison=False, filenames=None):
        import matplotlib.pyplot as plt
        plt.figure(figsize=self.figure_size)

        if not comparison:
            plt.plot(t, [int(x) for x in user_cpu_percent], label='User CPU (%)')
            plt.plot(t, [int(x) for x in system_cpu_percent], label='System CPU (%)')
            plt.plot(t, [int(x) for x in idle_cpu_percent], label='Idle CPU (%)')
            plt.plot(t, [int(x) for x in wait_cpu_percent], label='Wait CPU (%)')
            plt.plot(t, [int(x) for x in steal_cpu_percent], label='Steal CPU (%)')
            plt.title('CPU Usage (%)')
            plt.xlabel('Seconds')
        else:
            # Get filenames for labels
            file1_label = filenames[0] if filenames else 'File 1'
            file2_label = filenames[1] if filenames else 'File 2'
            if len(user_cpu_percent) > 0:
                plt.plot(t[:len(user_cpu_percent[0])], [int(x) for x in user_cpu_percent[0]], 
                        label=f'User CPU (%) - {file1_label}', color='#e74c3c', linewidth=2)
            if len(system_cpu_percent) > 0:
                plt.plot(t[:len(system_cpu_percent[0])], [int(x) for x in system_cpu_percent[0]], 
                         label=f'System CPU (%) - {file1_label}', color='#3498db', linewidth=2)
            if len(idle_cpu_percent) > 0:
                plt.plot(t[:len(idle_cpu_percent[0])], [int(x) for x in idle_cpu_percent[0]], 
                         label=f'Idle CPU (%) - {file1_label}', color='#2ecc71', linewidth=2)
            if len(wait_cpu_percent) > 0:
                plt.plot(t[:len(wait_cpu_percent[0])], [int(x) for x in wait_cpu_percent[0]], 
                     label=f'Wait CPU (%) - {file1_label}', color='#f39c12', linewidth=2)
            if len(steal_cpu_percent) > 0:
                plt.plot(t[:len(steal_cpu_percent[0])], [int(x) for x in steal_cpu_percent[0]], 
                        label=f'Steal CPU (%) - {file1_label}', color='#9b59b6', linewidth=2)
            if len(user_cpu_percent) > 1:
                plt.plot(t[:len(user_cpu_percent[1])], [int(x) for x in user_cpu_percent[1]], 
                        label=f'User CPU (%) - {file2_label}', color='#ec7063', linestyle='--', linewidth=2)
            if len(system_cpu_percent) > 1:
                plt.plot(t[:len(system_cpu_percent[1])], [int(x) for x in system_cpu_percent[1]], 
                         label=f'System CPU (%) - {file2_label}', color='#5dade2', linestyle='--', linewidth=2)
            if len(idle_cpu_percent) > 1:
                plt.plot(t[:len(idle_cpu_percent[1])], [int(x) for x in idle_cpu_percent[1]], 
                         label=f'Idle CPU (%) - {file2_label}', color='#58d68d', linestyle='--', linewidth=2)
            if len(wait_cpu_percent) > 1:
                plt.plot(t[:len(wait_cpu_percent[1])], [int(x) for x in wait_cpu_percent[1]], 
                     label=f'Wait CPU (%) - {file2_label}', color='#f8c471', linestyle='--', linewidth=2)
            if len(steal_cpu_percent) > 1:
                plt.plot(t[:len(steal_cpu_percent[1])], [int(x) for x in steal_cpu_percent[1]], 
                     label=f'Steal CPU (%) - {file2_label}', color='#bb8fce', linestyle='--', linewidth=2)
            plt.title('CPU Usage (%) - Comparison')
            plt.xlabel('Relative Time (seconds)')
        plt.ylabel('Percent')
        plt.legend(loc='best', fontsize=8 if comparison else 10)
        plt.tight_layout()
        ax = plt.gca()
        self.force_numeric(ax)
        plt.xticks(rotation=45)
        if comparison:
            plt = self._set_figtext_comparison(plt, tstart)
        else:
            if t:
                plt = self._set_figtext(plt, tstart)
        ax.set_ylim(bottom=0)
        if comparison:
            plt.savefig(f'{output_file_prefix}_cpu_comparison_{now_unix}.{output_format}', bbox_inches='tight')
        else:
            plt.savefig(f'{output_file_prefix}_cpu_{now_unix}.{output_format}', bbox_inches='tight')
        plt.close()

    def _plot_swap(self, swapped_memory_kb, swap_in_kb,
                  swap_out_kb, t, tstart,
                  output_file_prefix, output_format, now_unix, comparison=False, filenames=None):
        import matplotlib.pyplot as plt
        plt.figure(figsize=self.figure_size)

        if not comparison:
            plt.plot(t, [int(x) for x in swapped_memory_kb], label='Swapped Memory (KB)')
            plt.plot(t, [int(x) for x in swap_in_kb], label='Swap In (KB)')
            plt.plot(t, [int(x) for x in swap_out_kb], label='Swap Out (KB)')
            plt.title('Swap Usage')
            plt.xlabel('Seconds')
        else:
            # Get filenames for labels
            file1_label = filenames[0] if filenames else 'File 1'
            file2_label = filenames[1] if filenames else 'File 2'
            if len(swapped_memory_kb) > 0:
                plt.plot(t[:len(swapped_memory_kb[0])], [int(x) for x in swapped_memory_kb[0]], 
                        label=f'Swapped Memory (KB) - {file1_label}', color='#e74c3c', linewidth=2)
            if len(swap_in_kb) > 0:
                plt.plot(t[:len(swap_in_kb[0])], [int(x) for x in swap_in_kb[0]], 
                         label=f'Swap In (KB) - {file1_label}', color='#3498db', linewidth=2)
            if len(swap_out_kb) > 0:
                plt.plot(t[:len(swap_out_kb[0])], [int(x) for x in swap_out_kb[0]], 
                         label=f'Swap Out (KB) - {file1_label}', color='#f39c12', linewidth=2)
            if len(swapped_memory_kb) > 1:
                plt.plot(t[:len(swapped_memory_kb[1])], [int(x) for x in swapped_memory_kb[1]], 
                         label=f'Swapped Memory (KB) - {file2_label}', color='#ec7063', linestyle='--', linewidth=2)
            if len(swap_in_kb) > 1:
                plt.plot(t[:len(swap_in_kb[1])], [int(x) for x in swap_in_kb[1]], 
                         label=f'Swap In (KB) - {file2_label}', color='#5dade2', linestyle='--', linewidth=2)
            if len(swap_out_kb) > 1:
                plt.plot(t[:len(swap_out_kb[1])], [int(x) for x in swap_out_kb[1]], 
                     label=f'Swap Out (KB) - {file2_label}', color='#f8c471', linestyle='--', linewidth=2)
            plt.title('Swap Usage - Comparison')
            plt.xlabel('Relative Time (seconds)')
        plt.ylabel('Swap (KB)')
        plt.legend(loc='best', fontsize=8 if comparison else 10)
        plt.tight_layout()
        ax = plt.gca()
        self.force_numeric(ax)
        plt.xticks(rotation=45)
        if comparison:
            plt = self._set_figtext_comparison(plt, tstart)
        else:
            if t:
                plt = self._set_figtext(plt, tstart)
        ax.set_ylim(bottom=0)
        if comparison:
            plt.savefig(f'{output_file_prefix}_swap_comparison_{now_unix}.{output_format}', bbox_inches='tight')
        else:
            plt.savefig(f'{output_file_prefix}_swap_{now_unix}.{output_format}', bbox_inches='tight')
        plt.close()

    def _plot_io(self, blocks_in, blocks_out, t, tstart, output_file_prefix, output_format, now_unix, comparison=False, filenames=None):
        import matplotlib.pyplot as plt
        plt.figure(figsize=self.figure_size)
        if not comparison:
            plt.plot(t, [int(x) for x in blocks_in], label='Blocks In')
            plt.plot(t, [int(x) for x in blocks_out], label='Blocks Out')
            plt.title('IO')
            plt.xlabel('Seconds')
        else:
            # Get filenames for labels
            file1_label = filenames[0] if filenames else 'File 1'
            file2_label = filenames[1] if filenames else 'File 2'
            if len(blocks_in) > 0:
                plt.plot(t[:len(blocks_in[0])], [int(x) for x in blocks_in[0]], 
                        label=f'Blocks In - {file1_label}', color='#3498db', linewidth=2)
            if len(blocks_out) > 0:
                plt.plot(t[:len(blocks_out[0])], [int(x) for x in blocks_out[0]], 
                         label=f'Blocks Out - {file1_label}', color='#e74c3c', linewidth=2)
            if len(blocks_in) > 1:
                plt.plot(t[:len(blocks_in[1])], [int(x) for x in blocks_in[1]], 
                     label=f'Blocks In - {file2_label}', color='#5dade2', linestyle='--', linewidth=2)
            if len(blocks_out) > 1:
                plt.plot(t[:len(blocks_out[1])], [int(x) for x in blocks_out[1]], 
                        label=f'Blocks Out - {file2_label}', color='#ec7063', linestyle='--', linewidth=2)
            plt.title('IO - Comparison')
            plt.xlabel('Relative Time (seconds)')
        plt.ylabel('Blocks')
        plt.legend(loc='best', fontsize=8 if comparison else 10)
        plt.tight_layout()
        ax = plt.gca()
        self.force_numeric(ax)
        plt.xticks(rotation=45)
        if comparison:
            plt = self._set_figtext_comparison(plt, tstart)
        else:
            if t:
                plt = self._set_figtext(plt, tstart)
        ax.set_ylim(bottom=0)
        if comparison:
            plt.savefig(f'{output_file_prefix}_io_comparison_{now_unix}.{output_format}', bbox_inches='tight')
        else:
            plt.savefig(f'{output_file_prefix}_io_{now_unix}.{output_format}', bbox_inches='tight')
        plt.close()

    def _set_figtext(self, plt, tstart):
        plt.figtext(0.99, 0.01, f"Start time: {tstart}", horizontalalignment='right', fontsize=8, color='gray')
        plt.figtext(0.99, 0.99, f"File: {self.filename}", horizontalalignment='right', fontsize=8, color='gray')
        return plt

    def _set_figtext_comparison(self, plt, tstart):
        if isinstance(tstart, list) and len(tstart) == 2:
            plt.figtext(0.99, 0.01, f"Start times - File 1: {tstart[0]} | File 2: {tstart[1]}", 
                       horizontalalignment='right', fontsize=7, color='gray')
        else:
            plt.figtext(0.99, 0.01, f"Start time: {tstart}", 
                       horizontalalignment='right', fontsize=8, color='gray')
        return plt

    class PlotMetrics:
        def __init__(self, timeseries, relative_time=False):
            self.t = []
            self.run_queue = []
            self.blocked_processes = []
            self.free_memory_kb = []
            self.inactive_memory_kb = []
            self.active_memory_kb = []
            self.swapped_memory_kb = []
            self.user_cpu_percent = []
            self.system_cpu_percent = []
            self.idle_cpu_percent = []
            self.wait_cpu_percent = []
            self.steal_cpu_percent = []
            self.guest_cpu_percent = []
            self.swap_in_kb = []
            self.swap_out_kb = []
            self.blocks_in = []
            self.blocks_out = []
            self._counter = self._counter_gen()
            for ts_entry in timeseries:
                t_dt = datetime.datetime.strptime(ts_entry.time, '%Y-%m-%d %H:%M:%S')
                if not relative_time:
                    self.t.append(t_dt.strftime('%M:%S'))
                else: 
                    self.t.append(next(self._counter))
                self.run_queue.append(ts_entry.run_queue)
                self.blocked_processes.append(ts_entry.blocked_processes)
                self.free_memory_kb.append(ts_entry.free_memory_kb)
                self.inactive_memory_kb.append(ts_entry.inactive_memory_kb)
                self.active_memory_kb.append(ts_entry.active_memory_kb)
                self.swapped_memory_kb.append(ts_entry.swapped_memory_kb)
                self.user_cpu_percent.append(ts_entry.user_cpu_percent)
                self.system_cpu_percent.append(ts_entry.system_cpu_percent)
                self.idle_cpu_percent.append(ts_entry.idle_cpu_percent)
                self.wait_cpu_percent.append(ts_entry.wait_cpu_percent)
                self.steal_cpu_percent.append(ts_entry.steal_cpu_percent)
                self.guest_cpu_percent.append(ts_entry.guest_cpu_percent)
                self.swap_in_kb.append(ts_entry.swap_in_kb)
                self.swap_out_kb.append(ts_entry.swap_out_kb)
                self.blocks_in.append(ts_entry.blocks_in)
                self.blocks_out.append(ts_entry.blocks_out)

        @staticmethod
        def _counter_gen():
            n = 0
            while True:
                yield n
                n += 1
