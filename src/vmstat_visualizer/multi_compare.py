"""Multi-file comparison plotting for N vmstat log files."""

import datetime
import os
import time
import matplotlib.pyplot as plt


LINE_STYLES = ['-', '--', '-.', ':', (0, (3, 1, 1, 1))]
COLORS = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6',
          '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b']


def _style_for(idx):
    """Return (color, linestyle) for file index."""
    color = COLORS[idx % len(COLORS)]
    style = LINE_STYLES[idx % len(LINE_STYLES)]
    return color, style


def plot_multi_compare(parsers, metric, output_file_prefix='vmstat',
                       output_format='png'):
    """Compare N parsed files on a given metric.

    Args:
        parsers: list of Parser instances (already parsed)
        metric: one of 'cpu', 'memory', 'system_load', 'swap', 'io', 'all'
        output_file_prefix: filename prefix
        output_format: 'png' or 'svg'
    """
    if metric == 'all':
        for m in ['cpu', 'memory', 'system_load', 'swap', 'io']:
            plot_multi_compare(parsers, m, output_file_prefix, output_format)
        return

    from vmstat_visualizer.parser.parser import Parser

    all_metrics = []
    filenames = []
    for p in parsers:
        pm = Parser.PlotMetrics(p.timeseries, relative_time=True)
        all_metrics.append(pm)
        filenames.append(os.path.basename(p.filename))

    max_len = max(len(pm.t) for pm in all_metrics)
    t = list(range(max_len))

    now_unix = int(time.mktime(
        datetime.datetime.now().replace(second=0, microsecond=0).timetuple()
    ))

    metric_configs = {
        'cpu': {
            'title': 'CPU Usage (%) - Multi Comparison',
            'ylabel': 'Percent',
            'series': [
                ('User CPU', 'user_cpu_percent'),
                ('System CPU', 'system_cpu_percent'),
                ('Idle CPU', 'idle_cpu_percent'),
                ('Wait CPU', 'wait_cpu_percent'),
                ('Steal CPU', 'steal_cpu_percent'),
            ]
        },
        'memory': {
            'title': 'Memory Usage (KB) - Multi Comparison',
            'ylabel': 'Memory (KB)',
            'series': [
                ('Free', 'free_memory_kb'),
                ('Inactive', 'inactive_memory_kb'),
                ('Active', 'active_memory_kb'),
                ('Swapped', 'swapped_memory_kb'),
            ]
        },
        'system_load': {
            'title': 'System Load - Multi Comparison',
            'ylabel': 'Processes',
            'series': [
                ('Run Queue', 'run_queue'),
                ('Blocked', 'blocked_processes'),
            ]
        },
        'swap': {
            'title': 'Swap Usage - Multi Comparison',
            'ylabel': 'KB',
            'series': [
                ('Swap In', 'swap_in_kb'),
                ('Swap Out', 'swap_out_kb'),
                ('Swapped', 'swapped_memory_kb'),
            ]
        },
        'io': {
            'title': 'Block I/O - Multi Comparison',
            'ylabel': 'Blocks',
            'series': [
                ('Blocks In', 'blocks_in'),
                ('Blocks Out', 'blocks_out'),
            ]
        },
    }

    config = metric_configs[metric]
    fig, ax = plt.subplots(figsize=(12, 5))

    for file_idx, (pm, fname) in enumerate(zip(all_metrics, filenames)):
        color, style = _style_for(file_idx)
        for series_name, attr in config['series']:
            data = getattr(pm, attr, [])
            if not data or all(v is None for v in data):
                continue
            values = [int(v) for v in data]
            ax.plot(
                t[:len(values)], values,
                label=f'{series_name} ({fname})',
                color=color, linestyle=style, linewidth=1.5,
                alpha=0.8,
            )

    ax.set_title(config['title'])
    ax.set_xlabel('Relative Time (seconds)')
    ax.set_ylabel(config['ylabel'])
    ax.set_ylim(bottom=0)
    ax.legend(loc='best', fontsize=7, ncol=2)
    plt.tight_layout()

    starts = []
    for p in parsers:
        if p.timeseries:
            starts.append(f"{os.path.basename(p.filename)}: {p.timeseries[0].time}")
    start_text = " | ".join(starts)
    plt.figtext(0.99, 0.01, f"Start times: {start_text}",
                horizontalalignment='right', fontsize=6, color='gray')

    outfile = f'{output_file_prefix}_{metric}_multi_{now_unix}.{output_format}'
    plt.savefig(outfile, bbox_inches='tight')
    plt.close()
    print(f">>> Saved {outfile}")
