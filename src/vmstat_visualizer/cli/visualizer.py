"""
visualizer module implements the commands for visualizing
vmstat output files.
"""
import click
from vmstat_visualizer.parser.parser import Parser

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
def visualize(
    file, output_prefix, output_extension
):
    """
    Visualize a file or files in a directory
    """
    print(f">>> Visualizing file: {file}")
    parser = Parser(file)
    parser.parse()
    print(f">>> Parsed {len(parser.timeseries)} time series entries.")
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
    type=click.Choice(["cpu", "memory"], case_sensitive=False),
    required=True,
    help="Metric to compare: 'cpu' or 'memory'."
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
def compare(file1, file2, metric, output_prefix, output_extension):
    """
    Compare two vmstat log files based on a given metric (cpu or memory).
    """
    print(f">>> Comparing {file1} and {file2} on metric: {metric}")
    parser1 = Parser(file1)
    parser2 = Parser(file2)
    parser1.parse()
    print(f">>> Parsed {len(parser1.timeseries)} time series entries from {file1}.")
    parser2.parse()
    print(f">>> Parsed {len(parser2.timeseries)} time series entries from {file2}.")
    parser1.plot_comparison(
        parser1.timeseries, parser2.timeseries,
        output_file_prefix=output_prefix,
        output_format=output_extension,
        metric=metric
    )
