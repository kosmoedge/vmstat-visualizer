"""
visualizer module implements the commands for visualizing
vmstat output files.
"""
import click
from vmstat_visualizer.parser.parser import Parser

@click.command("visualize", no_args_is_help=True)
@click.argument("file", default="./vmstat.log", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output-dir",
    default="./",
    help="set the output directory for converted files.",
)
@click.option(
    "-k",
    "--output-kinds",
    default="png",
    help="set the output kind for conversion.",
)
def visualize(
    file, output_dir, output_kinds
):
    """
    Visualize a file or files in a directory
    """
    print(f">>> Visualizing file: {file}")
    parser = Parser(file)
    parser.parse()
    print(f">>> Parsed {len(parser.timeseries)} time series entries.")
    
    # Here you would add code to generate visualizations from parser.timeseries
