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
    # Here you would add code to generate visualizations from parser.timeseries
