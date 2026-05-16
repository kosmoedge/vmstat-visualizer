"""
visualizer module implements the commands for visualizing
vmstat output files.
"""
import click
from vmstat_visualizer.parser.parser import Parser
from vmstat_visualizer.summary import compute_summary, format_summary_text, format_summary_json

@click.command("visualize", no_args_is_help=True)
@click.argument("file", default="vmstat.log", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output-prefix",
    default="vmstat",
    help="set the output prefix for created files.",
)
@click.option(
    "-e",
    "--output-extension",
    default="png",
    help="set the output extension for created files.",
)
@click.option(
    "--summary",
    is_flag=True,
    default=False,
    help="Print summary statistics (min/max/mean/p95/p99) to stdout.",
)
@click.option(
    "--summary-json",
    is_flag=True,
    default=False,
    help="Print summary statistics as JSON to stdout.",
)
def visualize(
    file, output_prefix, output_extension, summary, summary_json
):
    """
    Visualize a file or files in a directory
    """
    print(f">>> Visualizing file: {file}")
    parser = Parser(file)
    parser.parse()
    print(f">>> Parsed {len(parser.timeseries)} time series entries.")

    if summary or summary_json:
        plot_metrics = parser.PlotMetrics(parser.timeseries)
        stats = compute_summary(plot_metrics)
        if summary_json:
            print(format_summary_json(stats))
        else:
            print(format_summary_text(stats))

    if not summary_json:
        parser.plot(
            output_file_prefix=f"{output_prefix}",
            output_format=output_extension
        )


@click.command("compare", no_args_is_help=True)
@click.argument("file1", type=click.Path(exists=True))
@click.argument("file2", type=click.Path(exists=True))
@click.option(
    "-m",
    "--metric",
    type=click.Choice(["cpu", "memory", "system_load", "swap", "io", "all"], case_sensitive=False),
    required=True,
    help="Metric to compare: 'cpu', 'memory', 'system_load', 'swap', 'io', or 'all'."
)
@click.option(
    "-o",
    "--output-prefix",
    default="vmstat",
    help="set the output prefix for created files.",
)
@click.option(
    "-e",
    "--output-extension",
    default="png",
    help="set the output extension for created files.",
)
@click.option(
    "-c",
    "--column",
    type=click.Choice(["r", "b", "swpd",
                       "free", "si", "so",
                       "us", "sy",
                       "id", "wa", "st",
                       "inact", "active",
                       "buff", "cache"], case_sensitive=False),
    multiple=True,
    help="""Specific column(s) to visualize. Can be specified multiple times. For each metric, the relevant columns are:\n
    - cpu: us, sy, id, wa, st\n
    - memory: swpd, free, inact, active (vmstat -a) or buff, cache (standard vmstat)\n
    - system_load: r, b, si, so\n
    Example: -c us -c sy -c id
    """
)
def compare(file1, file2, metric, output_prefix,
            output_extension, column):
    """
    Compare two vmstat log files based on a given metric (cpu or memory).
    """
    # Convert tuple to list (click returns tuple with multiple=True)
    column = list(column) if column else []
    if column:
        print(f">>> Filtering columns: {', '.join(column)}")
    print(f">>> Comparing {file1} and {file2} on metric: {metric}")
    parser1 = Parser(file1)
    parser1.enabled_columns = column
    parser2 = Parser(file2)
    parser2.enabled_columns = column
    parser1.parse()
    print(f">>> Parsed {len(parser1.timeseries)} time series entries from {file1}.")
    parser2.parse()
    print(f">>> Parsed {len(parser2.timeseries)} time series entries from {file2}.")
    parser1.plot_comparison(
        compare_parser=parser2,
        output_file_prefix=output_prefix,
        output_format=output_extension,
        metric=metric,
        column=column
    )
