"""CLI command for multi-file comparison."""

import click
from vmstat_visualizer.parser.parser import Parser
from vmstat_visualizer.multi_compare import plot_multi_compare


@click.command("compare-multi", no_args_is_help=True)
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    "-m",
    "--metric",
    type=click.Choice(["cpu", "memory", "system_load", "swap", "io", "all"],
                       case_sensitive=False),
    required=True,
    help="Metric to compare.",
)
@click.option(
    "-o",
    "--output-prefix",
    default="vmstat",
    help="Output filename prefix.",
)
@click.option(
    "-e",
    "--output-extension",
    default="png",
    help="Output format: png or svg.",
)
def compare_multi(files, metric, output_prefix, output_extension):
    """Compare N vmstat log files on a given metric.

    Pass two or more log files as arguments.
    """
    if len(files) < 2:
        raise click.UsageError("At least 2 files are required for comparison.")

    parsers = []
    for f in files:
        p = Parser(f)
        p.parse()
        print(f">>> Parsed {len(p.timeseries)} entries from {f}")
        parsers.append(p)

    plot_multi_compare(
        parsers, metric,
        output_file_prefix=output_prefix,
        output_format=output_extension,
    )
