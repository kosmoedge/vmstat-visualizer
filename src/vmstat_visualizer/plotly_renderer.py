"""Interactive HTML chart rendering using Plotly.

Requires: pip install plotly
(or: pip install vmstat-visualizer[interactive])
"""

import datetime
import time


def _check_plotly():
    try:
        import plotly  # noqa: F401
        return True
    except ImportError:
        return False


def render_html(parser, output_file_prefix='vmstat'):
    """Render all metric charts as a single interactive HTML file."""
    if not _check_plotly():
        raise ImportError(
            "Plotly is required for HTML output. "
            "Install it with: pip install plotly"
        )

    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    plot_metrics = parser.PlotMetrics(parser.timeseries)
    t = plot_metrics.t

    fig = make_subplots(
        rows=5, cols=1,
        subplot_titles=("CPU Usage (%)", "Memory Usage (KB)",
                        "System Load", "Swap Usage (KB)", "Block I/O"),
        vertical_spacing=0.06,
        shared_xaxes=True,
    )

    # CPU
    cpu_series = [
        ("User", plot_metrics.user_cpu_percent),
        ("System", plot_metrics.system_cpu_percent),
        ("Idle", plot_metrics.idle_cpu_percent),
        ("Wait", plot_metrics.wait_cpu_percent),
        ("Steal", plot_metrics.steal_cpu_percent),
    ]
    for name, data in cpu_series:
        if any(v is not None for v in data):
            fig.add_trace(go.Scatter(
                x=t, y=[int(v) for v in data if v is not None],
                mode='lines', name=f'CPU {name}',
                legendgroup='cpu',
            ), row=1, col=1)

    # Memory
    mem_series = [
        ("Free", plot_metrics.free_memory_kb),
        ("Inactive", plot_metrics.inactive_memory_kb),
        ("Active", plot_metrics.active_memory_kb),
        ("Swapped", plot_metrics.swapped_memory_kb),
    ]
    for name, data in mem_series:
        if any(v is not None for v in data):
            fig.add_trace(go.Scatter(
                x=t, y=[int(v) for v in data if v is not None],
                mode='lines', name=f'Mem {name}',
                legendgroup='memory',
            ), row=2, col=1)

    # System Load
    load_series = [
        ("Run Queue", plot_metrics.run_queue),
        ("Blocked", plot_metrics.blocked_processes),
    ]
    for name, data in load_series:
        if any(v is not None for v in data):
            fig.add_trace(go.Scatter(
                x=t, y=[int(v) for v in data if v is not None],
                mode='lines', name=name,
                legendgroup='load',
            ), row=3, col=1)

    # Swap
    swap_series = [
        ("Swap In", plot_metrics.swap_in_kb),
        ("Swap Out", plot_metrics.swap_out_kb),
    ]
    for name, data in swap_series:
        if any(v is not None for v in data):
            fig.add_trace(go.Scatter(
                x=t, y=[int(v) for v in data if v is not None],
                mode='lines', name=name,
                legendgroup='swap',
            ), row=4, col=1)

    # IO
    io_series = [
        ("Blocks In", plot_metrics.blocks_in),
        ("Blocks Out", plot_metrics.blocks_out),
    ]
    for name, data in io_series:
        if any(v is not None for v in data):
            fig.add_trace(go.Scatter(
                x=t, y=[int(v) for v in data if v is not None],
                mode='lines', name=name,
                legendgroup='io',
            ), row=5, col=1)

    tstart = parser.timeseries[0].time if parser.timeseries else 'N/A'
    now_unix = int(time.mktime(
        datetime.datetime.now().replace(second=0, microsecond=0).timetuple()
    ))

    fig.update_layout(
        height=1200,
        title_text=f"vmstat — {parser.filename} (start: {tstart})",
        showlegend=True,
        hovermode='x unified',
    )

    filename = f"{output_file_prefix}_{now_unix}.html"
    fig.write_html(filename)
    print(f">>> Interactive HTML saved to {filename}")
    return filename
